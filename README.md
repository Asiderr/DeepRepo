# Deep Repository Analysis

This tool allows to audit the google terraform provider repository
(hashicorp/terraform-provider-google and
hashicorp/terraform-provider-google-beta).

## Functionalities

* Technical dept analysis
* Resource generation analysis
* Open issues analysis
* Analysis of the issue support issue
* Boomerang tests analysis

## Usage

```bash
usage: python -m deep_repo.deep_repo [-h] -r REPO_PATH (-q | -b | -i | -m | -c | -a)

Tool analysis most common issues in the terraform-provider-repositories (hashicorp/terraform-provider-google and hashicorp/terraform-provider-google-beta)

options:
  -h, --help            show this help message and exit
  -r REPO_PATH, --repo-path REPO_PATH
  -q, --issue_quality   Analyse issue quality
  -b, --boomerangs      Analyse boomerangs in test failures
  -i, --issues          Analyse GitHub issues
  -m, --mmv1_resources  Analyse compute resources type
  -c, --code_quality    Analyse code quality - technical dept
  -a, --all             Create full repo analysis
```

> Note that `-a` currently works only for V1 repository

## Tool setup

Create python venv

Create `.env` file based on [.envexample](.envexample).

* **GITHUB_TOKEN** (required) - Github authentication token -
[documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
* **REPO_PATH** (required) - path of the terraform provider google repository.
Repository must be placed in a folder named hashicorp eg.
`/PATH/TO/hashicorp/terraform-provider-google-beta/google-beta/services/compute`
* **ISSUE_LABEL** (optional) - Filter for repository issues

