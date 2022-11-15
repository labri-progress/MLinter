import os

import pandas as pd

LINTER_RESULTS_PATH = './output/result/linter'
FILES_ANALYSED_FILENAME = './output/result/files.csv'


def extract_all_file_paths_analyzed():
    file_paths = []
    for root, _, linter_results in os.walk(LINTER_RESULTS_PATH):
        linter_results.sort()

        for result in linter_results:
            if not result.endswith('.json'):
                continue
            result_df = pd.read_json(os.path.join(root, result))
            files_analysed = result_df['filePath'].unique().tolist()

            for file_analysed in files_analysed:
                try:
                    with open(file_analysed, 'r') as file:
                        lines_number = sum(1 for _ in file)

                    file_paths.append({'filePath': file_analysed, 'linesNumber': lines_number})
                except Exception:
                    continue

    pd.DataFrame(file_paths).to_csv(FILES_ANALYSED_FILENAME, index=False)


if __name__ == '__main__':
    extract_all_file_paths_analyzed()
