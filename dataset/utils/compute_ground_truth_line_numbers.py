import os

import pandas as pd

DATA_PATH = '/Users/clatappy/Downloads'
GROUND_TRUTH_FOLDER = 'ground_truth_with_violation_validation'
OUTPUT_FILE = 'ground_truth_line_numbers.csv'


with open(OUTPUT_FILE, 'w') as result_file:
    result_file.write('rule,conf,size,total_line,mean\n')

    for root_data_path, rules, _ in os.walk(DATA_PATH):
        rules.sort()

        for rule in rules:
            for root_conf, confs, _ in os.walk(os.path.join(root_data_path, rule)):
                confs.sort()

                for conf in confs:
                    for root_size, sizes, _ in os.walk(os.path.join(root_conf, conf)):
                        sizes.sort()

                        for size in sizes:
                            ground_truth_path = os.path.join(root_size, size, GROUND_TRUTH_FOLDER)

                            current_file = 0
                            total_line_number = 0
                            while os.path.exists(os.path.join(ground_truth_path, f'{current_file}.csv')):
                                file_path = os.path.join(ground_truth_path, f'{current_file}.csv')
                                current_file += 1

                                file_path_df = pd.read_csv(file_path)
                                total_line_number += len(file_path_df)

                            mean = round(total_line_number / current_file)
                            result_file.write(f'{rule},{conf},{size},{total_line_number},{mean}\n')
                        break
                break
        break
