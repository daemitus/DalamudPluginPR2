from __future__ import annotations

import json
import logging
from pathlib import Path
from urllib.parse import urlparse

import sh  # noqa
import toml
from github import Github

from .config import ConfigModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("DalamudPluginPR2")
log.setLevel(logging.INFO)


def run_action() -> None:
    """Action entrypoint"""

    log.info("Loading config")
    config = ConfigModel()
    owner = config.repository.split("/")[0]  # name/repo -> name
    repo = config.repository
    pr_repo = config.pr_repository
    branch = config.plugin_name.replace(" ", "_")
    pr_branch = config.pr_branch
    token = config.token
    plugin_name = config.plugin_name

    log.info("Reading event data")
    event_data = json.loads(Path(config.gh_event_path).read_text())
    author_name: str = event_data["commits"][0]["author"]["name"]
    author_email: str = event_data["commits"][0]["author"]["email"]
    message: str = event_data["commits"][-1]["message"]

    log.info("Enabled flag: %s", config.enabled)
    if config.enabled == "true":
        log.info("Action enabled: explicit true")
        enabled = True
    elif config.enabled == "false":
        log.info("Action disabled: explicit false")
        enabled = False
    elif config.enabled in message:
        log.info("Action enabled: substring match")
        enabled = True
    else:
        log.info("Action disabled: substring failed")
        enabled = False

    # Bail if not enabled
    if not enabled:
        log.info("Exiting")
        return

    log.info("Testing flag: %s", config.testing)
    if config.testing == "true":
        log.info("Testing enabled: explicit true")
        testing = True
    elif config.testing == "false":
        log.info("Testing disabled: explicit false")
        testing = False
    elif config.testing in message:
        log.info("Testing enabled: substring match")
        testing = True
    else:
        log.info("Testing disabled: substring failed")
        testing = False

    log.info("Logging into GitHub")
    gh = Github(config.token)
    git = sh.git

    log.info("Configuring git user")
    git.config("--global", "user.name", author_name)
    git.config("--global", "user.email", author_email)

    log.info("Setting up %s", repo)
    git.clone(f"https://github.com/{repo}.git", "repo")
    git = sh.git.bake("-C", "repo")
    git.remote.add("pr_repo", f"https://github.com/{pr_repo}.git")
    git.fetch("--all")

    # Fixup the remote url so it can be pushed to
    remote = git.config("--get", "remote.origin.url")
    remote = urlparse(remote.strip())  # Insert the token next
    remote = f"{remote.scheme}://{token}@{remote.hostname}{remote.path}"
    git.config("remote.origin.url", remote)

    try:
        repo_branch_exists = git("show-ref", f"origin/{branch}")
    except sh.ErrorReturnCode_1:
        repo_branch_exists = False

    if repo_branch_exists:
        log.info("Branch %s already exists, resetting to %s", branch, pr_branch)
        git.checkout(branch)
        git.reset("--hard", f"pr_repo/{pr_branch}")
    else:
        log.info("Creating new branch %s", branch)
        git.reset("--hard", f"pr_repo/{pr_branch}")
        git.branch(branch)
        git.checkout(branch)
        git.push("--set-upstream", "origin", "--force", branch)

    env = "stable" if not testing else f"testing/{config.pr_testing_folder}"
    pr_title = f"Update {plugin_name} ({env})"
    if testing:
        pr_title = f"[Testing] {pr_title}"
    pr_body = "\n".join(message.splitlines()[2:])

    # Update the manifest where necessary
    manifest_path = Path(f"repo/{env}/{plugin_name}/manifest.toml")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    owners = config.plugin_owners.split(",")
    owners = [owner.strip() for owner in owners]
    owners = list(filter(None, owners))

    manifest = {
        "plugin": {
            "repository": f"{config.gh_server_url}/{config.gh_repository}.git",
            "owners": owners,
            "project_path": config.project_path,
            "commit": config.gh_commit_hash,
            "changelog": pr_body,
        }
    }

    manifest_path.write_text(toml.dumps(manifest))

    log.info("Adding and committing")
    git.add("--all")
    git.commit("--all", "-m", f"Update {plugin_name}")

    log.info("Pushing to origin")
    git.push("--force", "--set-upstream", "origin", branch)

    repo = gh.get_repo(pr_repo)
    pulls = repo.get_pulls()
    pulls = [pull for pull in pulls if pull.head.ref == branch]
    if pulls and (pull := pulls[0]):
        log.info("Editing existing PR")
        pull.edit(
            title=pr_title,
            body=pr_body,
            state="open",
        )
    else:
        log.info("Creating PR")
        repo.create_pull(
            title=pr_title,
            body=pr_body,
            base=pr_branch,
            head=f"{owner}:{branch}",
        )

    log.info("Done!")
