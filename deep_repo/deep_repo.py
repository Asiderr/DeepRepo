#!/usr/bin/env python3

import os
import sys

from deep_repo.analyzers.deep_issues import DeepIssues
from deep_repo.analyzers.deep_boomerangs import DeepBoomerangs
from deep_repo.analyzers.deep_issue_quality import DeepIssuesQuality
from deep_repo.analyzers.deep_resource_analysis import DeepResourceAnalysis
from deep_repo.analyzers.deep_code_quality import DeepCodeQuality
from deep_repo.deep_config import DeepRepoConfig

ANALYZERS = {
    "issues": DeepIssues,
    "boomerangs": DeepBoomerangs,
    "issue_quality": DeepIssuesQuality,
    "resource_analysis": DeepResourceAnalysis,
    "code_quality": DeepCodeQuality,
}


class DeepRepo(DeepRepoConfig):
    def __init__(self, envpath='.env'):
        parser = self.parse_cmdline()
        cmdline_input = parser.parse_args()
        self.repo_path = cmdline_input.repo_path
        self.all_modes = cmdline_input.all
        self.issue_mode = cmdline_input.issues
        self.boomerangs_mode = cmdline_input.boomerangs
        self.issue_quality_mode = cmdline_input.issue_quality
        self.resource_analysis_mode = cmdline_input.mmv1_resources
        self.code_quality_mode = cmdline_input.code_quality
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
        elif self.boomerangs_mode:
            self.log.info("Creating boomerangs analysis"
                          f" for issues {self.repo_path}.")
            analyzer = self.deep_repo_factory("boomerangs")
            analyzer.run()
            sys.exit(0)
        elif self.issue_quality_mode:
            self.log.info("Creating issue quality analysis"
                          f" for issues {self.repo_path}.")
            analyzer = self.deep_repo_factory("issue_quality")
            analyzer.run()
            sys.exit(0)
        elif self.resource_analysis_mode:
            repo_path = os.getenv("repo_path")
            self.log.info("Creating analysis of the compute resource types"
                          f"for {repo_path}.")
            analyzer = self.deep_repo_factory("resource_analysis")
            analyzer.run()
            sys.exit(0)
        elif self.code_quality_mode:
            repo_path = os.getenv("repo_path")
            self.log.info("Creating code quality analysis"
                          f" for {repo_path}.")
            analyzer = self.deep_repo_factory("code_quality")
            analyzer.run()
            sys.exit(0)
        else:
            self.log.error("Analyzer mode not set. Exiting...")
            sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    cls_deep_repo = DeepRepo()
    cls_deep_repo.deep_repo_main()
