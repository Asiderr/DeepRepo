#!/usr/bin/env python3
#
# Copyright 2025 Norbert Kamiński <norbert.kaminski@infogain.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import os

from datetime import datetime, timedelta
from deep_repo.deep_base import DeepRepoBase


class DeepIssuesQuality(DeepRepoBase):
    """
    Class for analyzing issues in a repository.
    """
    def __init__(self, repo_url_or_path, log, api_github):
        """
        Initialize the DeepIssues analyzer with a repository URL or path.

        Args:
            repo_url_or_path (str): URL or path of the repository.
            log (RootLogger): Logger instance for logging.
            api_github (Github): GitHub API handler
        """
        super().__init__(repo_url_or_path, log, api_github)
        self.log.info("Initialized issues analyzer for repository: "
                      f"{repo_url_or_path}")
        self.issues = []

    def collect_data(self):
        """
        Collect data about issues in the repository.
        """
        self.log.info("Collecting issue data from the repository: "
                      f"{self.repo_url}")

        repo = self.git_api.get_repo(self.repo_url)
        if not repo:
            raise ValueError(f"Repository '{self.repo_url}' not found.")
        self._label = os.getenv("ISSUE_LABEL")
        closed_issues = []
        if self._label:
            self.log.info(f"Filtering issues with label: {self._label}")
            self._label = self._label.split(",")
            for label in self._label:
                self.log.debug(f"Fetching issues with label: {label}")
                closed_issues.append(repo.get_issues(state='closed',
                                                     labels=[label]))
        else:
            self.log.info("No issue label filter applied, fetching issues"
                          " closed in the last 30 days.")
            since = datetime.now() - timedelta(days=30)
            closed_issues.append(repo.get_issues(state='closed', since=since))
        for issue_list in closed_issues:
            for issue in issue_list:
                if ("Failing test(s)" in issue.title or issue.comments == 0
                        or "/pull/" in issue.html_url):
                    continue
                self.issues.append({
                    "title": issue.title,
                    "created_at": issue.created_at,
                    "closed_at": issue.closed_at,
                    "resolution_time": issue.closed_at - issue.created_at,
                    "comments_number": issue.comments,
                    "comments": issue.get_comments(),
                    "reactions": issue.reactions["total_count"],
                    "url": issue.html_url,
                })

        if not self.issues:
            raise ValueError("Issues not available")

    def _issue_resolution_analysis(self):
        """
        Calculate the average open time of issues.
        """
        total_open_time = timedelta()
        self.longest_resolution_issues = sorted(
            self.issues, key=lambda x: x["resolution_time"],
            reverse=True
        )[:10]
        count = 0
        for issue in self.issues:
            total_open_time += issue["resolution_time"]
            count += 1

        return total_open_time / count if count > 0 else timedelta(0)

    def _issue_comments_analysis(self):
        """
        """
        total_first_comment_time = timedelta()
        total_comments = 0
        first_reaction_analysis_list = []
        count = 0
        for issue in self.issues:
            if issue["comments_number"] == 0:
                continue
            total_comments += issue["comments_number"]
            first_comment = issue["comments"][0]
            first_comment_creation_time = first_comment.created_at
            time_to_first_response = (
                first_comment_creation_time - issue["created_at"]
            )
            first_reaction_analysis_list.append(
                {
                    "title": issue["title"],
                    "first_reaction_time": time_to_first_response,
                    "url": issue["url"]
                }
            )

            total_first_comment_time += time_to_first_response
            count += 1

        self.most_commented_issues = sorted(
            self.issues,
            key=lambda x: x["comments_number"],
            reverse=True
        )[:10]
        self.average_comment_number = (
            total_comments / count if count > 0 else 0
        )
        self.longest_reaction_issues = sorted(
            first_reaction_analysis_list,
            key=lambda x: x["first_reaction_time"],
            reverse=True
        )[:10]
        return total_first_comment_time / count if count > 0 else timedelta(0)

    def _reactions_analysis(self):
        """
        """
        total_reactions_number = 0
        self.most_engaging_issues = sorted(
            self.issues, key=lambda x: x["reactions"],
            reverse=True
        )[:10]
        count = 0
        for issue in self.issues:
            total_reactions_number += issue["reactions"]
            count += 1

        return total_reactions_number / count if count > 0 else 0

    def analyze_data(self):
        """
        Analyze the collected issue data.
        """
        self.log.info("Analyzing quality of the issues.")
        # Average live time, average number of comments, average time to first
        # comment, average reaction, longest time to close
        if not self.issues:
            raise ValueError("Open issues not found.")

        self.log.info(f"Number of issues analyzed: {len(self.issues)}")

        self.average_open_time = self._issue_resolution_analysis()
        self.log.debug(f"Average time to close a issue: "
                       f"{self.average_open_time}")
        self.log.debug("The issues with the longest resolution time:"
                       f" {self.longest_resolution_issues}")

        self.average_reaction_time = self._issue_comments_analysis()
        self.log.debug("Average time to first comment: "
                       f"{self.average_reaction_time}")
        self.log.debug("The issues with the longest reaction time:"
                       f" '{self.longest_reaction_issues}'")
        self.log.debug("Average number of comments: "
                       f"{self.average_comment_number}")
        self.log.debug("The most commented issues:"
                       f" '{self.most_commented_issues}'")

        self.average_reaction_count = self._reactions_analysis()
        self.log.debug("Average number of reactions for issue: "
                       f"{self.average_reaction_count}")
        self.log.debug("The most engaging issues:"
                       f" '{self.most_engaging_issues}'")

    def generate_report(self):
        """
        Generate a report based on the analyzed issue data.
        """
        self.log.info("Generating report for issues.")
        if (not self.average_open_time or not self.average_reaction_time
                or not self.average_reaction_count):
            raise ValueError("Analysis not found")

        now_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = ("issue_quality_analysis_"
                     f"{self.repo_url.replace('/', '_')}_{now_str}.md")
        with open(file_name, "w") as file:
            if self._label:
                bullet = "\n* "
                file.write("# Issues Quality Analysis Report for issues with "
                           f"in {self.repo_url}\n\n")
                file.write("**Filtered by label(s):**"
                           f"{bullet.join(self._label)}\n\n")
            else:
                file.write("# Issues Quality Analysis Report for "
                           f"{self.repo_url}\n\n")
            file.write("## Issues resolution time\n\n")
            file.write("Average time of issue resolution: "
                       f"{self.average_open_time}\n\n")
            file.write("### Issues with the longest resolution time\n\n")
            for i, issue in enumerate(self.longest_resolution_issues):
                file.write(f"{i+1}. {issue['title']} - "
                           f"{issue['resolution_time']}: {issue['url']}\n")
            file.write("\n---------------------------------\n\n")

            file.write("## Time to first comment\n\n")
            file.write("Average time to first comment: "
                       f"{self.average_reaction_time}\n\n")
            file.write("### Issues with the longest time to first comment\n\n")
            for i, issue in enumerate(self.longest_reaction_issues):
                file.write(f"{i+1}. {issue['title']} - "
                           f"{issue['first_reaction_time']}: {issue['url']}\n")
            file.write("\n---------------------------------\n\n")

            file.write("## The most commented issues\n\n")
            file.write("Average number of comments: "
                       f"{self.average_comment_number}\n\n")
            file.write("### List of the most commented issues\n\n")
            for i, issue in enumerate(self.most_commented_issues):
                file.write(f"{i+1}. {issue['title']} - "
                           f"{issue['comments_number']}: {issue['url']}\n")
            file.write("\n---------------------------------\n\n")

            file.write("## The most engaging issues\n\n")
            file.write("Average number of reactions for issue: "
                       f"{self.average_reaction_count}\n\n")
            file.write("### List of the most engaging issues\n\n")
            for i, issue in enumerate(self.most_engaging_issues):
                file.write(f"{i+1}. {issue['title']} - "
                           f"{issue['reactions']}: {issue['url']}\n")
            file.write("\n---------------------------------\n\n")
        self.log.info(f"Report generated: {file_name}")
