#!/usr/bin/env python3

import sys

from deep_repo.analyzers.deep_issues import DeepIssues
from deep_repo.deep_config import DeepRepoConfig

ANALYZERS = {
    "issues": DeepIssues,
}


class DeepRepo(DeepRepoConfig):
    def __init__(self, envpath='.env'):
        parser = self.parse_cmdline()
        cmdline_input = parser.parse_args()
        self.repo_path = cmdline_input.repo_path
        self.all_modes = cmdline_input.all
        self.issue_mode = cmdline_input.issues
        self.setup_logger()
        try:
            self.load_env_vars(envpath=envpath)
        except (RuntimeError, FileNotFoundError) as e:
            self.log.error(f"Loading environmental variables failed: {e}")
            sys.exit(1)
        self.git_api = self.setup_git_api()

    def deep_repo_factory(self, analyzer_type):
        analyzer_class = ANALYZERS.get(analyzer_type)
        if not analyzer_class:
            raise ValueError(f"Analyzer type '{analyzer_type}'"
                             " is not recognized.")
        return analyzer_class(self.repo_path, self.log, self.git_api)

    def deep_repo_main(self):
        if self.all_modes:
            for analyzer_type in ANALYZERS.keys():
                self.log.info(f"Creating {analyzer_type} analysis for "
                              f"{self.repo_path}.")
                analyzer = self.deep_repo_factory(analyzer_type)
                analyzer.run()
            sys.exit(0)
        elif self.issue_mode:
            self.log.info("Creating issues analysis"
                          f" for issues {self.repo_path}.")
            analyzer = self.deep_repo_factory("issues")
            analyzer.run()
            sys.exit(0)
        else:
            self.log.error("Analyzer mode not set. Exiting...")
            sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    cls_deep_repo = DeepRepo()
    cls_deep_repo.deep_repo_main()
