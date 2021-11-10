from utils.log import log, LogIndent
import os
from utils.os_helpers import Pushd
from utils import command
from pathlib import Path
from utils.log import log, LogIndent


class Step:
    def __init__(self, name):
        self.name = name

    def get_required_packages(self):
        pass

    def perform(self, *args, **kwargs):
        log(f"Performing step: {self.name}")

        with LogIndent():
            self._perform_impl(*args, **kwargs)

    def _perform_impl(self, *args, **kwargs):
        raise NotImplementedError()

    def _compile_remote_project(self, build_dir, url, revision, patches_dir, setup_repo):
        if setup_repo:
            log(f"Downloading {url} to {build_dir}")
            command.setup_git_repo(url, revision, build_dir)

        with Pushd(build_dir):
            diffs = list(Path(patches_dir).glob("*.diff"))
            log(f"Applying {len(diffs)} patches")
            with LogIndent():
                diffs.sort()
                for diff in diffs:
                    log(diff)
                    command.apply_patch(diff)

            log(f"Building and installing")
            command.run_command("sudo make install")
