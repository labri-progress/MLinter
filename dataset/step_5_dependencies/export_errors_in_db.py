import json
import logging
import os
import re
import subprocess
import sys

from dotenv import load_dotenv
from pymongo import MongoClient

DATASET_COMMIT_IDS_PATH = './output/result/commit_id'
DATASET_PROJECTS_PATH = './output/tmp'
LINTER_CONFIG_PATH = './output/tmp/.eslintrc'
LINTER_RESULTS_PATH = './output/result/linter'
LOGS_PATH = './output/logs'
RULE_DUMPS_PATH = './output/result/dump'

MAX_SIZE_ALLOCATED_TO_EXTRACTION_GO = 16
MAX_SIZE_VIOLATION_LINE = 115

RULES_DONE = []

current_working_directory = os.getcwd()
dataset_repo_path_length = len(current_working_directory + DATASET_PROJECTS_PATH)


def save_rules_errors_in_db(rules, database):
    for rule_index, rule in enumerate(rules, 1):
        if rule in RULES_DONE:
            logging.debug('==========================================================')
            logging.debug(f'Rule {rule} already done.')
            logging.debug('==========================================================\n')
            continue

        logging.debug('==========================================================')
        logging.debug(f'Processing rule: {rule} ({rule_index} / {len(rules)})')

        database[rule].drop()

        violations_count = 0
        fixes_count = 0
        current_memory_used = 0

        errors = []
        repo_index = 0
        for repo in repos:
            repo_name = repo['name']
            repo_commit_id = repo['commit_id']
            repo_index += 1
            logging.debug(f'\tProcessing repo: {repo_name} ({repo_index} / {len(repos)})')

            linter_result_file = open(LINTER_RESULTS_PATH + '/' + repo['filename'], 'r')
            linter_result = linter_result_file.read()
            linter_result_file.close()
            files_analyzed = json.loads(linter_result)

            file_index = 0
            for file in files_analyzed:
                if file_index % 200 == 0:
                    logging.debug(f'\t\tProcessing file {file_index + 1} / {len(files_analyzed)}')
                file_index += 1

                if 'source' not in file:
                    continue

                file_path = anonymize_path(file['filePath'])
                source = file['source']

                for violation in file['messages']:
                    if violation['ruleId'] != rule:
                        continue

                    violation_content = extract_violation_content(source, violation)
                    if violation_content == '':
                        continue

                    line = violation['line']
                    error_instance = {
                        'repo': repo_name,
                        'commitId': repo_commit_id,
                        'filePath': file_path,
                        'violation': violation_content,
                        'line': line,
                    }
                    violations_count += 1

                    fix_content = compute_fix_content(rule, source, violation)
                    if fix_content != '':
                        error_instance['fix'] = fix_content
                        fixes_count += 1

                    errors.append(error_instance)
                    current_memory_used += get_size(error_instance)

                    if current_memory_used > execution_max_size * 1000000000:
                        logging.debug(f'  Memory limit reached, dumping {len(errors)} errors')
                        database[rule].insert_many(errors)
                        errors.clear()
                        current_memory_used = 0

        if len(errors) > 0:
            logging.debug(f'  Dumping last {len(errors)} errors')
            database[rule].insert_many(errors)
            database[rule].create_index([('filePath', 1), ('line', 1)])

            subprocess.run([
                'mongodump',
                '--db=linter-extraction',
                '--collection=' + rule,
                '--out=' + RULE_DUMPS_PATH,
                '--uri=' + os.getenv('MONGO_URI'),
                '--gzip',
                '--quiet'
            ])
            os.remove(f'{RULE_DUMPS_PATH}/linter-extraction/{rule}.metadata.json.gz')

        logging.debug(f'Rule {rule} done')
        logging.debug('==========================================================\n')


def init_mandatory_folders():
    if not os.path.exists(LOGS_PATH):
        os.makedirs(LOGS_PATH)
    if not os.path.exists(RULE_DUMPS_PATH):
        os.makedirs(RULE_DUMPS_PATH)


def extract_repos_with_linter_result(results_path) -> [str]:
    logging.debug('Extracting repositories ...')

    repos = []
    for root, _, files in os.walk(results_path):
        files.sort()
        for file in files:
            repo = get_repo_from_file(file)
            repos.append({
                'filename': file,
                'name': repo,
                'commit_id': get_commit_id_from_repo(repo)
            })

    return repos


def get_repo_from_file(file_name):
    return re.search(r'^(.+)\.json$', file_name).group(1)


def get_commit_id_from_repo(repo):
    commit_id_file = open(DATASET_COMMIT_IDS_PATH + '/' + repo, 'r')
    commit_id = commit_id_file.read()
    commit_id_file.close()
    return commit_id


def extract_rules_from_linter_configuration(linter_config_path) -> [str]:
    logging.debug('Extracting rules from linter configuration...')
    linter_config_file = open(linter_config_path, 'r')
    config_file = linter_config_file.read()
    linter_config_file.close()

    config = json.loads(config_file)
    rules = []
    for rule in config['rules']:
        if config['rules'][rule] == 'warn':
            rules.append(rule)

    rules.sort()
    return rules


def anonymize_path(path):
    return '/' + path[dataset_repo_path_length:]


def extract_violation_content(source: str, violation) -> str:
    begin_line = violation['line']
    end_line = begin_line
    if 'endLine' in violation:
        end_line = violation['endLine']

    if begin_line != end_line:
        return ''

    lines = source.split('\n')
    try:
        violation_line = lines[begin_line - 1]

        return violation_line if len(violation_line) <= MAX_SIZE_VIOLATION_LINE else ''
    except IndexError:
        return ''


def compute_fix_content(rule_id, source, violation):
    if 'fix' not in violation:
        if rule_id != 'eqeqeq':
            return ''
        content_error = extract_violation_content(source, violation)
        return content_error.replace('===', '==').replace('!==', '!=').replace('==', '===').replace('!=', '!==')

    content_fixed = source[:violation['fix']['range'][0]] + violation['fix']['text'] + source[violation['fix']['range'][1]:]
    return extract_violation_content(content_fixed, violation)


# From: https://goshippo.com/blog/measure-real-size-any-python-object/
def get_size(obj, seen=None):
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0

    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


if __name__ == '__main__':
    load_dotenv()

    execs_number = int(sys.argv[1])
    current_exec = int(sys.argv[2])

    init_mandatory_folders()

    logging.basicConfig(filename=f'{LOGS_PATH}/5_{current_exec}.log', encoding='utf-8', filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.debug('==========================================================')

    execution_max_size = MAX_SIZE_ALLOCATED_TO_EXTRACTION_GO / execs_number
    logging.debug(f'Execution max size: {execution_max_size} Go')
    rule_ids = extract_rules_from_linter_configuration(LINTER_CONFIG_PATH)
    repos = extract_repos_with_linter_result(LINTER_RESULTS_PATH)

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

    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client['linter-extraction']

    save_rules_errors_in_db(rule_ids_selected, db)

    client.close()
