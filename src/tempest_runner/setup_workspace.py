import os
from pathlib import Path

from tempest.cmd.init import TempestInit, get_tempest_default_config_dir
from tempest.cmd.workspace import WorkspaceManager


class TempestManager:
    base_path: str

    def __init__(
        self,
        workspaces_config_path: str,
        base_path: str,
    ) -> None:
        """
        Takes arguments:
        workspaces_config_path: path to workspaces.yaml file, which defines location of each workspace for tempest.
        workspace_config_src: path to directory containing a tempest.conf and other files, will be copied into workspace.
        base_path: directory which will hold each managed workspace as a subdir

        """

        self.base_path = base_path

        # get a workspace manager using the workspaces_yaml file
        self.workspace_manager = WorkspaceManager(workspaces_config_path)

        # instance of tempest workspace initializer, we'll call some methods on this to populate the new workspace
        self.workspace_initializer = TempestInit(app=None, app_args=None, cmd_name=None)

    def _update_accts_yaml(self, local_dir):
        local_dir_path = Path(local_dir)
        etc_dir = local_dir_path.joinpath("etc")
        config_path = os.path.join(etc_dir, "tempest.conf")
        accounts_yaml = os.path.join(etc_dir, "accounts.yaml")

        config_parse = self.workspace_initializer.get_configparser(config_path)

        # Set test_accounts_file in tempest conf
        config_parse.set("auth", "test_accounts_file", accounts_yaml)

        # write out a new file with the updated configurations
        with open(config_path, "w+") as conf_file:
            config_parse.write(conf_file)

    def init_and_register_workspace(
        self, workspace_name, workspace_src_config: str | None = None
    ):
        # get path for workspace to live in
        workspace_local_dir = os.path.join(self.base_path, workspace_name)

        # ensure that directory exists
        Path(workspace_local_dir).mkdir(exist_ok=True)

        # initalize the new workspace, optionally with with a source config
        config_dir = workspace_src_config or get_tempest_default_config_dir()
        self.workspace_initializer.create_working_dir(
            local_dir=workspace_local_dir, config_dir=config_dir
        )

        self._update_accts_yaml(workspace_local_dir)

        self.workspace_manager.register_new_workspace(
            name=workspace_name, path=workspace_local_dir
        )
