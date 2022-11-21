library(effectsize)
library(ggplot2)
library(readr)

input_folder <- 'results/'
output_folder <- 'output'

validation_methods <- c('balanced_corpus', 'ground_truth_with_violation')
confs <- c(0, 0.5, 1)
sizes <- c(10, 100, 1000)

bonferonni_value <- 3

get_all_rules <- function() {
  rules <- c()
  files <- list.files(path=input_folder, pattern="*.csv", full.names=FALSE, recursive=FALSE)

  for (file in files) {
    file_split <- unlist(strsplit(file, '_'))
    rule <- file_split[1]
    rules <- c(rules, rule)
  }

  return(unique(rules))
}

generate_plot <- function(path, data_df) {
  size <- rep(sapply(data_df$size, toString), 3)
  conf <- rep(sapply(data_df$conf, function(c) ifelse(c == 0, 'VE', ifelse(c == 0.5, 'VFE', 'VF'))), 3)
  measure <- c(rep('precision', nrow(data_df)), rep('recall', nrow(data_df)), rep('accuracy', nrow(data_df)))
  score <- c(data_df$precision, data_df$recall, data_df$accuracy)

  plot_df <- data.frame(size, conf, measure, score)

  plot <- ggplot(plot_df, aes(x=size, y=score, fill=measure)) +
    geom_boxplot() +
    facet_wrap(~conf, ncol=1) +
    xlab('size') +
    ylab('') +
    scale_fill_manual(values=c("#AAAAAA", "#DDDDDD", "#FFFFFF")) +
    scale_y_continuous(breaks=seq(0, 1, 0.2), limits=c(0, 1)) +
    geom_hline(yintercept=0.8, color='red', linetype='dashed') +
    theme_light() +
    theme(axis.title.y=element_blank(), legend.position='top')

  ggsave('plot_scores.png', plot=plot, path=path, device='png', width=1500, height=1400, units='px')
}

compute_stats_test <- function(path, data_df) {
  indices_comparison <- list(c(1, 2), c(2, 3), c(1, 3))

  conf_comparison_df = data.frame(matrix(ncol=4, nrow=0))
  names(conf_comparison_df) <- c('conf1', 'conf2', 'p-value', 'effect_size')
  for (indices in indices_comparison) {
    conf_x <- confs[indices[[1]]]
    conf_y <- confs[indices[[2]]]
    x <- subset(data_df, conf == conf_x)$precision
    y <- subset(data_df, conf == conf_y)$precision

    t <- wilcox.test(x, y)
    p <- as.double(t['p.value']) / bonferonni_value
    e <- rank_biserial(x, y)
    conf_comparison_df[nrow(conf_comparison_df) + 1,] <- c(conf_x, conf_y, p, e$r_rank_biserial)
  }
  file <- file.path(path, 'stats_test_conf.csv')
  write.csv(conf_comparison_df, file=file, row.names=FALSE)
  
  size_comparison_df = data.frame(matrix(ncol=4, nrow=0))
  names(size_comparison_df) <- c('size1', 'size2', 'p-value', 'effect_size')
  for (indices in indices_comparison) {
    size_x <- sizes[indices[[1]]]
    size_y <- sizes[indices[[2]]]
    x <- subset(data_df, size == size_x)$precision
    y <- subset(data_df, size == size_y)$precision
    
    t <- wilcox.test(x, y)
    p <- as.double(t['p.value']) / bonferonni_value
    e <- rank_biserial(x, y)
    size_comparison_df[nrow(size_comparison_df) + 1,] <- c(size_x, size_y, p, e$r_rank_biserial)
  }
  file <- file.path(path, 'stats_test_size.csv')
  write.csv(size_comparison_df, file=file, row.names=FALSE)
}

compute_rules_precision_median_upper_threshold <- function(path, data_df, threshold) {
  upper_threshold = data.frame(matrix(ncol=3, nrow=0))
  names(upper_threshold) <- c('size', 'conf', 'count')

  for (size_ in sizes) {
    for (conf_ in confs) {
      data_for_conf_and_size <- subset(all_data, size == size_ & conf == conf_)
      
      number_of_rule_with_precision_median_upper_threshold <- 0
      for (rule_ in rules) {
        rule_data_for_conf_and_size <- subset(data_for_conf_and_size, rule == rule_)
        
        rule_median_for_conf_and_size <- median(rule_data_for_conf_and_size$precision)
        if (rule_median_for_conf_and_size >= threshold) {
          number_of_rule_with_precision_median_upper_threshold <- number_of_rule_with_precision_median_upper_threshold + 1
        }
      }
      
      upper_threshold[nrow(upper_threshold) + 1,] <- c(size_, conf_, number_of_rule_with_precision_median_upper_threshold)
    }
  }
  
  file <- file.path(path, paste('upper_threshold_', threshold, '.csv', sep=''))
  write.csv(upper_threshold, file=file, row.names=FALSE)
}

compute_scores_median <- function(path, data_df) {
  scores_median = data.frame(matrix(ncol=5, nrow=0))
  names(scores_median) <- c('size', 'conf', 'accuracy', 'precision', 'recall')

  scores_median[nrow(scores_median) + 1,] <- c(
    'all',
    'all',
    median(all_data$accuracy),
    median(all_data$precision),
    median(all_data$recall)
  )
  
  for (size_ in sizes) {
    data_for_size <- subset(all_data, size == size_)
    
    scores_median[nrow(scores_median) + 1,] <- c(
      size_,
      'all',
      median(data_for_size$accuracy),
      median(data_for_size$precision),
      median(data_for_size$recall)
    )
  }
  
  for (conf_ in confs) {
    data_for_conf <- subset(all_data, conf == conf_)
    
    scores_median[nrow(scores_median) + 1,] <- c(
      'all',
      conf_,
      median(data_for_conf$accuracy),
      median(data_for_conf$precision),
      median(data_for_conf$recall)
    )
  }
  
  for (size_ in sizes) {
    for (conf_ in confs) {
      data_for_conf_and_size <- subset(all_data, size == size_ & conf == conf_)
      
      scores_median[nrow(scores_median) + 1,] <- c(
        size_,
        conf_,
        median(data_for_conf_and_size$accuracy),
        median(data_for_conf_and_size$precision),
        median(data_for_conf_and_size$recall)
      )
    }
  }
  
  file <- file.path(path, paste('scores_median.csv', sep=''))
  write.csv(scores_median, file=file, row.names=FALSE)
}

rules <- get_all_rules()

for (method in validation_methods) {
  method_output_folder = file.path(output_folder, method)
  dir.create(method_output_folder, recursive=TRUE, showWarnings=FALSE)
  
  all_data <- data.frame()

  for (rule in rules) {
    rule_data_file_path <- paste(input_folder, rule, '_', method, '.csv', sep='')
    rule_data <- read_csv(rule_data_file_path, show_col_types=FALSE)
    rule_data <- cbind(rule = rep(rule, nrow(rule_data)), rule_data)
    all_data <- rbind(all_data, rule_data)
  }

  generate_plot(method_output_folder, all_data)
  
  compute_stats_test(method_output_folder, all_data)

  compute_rules_precision_median_upper_threshold(method_output_folder, all_data, 0.8)
  compute_rules_precision_median_upper_threshold(method_output_folder, all_data, 0.95)

  compute_scores_median(method_output_folder, all_data)
}
