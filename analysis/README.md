# Analysis

This directory contains the two R scripts used to process the results from the learning phase:
- `results.R` Used to generate the following outputs:
    - Plots for the scores obtained by the classifiers according to the number of lines used for training, grouped by
ratio
    - Mann-Whitney p-values and rank-biserial correlation scores obtained for the analysis of precision
    - Number of rules where the median precision of classifiers is greater than P for each size and ratio
- `stats.R` Used to generate the plot of the number of non-compliant examples, with ratio, per rule.
