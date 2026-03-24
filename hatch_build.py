import subprocess
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        result = subprocess.run(
            ["ruff", "format", "--check", "src/", "tests/"],
            cwd=self.root,
        )
        if result.returncode != 0:
            sys.exit("Build failed: code is not formatted. Run 'ruff format src/ tests/' to fix.")
