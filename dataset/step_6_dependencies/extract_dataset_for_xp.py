import logging
import math
import random
import sys

import numpy as np

from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.utils import resample

from extract_all_file_paths_analysed import *

random_state = 20221118
np.random.seed(random_state)
random.seed(random_state)

DATA_PATH = './output/result/data'
FILES_ANALYSED_FILENAME = './output/result/files.csv'
LOGS_PATH = './output/logs'
REPO_PATH = './output/tmp'

RULES_TO_IGNORE = ['arrow-spacing', 'computed-property-spacing', 'generator-star-spacing', 'template-curly-spacing']

MAX_SIZE_VIOLATION_LINE = 115

# SETS_NUMBER = 1
SETS_NUMBER = 100
# SIZES = [10]
SIZES = [1000, 100, 10]
# CONFS = [0.5]
CONFS = [0, 0.5, 1]
# FILE_NUMBER = 1
FILE_NUMBER = 5


def extract_dataset_for_rule_ids(rule_ids, database):
    if not os.path.exists(FILES_ANALYSED_FILENAME):
        extract_all_file_paths_analyzed()
    file_analysed_df = pd.read_csv(FILES_ANALYSED_FILENAME)

    for rule_index, rule_id in enumerate(rule_ids, 1):
        logging.debug('==========================================================')
        logging.debug(f'Processing rule: {rule_id} ({rule_index} / {len(rule_ids)})')
        if rule_id in RULES_TO_IGNORE:
            logging.debug(f'Rule ignored')
            logging.debug('==========================================================')
            continue

        rule_violations, rule_fixes = get_violations_and_fixes_for_rule_id(rule_id, database)

        for conf in CONFS:
            logging.debug(f'\tConf {conf}')

            for size in SIZES:
                logging.debug(f'\t\tSize {size}')

                dataset_path = os.path.join(DATA_PATH, rule_id, str(conf), str(size))
                train_path = dataset_path + '/train'
                os.makedirs(train_path, exist_ok=True)
                balanced_corpus_validation_path = dataset_path + '/balanced_corpus_validation'
                os.makedirs(balanced_corpus_validation_path, exist_ok=True)
                ground_truth_with_violation_validation_path = dataset_path + '/ground_truth_with_violation_validation'
                os.makedirs(ground_truth_with_violation_validation_path, exist_ok=True)

                for bootstrap_index in range(0, SETS_NUMBER):
                    logging.debug(f'\t\t\tCreating dataset {bootstrap_index+1} / {SETS_NUMBER}')

                    train_violations, train_no_violations, train_fixes = write_bootstrap_train_for_rule(
                        rule_id,
                        rule_violations,
                        rule_fixes,
                        file_analysed_df,
                        database,
                        conf,
                        size,
                        train_path,
                        bootstrap_index
                    )

                    write_balanced_corpus_validation_for_rule(
                        rule_id,
                        rule_violations,
                        rule_fixes,
                        file_analysed_df,
                        database,
                        train_violations,
                        train_no_violations,
                        train_fixes,
                        balanced_corpus_validation_path,
                        bootstrap_index
                    )

                    write_ground_truth_with_violations_validation(
                        rule_violations,
                        train_violations,
                        FILE_NUMBER,
                        ground_truth_with_violation_validation_path,
                        bootstrap_index
                    )

                    logging.debug(f'\t\t\tDataset {bootstrap_index+1} / {SETS_NUMBER} done')

                logging.debug(f'\t\tSize {size} done')

            logging.debug(f'\tConf {conf} done')

        logging.debug(f'Rule {rule_id} done')
        logging.debug('==========================================================\n')


def get_violations_and_fixes_for_rule_id(rule_id, database):
    violations = list(database[rule_id].find({'violation': {'$exists': True}}, {'_id': 0, 'filePath': 1, 'line': 1, 'violation': 1}))
    violations_df = pd.DataFrame(violations)
    violations_df = violations_df.rename(columns={'violation': 'content'})
    violations_df['value'] = 1

    fixes = list(database[rule_id].find({'fix': {'$exists': True}}, {'_id': 0, 'filePath': 1, 'line': 1, 'fix': 1}))
    fixes_df = pd.DataFrame(fixes)
    fixes_df = fixes_df.drop_duplicates(subset=['filePath', 'line'], keep=False)
    fixes_df = fixes_df.rename(columns={'fix': 'content'})
    fixes_df['value'] = 0

    return violations_df, fixes_df


def write_bootstrap_train_for_rule(rule, violations, fixes, files_df, database, conf, size, train_path, index):
    logging.debug(f'\t\t\t\tCreating train set...')

    violation_number = int(size / 2)
    logging.debug(f'\t\t\t\t\tSelecting {violation_number} violations...')
    train_violations = resample(violations, n_samples=violation_number, replace=True)
    logging.debug(f'\t\t\t\t\t{len(train_violations)} violations selected')

    no_violation_number = math.ceil(size - violation_number - conf * violation_number)
    logging.debug(f'\t\t\t\t\tSelecting {no_violation_number} no violations...')
    train_no_violations = extract_n_lines_with_no_rule_violation(no_violation_number, rule, files_df, database)
    logging.debug(f'\t\t\t\t\t{len(train_no_violations)} no violations selected')

    fix_number = int(size - violation_number - no_violation_number)
    logging.debug(f'\t\t\t\t\tSelecting {fix_number} fixes...')
    train_fixes = resample(fixes, n_samples=fix_number, replace=True)
    logging.debug(f'\t\t\t\t\t{len(train_fixes)} fixes selected')

    write_lines_in_csv(train_violations, train_no_violations, train_fixes, train_path, index)

    return train_violations, train_no_violations, train_fixes


