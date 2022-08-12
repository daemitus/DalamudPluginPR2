# DalamudPluginPR2

This action checks-out your fork of `goatcorp/DalamudPluginsD17` and updates the plugin manifest.toml with the commit hash that triggered the action.

The PR branch is the name of your plugin, as contained in the manifest "Name" field. If you would like to PR to testing, make sure to either enable the testing field or add the required string to your commit message.

For the PR itself, the title is the plugin name combined with the assembly version from the manifest. The body is the body of the last commit.

# Usage
```yaml
jobs:
  pull_request:
    runs-on: ubuntu-latest
    steps:
    - name: Create pull request
      uses: daemitus/DalamudPluginPR2@master
      with:
        # ===== Required inputs =====
        # Personal access token to authenticate with GitHub.
        # Your access token should be stored in a repository secret
        token: ${{ secrets.PAT }}

        # The name of your plugin, used in determining the manifest path.
        plugin_name: TestPlugin

        # ===== Optional inputs =====
        # Enable or disable the entire dalamud_plugin_pr2.
        # This can be true/false or a partial string searched for within the commit message.
        # Default: "[PR]"
        # enabled:

        # If the artifact should be commited to testing instead of plugins.
        # This can be true/false or a partial string searched for within the commit message.
        # Default: "[TEST]"
        # testing:

        # Repository where your artifact will be committed.
        # Default: ${{ github.repository_owner }}/DalamudPlugins
        # repository:

        # Repository where the PR will be created.
        # Default: goatcorp/DalamudPlugins
        # pr_repository:
```
