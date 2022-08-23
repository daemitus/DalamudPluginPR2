from __future__ import annotations

from pydantic import BaseSettings, Field

__all__ = [
    "ConfigModel",
]


class ConfigModel(BaseSettings):
    """Configuration"""

    enabled: str = Field(
        description="Enable or disable the entire dalamud_plugin_pr2. This can be true/false or a partial string searched for within the commit message.",
        env="INPUT_ENABLED",
    )
    testing: str = Field(
        description="If the toml should be update in the testing folder instead of stable. This can be true/false or a partial string searched for within the commit message.",
        env="INPUT_TESTING",
    )
    repository: str = Field(
        description="Repository where your manifest PR will originate from.",
        env="INPUT_REPOSITORY",
    )
    pr_repository: str = Field(
        description="Repository where the PR will be created.",
        env="INPUT_PR_REPOSITORY",
    )
    pr_branch: str = Field(
        description="Branch to merge your PR into.",
        env="INPUT_PR_BRANCH",
    )
    pr_testing_folder: str = Field(
        description="The folder to merge testing plugins into.",
        env="INPUT_PR_TESTING_FOLDER",
    )
    token: str = Field(
        description="Personal access token to authenticate with GitHub.",
        env="INPUT_TOKEN",
    )
    plugin_name: str = Field(
        description="Name of your plugin in the manifest.toml path.",
        env="INPUT_PLUGIN_NAME",
    )
    plugin_owners: str = Field(
        description="Comma delimited author names, responsible for plugin development.",
        env="INPUT_PLUGIN_OWNERS",
    )
    project_path: str = Field(
        description="The directory path your csproj resides in.",
        env="INPUT_PROJECT_PATH",
    )
    gh_workspace: str = Field(
        description="The default working directory on the runner for steps, and the default location of your repository when using the checkout dalamud_plugin_pr2.",
        env="GITHUB_WORKSPACE",
    )
    gh_event_path: str = Field(
        description="The path to the file on the runner that contains the full event webhook payload.",
        env="GITHUB_EVENT_PATH",
    )
    gh_commit_hash: str = Field(
        description="The commit SHA that triggered the workflow.",
        env="GITHUB_SHA",
    )
    gh_server_url: str = Field(
        description="The commit SHA that triggered the workflow.",
        env="GITHUB_SERVER_URL",
    )
    gh_repository: str = Field(
        description="The commit SHA that triggered the workflow.",
        env="GITHUB_REPOSITORY",
    )
