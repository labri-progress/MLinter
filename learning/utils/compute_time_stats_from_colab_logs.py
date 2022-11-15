import re

COLAB_LOG_PATH = 'colab.log'
OUTPUT_PATH = 'time_stats.csv'

rule_regex = r'^==============  (\S+)  \( \d+ \/ \d+ \) ==============$'
conf_regex = r'^\s+Conf (\S+)$'
size_regex = r'^\s+Size (\d+)$'
file_regex = r'^\s+File (\d+)$'
total_training_time_regex = r'^\s+Total training time: (\d+:\d+:\d+)$'
total_validation_time_regex = r'^\s+Total validation time: (\d+:\d+:\d+)$'
total_time_regex = r'^\s+Total time for file \d+: (\d+:\d+:\d+)$'


def compute_time_stats_from_colab_logs():
    rule = ''
    conf = ''
    size = ''
    file = ''
    training_time = ''
    current_validation = ''
    balanced_corpus_validation = ''
    ground_truth_with_violation_validation = ''

    rule_training_times = []
    conf_training_times = []
    size_training_times = []

    rule_balanced_corpus_validation_times = []
    conf_balanced_corpus_validation_times = []
    size_balanced_corpus_validation_times = []

    rule_ground_truth_with_violation_validation_times = []
    conf_ground_truth_with_violation_validation_times = []
    size_ground_truth_with_violation_validation_times = []

    rule_total_times = []
    conf_total_times = []
    size_total_times = []

    with open(COLAB_LOG_PATH, 'r') as log_file, open(OUTPUT_PATH, 'w') as output_file:
        output_file.write('rule,conf,size,file,training_time,balanced_corpus_validation_time,ground_truth_with_violation_validation_time,total_time\n')

        for line in log_file:
            if re.search(rule_regex, line):
                rule = re.match(rule_regex, line).group(1)

            if re.search(conf_regex, line):
                conf = re.match(conf_regex, line).group(1)

            if re.search(size_regex, line):
                size = re.match(size_regex, line).group(1)

            if re.search(file_regex, line):
                file = re.match(file_regex, line).group(1)

            if re.search(total_training_time_regex, line):
                training_time = re.match(total_training_time_regex, line).group(1)

                rule_training_times.append(training_time)
                conf_training_times.append(training_time)
                size_training_times.append(training_time)

            if 'balanced_corpus...' in line:
                current_validation = 'balanced_corpus'

            if 'ground_truth_with_violation...' in line:
                current_validation = 'ground_truth_with_violation'

            if re.search(total_validation_time_regex, line):
                validation_time = re.match(total_validation_time_regex, line).group(1)

                if current_validation == 'balanced_corpus':
                    balanced_corpus_validation = validation_time
                    rule_balanced_corpus_validation_times.append(validation_time)
                    conf_balanced_corpus_validation_times.append(validation_time)
                    size_balanced_corpus_validation_times.append(validation_time)

                if current_validation == 'ground_truth_with_violation':
                    ground_truth_with_violation_validation = validation_time
                    rule_ground_truth_with_violation_validation_times.append(validation_time)
                    conf_ground_truth_with_violation_validation_times.append(validation_time)
                    size_ground_truth_with_violation_validation_times.append(validation_time)

            if re.search(total_time_regex, line):
                total_time = re.match(total_time_regex, line).group(1)

                rule_total_times.append(total_time)
                conf_total_times.append(total_time)
                size_total_times.append(total_time)

                output_file.write(f'{rule},{conf},{size},{file},{training_time},{balanced_corpus_validation},{ground_truth_with_violation_validation},{total_time}\n')

            if 'Total time for size ' in line:
                write_size_mean(
                    rule,
                    conf,
                    size,
                    [
                        size_training_times,
                        size_balanced_corpus_validation_times,
                        size_ground_truth_with_violation_validation_times,
                        size_total_times,
                    ],
                    output_file
                )

            if 'Total time for conf ' in line:
                write_conf_mean(
                    rule,
                    conf,
                    [
                        conf_training_times,
                        conf_balanced_corpus_validation_times,
                        conf_ground_truth_with_violation_validation_times,
                        conf_total_times,
                    ],
                    output_file
                )

            if '============== Total time for ' in line:
                write_rule_mean(
                    rule,
                    [
                        rule_training_times,
                        rule_balanced_corpus_validation_times,
                        rule_ground_truth_with_violation_validation_times,
                        rule_total_times,
                    ],
                    output_file
                )


def write_size_mean(r, c, s, steps_times, output_file):
    output_file.write(f'{r},{c},{s},mean')

    for step_times in steps_times:
        mean = compute_mean(step_times)
        output_file.write(f',{mean}')
        step_times.clear()

    output_file.write('\n')


def write_conf_mean(r, c, steps_times, output_file):
    output_file.write(f'{r},{c},mean,mean')

    for step_times in steps_times:
        mean = compute_mean(step_times)
        output_file.write(f',{mean}')
        step_times.clear()

    output_file.write('\n')


def write_rule_mean(r, steps_times, output_file):
    output_file.write(f'{r},mean,mean,mean')

    for step_times in steps_times:
        mean = compute_mean(step_times)
        output_file.write(f',{mean}')
        step_times.clear()

    output_file.write('\n')


def compute_mean(times):
    if len(times) == 0:
        return 0

    seconds_sum = sum([convert_time_to_seconds(time) for time in times])
    return round(seconds_sum / len(times))


def convert_time_to_seconds(time):
    hours, minutes, seconds = time.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


if __name__ == '__main__':
    compute_time_stats_from_colab_logs()
