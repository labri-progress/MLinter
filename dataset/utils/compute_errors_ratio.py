import os
import pandas as pd

CLONES_PATH = '../output/tmp'
RESULT_LINTERS_PATH = '../output/result/linter'
STATS_FILE = './stats.csv'

file_number = 0
line_number = 0
for _, _, results in os.walk(RESULT_LINTERS_PATH):
    results.sort()

    for result in results:
        if not result.endswith('.json'):
            continue

        result_df = pd.read_json(os.path.join(RESULT_LINTERS_PATH, result))
        files_analysed = result_df['filePath'].unique()
        file_number += len(files_analysed)
        for file in files_analysed:
            try:
                line_number += sum(1 for _ in open(file))
            except UnicodeDecodeError:
                continue

stats_df = pd.read_csv(STATS_FILE)
with open('ratio.csv', 'w') as ratio_file:
    ratio_file.write('rule,line_number,line_violation_number,line_ratio,file_number,file_violation_number,file_ratio\n')
    for _, row in stats_df.iterrows():
        rule = row['rule']
        line_violation_number = row['violations_count']
        file_violation_number = row['files_count']

        line_ratio = round(line_violation_number / line_number, ndigits=10)
        file_ratio = round(file_violation_number / file_number, ndigits=10)

        ratio_file.write(f'{rule},{line_number},{line_violation_number},{line_ratio},{file_number},{file_violation_number},{file_ratio}\n')
