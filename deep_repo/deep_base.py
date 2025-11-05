#!/usr/bin/env python3
#
# Copyright 2025 Norbert Kamiński <norbert.kaminski@infogain.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from abc import ABC, abstractmethod
from github import Github
from logging import RootLogger


class DeepRepoBase(ABC):
    """
    Abstract base class for deep repository operations.
    """
    def __init__(self, repo_url_or_path, log: RootLogger, api_github: Github):
        """
        Initialize the repository with a URL.

        Args:
            repo_url_or_path (str): URL of the repository.
        """
        self.repo_url = repo_url_or_path
        self.log = log
        self.git_api = api_github

    @abstractmethod
    def collect_data(self):
        """
        Retrieve information about the repository.
        """
        pass

    @abstractmethod
    def analyze_data(self):
        """
        Analyze the collected data from the repository.
        """
        pass

    @abstractmethod
    def generate_report(self):
        """
        Generate a report based on the analyzed data.
        """
        pass

    def run(self):
        """
        Execute the data collection, analysis, and report generation.
        """
        try:
            self.collect_data()
        except ValueError as e:
            self.log.error(f"Error collecting data: {e}")
            return
        self.analyze_data()
        self.generate_report()
