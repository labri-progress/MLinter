library(ggplot2)
library(readr)

options(scipen=999)

stats_file <- 'ratio.csv'
output_folder <- 'output'

total_numbers_of_line <- 33213474

seed <- 18112022

stats_df <- read_csv(
  stats_file,
  col_types = list(
    rule = col_character(),
    line_number = col_integer(),
    line_violation_number = col_integer(),
    line_ratio = col_double()
  )
)

rules_to_display <- c('quotes', 'eqeqeq', 'no-floating-decimal')

data <- data.frame(rule = stats_df$rule, number = stats_df$line_violation_number)

plot <- ggplot(data, aes(x = c('rule'), y = number)) +
  geom_jitter(
    aes(colour = ifelse(rule %in% rules_to_display, 'blue', '')),
    position = position_jitter(seed = seed)
  ) +
  geom_text(
    aes(label = ifelse(rule %in% rules_to_display, rule, '')),
    position = position_jitter(seed = seed),
    size = 3,
    vjust = 1.5,
    hjust = 0
  ) +
  xlab('') +
  scale_x_discrete(labels = NULL, breaks = NULL) +
  scale_y_continuous(
    'Number of non-compliant examples',
    trans = 'log1p',
    breaks = c(1000, 10000, 100000, 1000000, 4000000),
    limits = c(1000, 4000000),
    labels = c('1k', '10k', '100k', '1m', '4m'),
    sec.axis = sec_axis(
      ~ . / total_numbers_of_line * 100,
      name = 'Ratio of non-compliant examples',
      breaks = c(0.003, 0.03, 0.3, 1, 6, 12),
      labels = c('0.003', '0.03', '0.3', '1', '6', '12')
    )
  ) +
  guides(colour = 'none') +
  theme_light()

ggsave('violation_and_base_rate.png', plot=plot, path=output_folder, device='png', width = 1400, height = 1000, units = 'px')
