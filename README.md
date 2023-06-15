# Bounce Challenge


## Exercise 1

Your first task is to write a Python script to extract data from the GitHub API. The API returns paginated responses for repository data. Your script should be able to handle paging, cursors, and authentication and should store the extracted data in a suitable format for further analysis.

Here's the API endpoint you need to extract data from: `https://api.github.com/users/bounceapp/repos`

### Requirements:

1. Implement paging logic to retrieve all repositories of the user.
2. Handle cursor-based pagination if applicable.
3. Handle API authentication.
4. Save the data in a CSV format for further analysis.

### Assumptions
- The implementation must be manual and not use any existing library such as PyGithub (https://github.com/PyGithub/PyGithub) or Scrapy
- The implementation must be sequential due to the linear dependency of the cursor pagination meaning, no multi-threading nor Asyncio implementations are valid

#### Future Work
- Replace the custom library with a set of existing, heavily tested implementations such as Scrapy and PyGithub
- Add unit and integration tests
- Add a CI/CD for the target deployment platform

### Solution

Notes: The challenge requires saving the data in CSV. Given it is unstructured data, I would opt instead to store it in an optimized format (Parquet, Delta) or as an alternative, JSON.

> The implementation can be found in the `bounce_challenge/*`, `main.py`, `setup.py` directories

Note: In order to use the authentication via Token, make sure the `AUTH_TOKEN` environment variable is set

To start the process execute the following command:
> `bounce_challenge --s github_repositories --u bounceapp --o data.csv --use_token`

| Argument Name | Short Option | Long Option | Type | Is Optional | Example |  Description | Default Value |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |------------- |------------- |
| Scraper  | `--s`  | `--scraper_name`  | String  | False | `--scraper_name github_repositories` | The name of the scraper instance to be initialized |  |
| Scraper  | `--u`  | `--user_name`  | String  | False | `--user_name bounce-app` | The user name to be scraped | |
| Scraper  | `--o`  | `--output_path`  | String  | False | `--output_path data.csv` | The output path where to store the extracted data |  |
| Scraper  | `--t`  | `--use_token`  | Flag  | True | `--use_token` | Should a token be used for authentication (stored in Env variable `AUTH_TOKEN`) | |
| Scraper  | `--f`  | `--filters_list`  | String List  | False | `--filters_list user_id, repo_id` | A list of extracted data attributes to be selected | `id, node_id, name, full_name, private,html_url, description ,fork,url, created_at, updated_at, pushed_at, git_url, ssh_url, clone_url, homepage, size, has_issues, has_projects, has_downloads, archived, disabled, license, visibility, watchers` |