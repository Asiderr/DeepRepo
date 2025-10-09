#!/usr/bin/env python3
import os
import re
import subprocess

from datetime import datetime
from deep_repo.deep_base import DeepRepoBase

RESOURCE_PATTERN = re.compile(r'^resource_compute_[a-z_]+\.go$')
TODO_PATTERN = re.compile(r'.*TODO.*', re.IGNORECASE)


class DeepCodeQuality(DeepRepoBase):
    """
    Class for analyzing code quality in a repository.
    """
    def __init__(self, repo_url_or_path, log, api_github):
        """
        Initialize the DeepCodeQuality analyzer with a repository
        URL or path.

        Args:
            repo_url_or_path (str): URL or path of the repository.
            log (RootLogger): Logger instance for logging.
            api_github (Github): GitHub API handler
        """
        super().__init__(repo_url_or_path, log, api_github)
        self.log.info("Initialized code quality analyzer for repository: "
                      f"{repo_url_or_path}")

    def collect_data(self):
        """
        Collect data about resources in the repository.
        """
        self.log.info("Collecting a list of resources from "
                      "the compute directory")
        self._repo_path = os.getenv("REPO_PATH")
        if not self._repo_path:
            raise EnvironmentError("self._repo_path environment"
                                   " variable is not set.")
        elif f"{self.repo_url}/" not in self._repo_path:
            raise ValueError(
                f"Repository path '{self._repo_path}' does not match "
                f"the repository URL '{self.repo_url}'."
            )
        if not os.path.isabs(self._repo_path):
            self._repo_path = os.path.abspath(self._repo_path)
        if not os.path.exists(self._repo_path):
            raise FileNotFoundError(
                f"Compute path '{self._repo_path}' does not exist."
            )
        try:
            self.repo_commit = subprocess.check_output(
                 ["git", "rev-parse", "HEAD"],
                 cwd=self._repo_path,
            ).decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get git commit hash: {e}")

        self.resources = [
            file for file in os.listdir(self._repo_path)
            if re.match(RESOURCE_PATTERN, file)
        ]
        if not self.resources:
            raise FileNotFoundError(
                f"No resources found in the {self._repo_path} directory. "
                "Check if you used the hashicorp/terraform-provider-google "
                "repository"
            )
        self.log.info(f"Found {len(self.resources)} compute resources.")

    def analyze_data(self):
        """
        Analyze the collected resource data.
        """
        self.log.info("Collecting info about existing TODO's.")
        self.todo_resources = {}

        for resource in self.resources:
            matches = {}
            resource_path = os.path.join(self._repo_path, resource)
            with open(resource_path, 'r', encoding='utf-8') as file:
                for line, todo in enumerate(file, 1):
                    match = TODO_PATTERN.search(todo)
                    if match:
                        matches.update({line: todo.strip()})
                if matches:
                    self.log.info(f"Found {len(matches)} TODO's in "
                                  f"{resource}")
                    self.todo_resources.update({resource: {
                        "todos_number": len(matches),
                        "matches": matches,
                    }})

    def generate_report(self):
        """
        Generate a report based on the analysis.
        """
        self.log.info("Generating code quality report.")
        if not self.todo_resources:
            raise ValueError("No TODO's found in the resources.")
        now_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = (f"code_quality_analysis_"
                     f"{self.repo_url.replace('/', '_')}"
                     f"_{now_str}.md")

        url_base = (f"https://github.com/{self.repo_url}/tree/"
                    f"{self.repo_commit}")

        with open(file_name, "w") as file:
            file.write("# Technical Debt Analysis Report for compute resources"
                       f" in {self.repo_url}\n\n")
            file.write("## Summary\n\n")
            file.write("* Number of analyzed resources and test files:"
                       f" {len(self.resources)}\n")
            file.write("* Number resources and test files with TODO's: "
                       f"{len(self.todo_resources)}\n\n")

            file.write("## List of files with TODO's\n\n")
            for key in self.todo_resources.keys():
                file.write(f"* {key}\n")

            file.write("\n ## Detailed information about TODO's\n")
            for key, items in self.todo_resources.items():
                resource_url = (
                    f"{url_base}{self._repo_path.split(self.repo_url)[1]}"
                    f"/{key}"
                )
                file.write(f"\n### {key}\n\n")
                for i, (line, todo) in enumerate(items["matches"].items(), 1):

                    file.write(f"{i}. [{key}#L{line}]({resource_url}#L{line}):"
                               f" {todo}\n")

        self.log.info(f"Report generated: {file_name}")
