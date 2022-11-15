import requests

CLONE_URL_REPOS_DATASET_PATH = 'output/result/repo_urls/dataset.txt'

MAX_REPO_BY_REQUEST = 100
LANGUAGE = 'javascript'
MIN_STARS = 10000


def get_github_repo_list():
    repos_file = open(CLONE_URL_REPOS_DATASET_PATH, 'w')

    current_page = 1
    has_next_page = True
    while has_next_page:
        response = requests.get(f'https://api.github.com/search/repositories?q=language:{LANGUAGE}+stars:>{MIN_STARS}&sort=stars&order=desc&page={current_page}&per_page={MAX_REPO_BY_REQUEST}')
        data = response.json()

        for repo in data['items']:
            full_name = repo['full_name'].replace('/', '_')
            clone_url = repo['clone_url']
            repos_file.write(f'{full_name}:{clone_url}\n')

        has_next_page = len(data['items']) > 0
        current_page += 1

    repos_file.close()


if __name__ == '__main__':
    get_github_repo_list()