def write_balanced_corpus_validation_for_rule(rule, violations, fixes, files_df, database, train_violations, train_no_violations, train_fixes, validation_path, index):
    logging.debug(f'\t\t\t\tCreating balanced corpus validation set...')

    validation_violations = violations[~violations.index.isin(train_violations.index)]
    violation_number = len(train_violations.index)
    logging.debug(f'\t\t\t\t\tSelecting {violation_number} violations...')
    validation_violations = resample(validation_violations, n_samples=violation_number, replace=False)
    logging.debug(f'\t\t\t\t\t{len(validation_violations)} violations selected')

    no_violation_number = len(train_no_violations.index)
    logging.debug(f'\t\t\t\t\tSelecting {no_violation_number} no violations...')
    validation_no_violations = extract_n_lines_with_no_rule_violation(no_violation_number, rule, files_df, database, train_no_violations)
    logging.debug(f'\t\t\t\t\t{len(validation_no_violations)} no violations selected')

    validation_fixes = fixes[~fixes.index.isin(train_fixes.index)]
    fix_number = len(train_fixes.index)
    logging.debug(f'\t\t\t\t\tSelecting {fix_number} fixes...')
    validation_fixes = resample(validation_fixes, n_samples=fix_number, replace=False)
    logging.debug(f'\t\t\t\t\t{len(validation_fixes)} fixes selected')

    write_lines_in_csv(validation_violations, validation_no_violations, validation_fixes, validation_path, index)


def extract_n_lines_with_no_rule_violation(n, rule, files_df, database, exclude=pd.DataFrame(columns=['content'])):
    current_try = 0
    no_violations = []

    while len(no_violations) < n and current_try < n * 10:
        current_try += 1

        random_file_df = files_df.sample()
        random_file = random_file_df.iloc[0]
        file_path = random_file['filePath']
        file_lines_number = random_file['linesNumber']

        line_number = 0
        if file_lines_number > 1:
            line_number = random.randint(0, file_lines_number - 1)
        try:
            line_content = get_line_in_file_path(line_number, file_path)
            if line_content is None \
                    or has_rule_violation_on_file_and_at_line(rule, file_path, line_number, database) \
                    or not exclude[exclude['content'] == line_content].empty \
                    or len(line_content) > MAX_SIZE_VIOLATION_LINE:
                continue

            no_violations.append({'content': line_content, 'value': 0})
        except UnicodeDecodeError:
            continue

    return pd.DataFrame(no_violations)


def get_line_in_file_path(line_number: int, file_path: str) -> str:
    with open(file_path, 'r') as file:
        for pos, line in enumerate(file):
            if pos == line_number:
                return line


def has_rule_violation_on_file_and_at_line(rule: str, file_path: str, line: int, database) -> bool:
    violation = database[rule].find_one({'filePath': file_path, 'line': line})
    return violation is not None


def write_lines_in_csv(violations, no_violations, fixes, save_path, index):
    violations = violations[['content', 'value']]
    fixes = fixes[['content', 'value']]

    dataset = pd.concat([violations, no_violations, fixes]).sample(frac=1)
    with open(os.path.join(save_path, f'{index}.csv'), 'w') as file:
        file.write('content,value\n')
        for _, row in dataset.iterrows():
            file.write(f'{escape_string_for_csv(row["content"])},{row["value"]}\n')


def escape_string_for_csv(string):
    return '' if string is None else '"' + string.replace('"', '""') + '"'


def write_ground_truth_with_violations_validation(rule_violations, train_violations, files_number, validation_path, index):
    logging.debug(f'\t\t\t\tCreating ground truth with violations validation set...')

    violations_not_used = rule_violations[~rule_violations.index.isin(train_violations.index)]
    file_paths = violations_not_used['filePath'].unique()
    random.shuffle(file_paths)

    ground_truth = []
    file_paths_used = 0
    current_file_path_index = 0
    while file_paths_used < files_number and current_file_path_index < len(file_paths):
        file_path = file_paths[current_file_path_index]
        current_file_path_index += 1

        try:
            with open(f'{REPO_PATH}{file_path}', 'r') as file_content:
                file_path_violations = violations_not_used[violations_not_used['filePath'] == file_path]
                violations_lines = file_path_violations['line'].unique()

                for line_number, line in enumerate(file_content, 1):
                    value = 1 if line_number in violations_lines else 0
                    ground_truth.append({'content': line, 'value': value})

                file_paths_used += 1
        except UnicodeDecodeError:
            logging.debug('\t\t\t\tUnicodeDecodeError')
            continue

    ground_truth_df = pd.DataFrame(ground_truth)
    ground_truth_df.to_csv(os.path.join(validation_path, f'{index}.csv'), index=False)


if __name__ == '__main__':
    load_dotenv()

    execs_number = int(sys.argv[1])
    current_exec = int(sys.argv[2])
    logging.basicConfig(filename=f'{LOGS_PATH}/6_{current_exec}.log', encoding='utf-8', filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client['linter-extraction']

    rule_ids = db.list_collection_names()
    rule_ids.sort()

    rules_size = len(rule_ids)
    rules_by_exec = int(rules_size / execs_number)
    current_exec_start, current_exec_end = 0, 0
    for computing_exec in range(0, current_exec + 1):
        current_exec_start = current_exec_end
        current_exec_end = current_exec_start + rules_by_exec
        if rules_size % execs_number > computing_exec:
            current_exec_end += 1
    rule_ids_selected = rule_ids[current_exec_start:current_exec_end]
    logging.debug('%s rules selected for this execution.\n', str(len(rule_ids_selected)))

    extract_dataset_for_rule_ids(rule_ids_selected, db)

    client.close()
