import os
import pandas as pd
import random

FILES_NUMBER_TO_SELECT = 385
LINTER_RESULTS_PATH = '../output/result/linter'

analysed_files = []

for _, _, repos in os.walk(LINTER_RESULTS_PATH):
    repos.sort()
    repos_number = len(repos)

    for index, repo in enumerate(repos):
        print(f'Processing repo: {index} / {repos_number}', flush=True)
        df = pd.read_json(os.path.join(LINTER_RESULTS_PATH, repo), orient='records')
        analysed_files += df['filePath'].tolist()

random.shuffle(analysed_files)
selected_files = analysed_files[:FILES_NUMBER_TO_SELECT]
print(len(analysed_files), 'files')
print(len(selected_files), 'files selected')

csv_file = open('lines_size.csv', 'w')
csv_file.write('filePath,line,size\n')
for file_path in selected_files:
    with open(file_path, 'r') as repo:
        lines = repo.readlines()

        for index, line in enumerate(lines):
            line_size = len(line)
            csv_file.write(f'{file_path},{index},{line_size}\n')

csv_file.close()
