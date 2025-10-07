#!/usr/bin/env python3

import argparse
import colorlog
import os

from dotenv import load_dotenv, find_dotenv
from github import Github, Auth


class DeepRepoConfig:
    def setup_logger(self):
        """
        Set up the logger with color formatting for console output.
        """
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(asctime)s [%(levelname)s] - %(log_color)s%(message)s%(reset)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        ))

        self.log = colorlog.getLogger()
        self.log.setLevel(colorlog.DEBUG)
        self.log.addHandler(handler)

    def parse_cmdline(self):
        """
        Method parses commandline input and shows help message if needed.
        """
        description = (
            "Tool analysis most common issues in the GitHub repositories"
        )
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "-r",
            "--repo-path",
            required=True
        )
        mode_group = parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument(
            "-q",
            "--issue_quality",
            action="store_true",
            help="Analyse issue quality"
        )
        mode_group.add_argument(
            "-b",
            "--boomerangs",
            action="store_true",
            help="Analyse boomerangs in test failures"
        )
        mode_group.add_argument(
            "-i",
            "--issues",
            action="store_true",
            help="Analyse GitHub issues"
        )
        mode_group.add_argument(
            "-m",
            "--mmv1_resources",
            action="store_true",
            help="Analyse compute resources type"
        )
        mode_group.add_argument(
            "-c",
            "--code_quality",
            action="store_true",
            help="Analyse code quality"
        )
        mode_group.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Create full repo analysis"
        )
        return parser

    def load_env_vars(self, envpath=".env"):
        """
        Load environment variables from a .env file.
        Args:
            envpath (str): Path to the .env file. Defaults to ".env".
        """

        if not hasattr(self, "log"):
            raise RuntimeError("Logger not initialized. "
                               "Call setup_logger() first.")

        if not find_dotenv(envpath):
            raise FileNotFoundError(f"No .env file found at {envpath}. "
                                    "Environment variables may not be set.")

        load_dotenv(envpath)
        self.log.info(f"Environment variables loaded from {envpath}.")

    def setup_git_api(self):
        """
        Set up the GitHub API client using an access token from environment
        variables.
        """
        if not hasattr(self, "log"):
            raise RuntimeError("Logger not initialized. "
                               "Call setup_logger() first.")

        token = os.getenv("GITHUB_TOKEN")
        if token:
            auth = Auth.Token(token)
        else:
            self.log.warning("No GITHUB_TOKEN found in environment variables. "
                             "Using unauthenticated GitHub API client.")

        git_api = Github(auth=auth, per_page=100) if token else Github(
            per_page=100
        )
        self.log.info("GitHub API client initialized.")

        return git_api
