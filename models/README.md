# Models Directory

This directory contains 2 folders, each with a similar structure:
- model_mic_d16 : MIC model
- model_sir_d16 : SIR model

Each model directory structure consists of the following:
- all : this directory contains the individual folds that were trained.  For this paper, the first 5 folds of a 10-fold CV were trained.  Additionally, it contains the labels and predictions for each fold and training history for each fold.  Additionally, statistical tabular files exist in here as well.
- model.attrOrder : order of features for the feature vector
- model.genomes.list : list of genome IDs used to train the model
- model.labels.map : mapping of labels to numeric value (used for non-AMR models)
- model.params : parameter hash used to train the model
- model.stats.* : sets of files generated to compute stats by species
- temp.txt : temporary output used during debugging
- weights.list : list of weights in order that were used

Note that the randomization seed isn't set in GenomicModelCreator, so the model outputs will not match the output of shown here 100%, they should be within the confidence intervals though for the statistic files in the *all* directories.
