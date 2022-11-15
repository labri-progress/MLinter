library(effectsize)
library(ggplot2)
library(readr)

input_folder <- '/Users/clatappy/Documents/Thèse/MLinter/221021/results/22:11:06/'
output_folder <- '/Users/clatappy/Documents/Thèse/MLinter/221021/analysis'

validation_methods <- c('balanced_corpus', 'ground_truth_with_violation')
confs <- c(0, 0.5, 1)
sizes <- c(10, 100, 1000)

get_all_rules <- function() {
  files <- list.files(path=input_folder, pattern="*.csv", full.names=FALSE, recursive=FALSE)

  for (file in files)
  {
    file_split <- unlist(strsplit(file, '_'))
    rule <- file_split[1]
    rules <- c(rules, rule)
  }

  return(unique(rules))
}

generate_plot <- function(path, method, data_df) {
  size <- rep(sapply(data_df$size, toString), 3)
  conf <- rep(sapply(data_df$conf, function(c) ifelse(c == 0, 'VR', ifelse(c == 0.5, 'VFR', 'VF'))), 3)
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
    theme(axis.title.y=element_blank())

  dir.create(path, recursive=TRUE, showWarnings=FALSE)
  file <- paste(method, '_scores.png', sep='')
  ggsave(file, plot=plot, path=path, device='png', width=1500, height=1400, units='px')
}

compute_MWU_test <- function(path, data_df) {
  indices_comparison <- list(c(1, 2), c(2, 3), c(1, 3))

  conf_comparison_df = data.frame(matrix(ncol=5, nrow=0))
  names(conf_comparison_df) <- c('size', 'conf1', 'conf2', 'p-value', 'effect_size')
  for (size_ in sizes) {
    for (indices in indices_comparison) {
      conf_x <- confs[indices[[1]]]
      conf_y <- confs[indices[[2]]]
      x <- subset(data_df, conf == conf_x & size == size_)$precision
      y <- subset(data_df, conf == conf_y & size == size_)$precision

      t <- wilcox.test(x, y)
      e <- rank_biserial(x, y)
      
      conf_comparison_df[nrow(conf_comparison_df) + 1,] <- c(size_, conf_x, conf_y, t['p.value'], e$r_rank_biserial)
    }
  }
  file <- paste(path, '_conf.csv', sep='')
  write.csv(conf_comparison_df, file=file, row.names=FALSE)
  
  size_comparison_df = data.frame(matrix(ncol=5, nrow=0))
  names(size_comparison_df) <- c('conf', 'size1', 'size2', 'p-value', 'effect_size')
  for (conf_ in confs) {
    for (indices in indices_comparison) {
      size_x <- sizes[indices[[1]]]
      size_y <- sizes[indices[[2]]]
      x <- subset(data_df, size == size_x & conf == conf_)$precision
      y <- subset(data_df, size == size_y & conf == conf_)$precision
      
      t <- wilcox.test(x, y)
      e <- rank_biserial(x, y)
      
      size_comparison_df[nrow(size_comparison_df) + 1,] <- c(conf_, size_x, size_y, t['p.value'], e$r_rank_biserial)
    }
  }
  file <- paste(path, '_size.csv', sep='')
  write.csv(size_comparison_df, file=file, row.names=FALSE)
}

rules <- get_all_rules()

for (method in validation_methods) {
  print(method)
  all_data <- data.frame()

  for (rule in rules) {
    rule_data_file_path <- paste(input_folder, rule, '_', method, '.csv', sep='')
    rule_data <- read_csv(rule_data_file_path, show_col_types=FALSE)
    rule_data <- cbind(rule = rep(rule, nrow(rule_data)), rule_data)
    all_data <- rbind(all_data, rule_data)
  }

  generate_plot(output_folder, method, all_data)
  
  print(paste('median accuracy', median(all_data$accuracy)), sep=': ')
  print(paste('median precision', median(all_data$precision)), sep=': ')
  print(paste('median recall', median(all_data$recall)), sep=': ')
  for (conf_ in confs) {
    for (size_ in sizes) {
      data_for_conf_and_size <- subset(all_data, size == size_ & conf == conf_)

      print(paste(size_, conf_, sep=' '))
      print(paste('median accuracy', median(data_for_conf_and_size$accuracy)), sep=': ')
      print(paste('median precision', median(data_for_conf_and_size$precision)), sep=': ')
      print(paste('median recall', median(data_for_conf_and_size$recall)), sep=': ')
 
      number_of_rule_with_precision_median_upper_80 <- 0
      number_of_rule_with_precision_median_upper_95 <- 0
      for (rule_ in rules) {
        rule_data_for_conf_and_size <- subset(data_for_conf_and_size, rule == rule_)
        
        rule_median_for_conf_and_size <- median(rule_data_for_conf_and_size$precision)
        if (rule_median_for_conf_and_size >= 0.8) {
          number_of_rule_with_precision_median_upper_80 <- number_of_rule_with_precision_median_upper_80 + 1
        }
        if (rule_median_for_conf_and_size >= 0.95) {
          number_of_rule_with_precision_median_upper_95 <- number_of_rule_with_precision_median_upper_95 + 1
        }
      }
      print(paste('Number rule with median precision >= 0.8 ', number_of_rule_with_precision_median_upper_80, sep=': '))
      print(paste('Number rule with median precision >= 0.95 ', number_of_rule_with_precision_median_upper_95, sep=': '))
    }
  }

  path <- file.path(output_folder, method)
  compute_MWU_test(path, all_data)
}
