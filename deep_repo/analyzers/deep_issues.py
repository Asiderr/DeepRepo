#!/usr/bin/env python3
import hdbscan

from datetime import datetime
from deep_repo.deep_base import DeepRepoBase
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import manhattan_distances


class DeepIssues(DeepRepoBase):
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
        self.issues = {}
        self.analysis = {}

    def collect_data(self):
        """
        Collect data about issues in the repository.
        """
        self.log.info("Collecting issue data from the repository: "
                      f"{self.repo_url}")

        repo = self.git_api.get_repo(self.repo_url)
        if not repo:
            raise ValueError(f"Repository '{self.repo_url}' not found.")
        open_issues = repo.get_issues(state='open')
        for issue in open_issues:
            self.issues.update({issue.title: issue.html_url})

        if not self.issues:
            raise ValueError("Issues not available")

    def analyze_data(self):
        """
        Analyze the collected issue data.
        """
        self.log.info("Analyzing issue data.")
        if not self.issues:
            raise ValueError("Open issues not found.")

        model = SentenceTransformer("all-MiniLM-L12-v2")
        vectors = model.encode(list(self.issues.keys()),
                               normalize_embeddings=True)
        distance_matrix = manhattan_distances(vectors).astype("double")
        clustering = hdbscan.HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric="precomputed",
        ).fit_predict(distance_matrix)

        for label, issue in zip(clustering, list(self.issues.items())):
            title, url = issue
            self.analysis.setdefault(label, []).append(f"{title}: {url}")

        self.analysis = dict(sorted(self.analysis.items(),
                                    key=lambda item: len(item[1]),
                                    reverse=True))
        self.analysis[-1] = self.analysis.pop(-1)

    def generate_report(self):
        """
        Generate a report based on the analyzed issue data.
        """
        self.log.info("Generating report for issues.")
        if not self.analysis:
            raise ValueError("Analysis not found")

        now_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = (f"issue_analysis_{self.repo_url.replace('/', '_')}"
                     f"_{now_str}.md")

        with open(file_name, "w") as file:
            file.write(f"# Issues Analysis Report for {self.repo_url}\n\n")
            for i, items in enumerate(self.analysis.items()):
                label, issues = items
                file.write(f"### Group {i+1 if label != -1 else 'Other'}:\n\n")
                for issue in issues:
                    file.write(f"* {issue}\n")
                file.write("\n---------------------------------\n\n")

        self.log.info(f"Report generated: {file_name}")
