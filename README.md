# AMR Metadata Review

This is the repository for the AMR Metadata review.  It includes all the models that were built for the paper as well as the data required to generate the models and steps and scripts on how to download the fasta files required to download the data from the PATRIC FTP servers.  All models are built using the [Genomic Model Creator](https://github.com/Tinyman392/GenomicModelCreator) repository which will be linked in this repo.  Although command line code will be provided on how to build our models, there is additional information about the model building process in the GenomicModelCreator repo. 

# Setup

 

# Tabular Directory

This directory contains all the raw tabular files that were used to generate the models.  It contains 3 files:
- AMR.tbl.v4 : This is the raw file containing all the AMR metadata for each genome.  This file is parsed, cut, and filtered to generate the *amr.mic.filt.tab* and *amr.sir.filt.tab* files.
- amr.mic.filt.tab : This is the file used to train the MIC model.  It is filtered down to just contain all species-antibiotic combinations that have more than 450 samples.  It contains 3 columns: [genome_id, antibiotic:MIC, MIC_value].
- amr.sir.filt.tab : This is the file used to train the SIR model.  It is filtered down to contain all species-antibiotic combinations that have more than 50 samples in S and R.  The file contains 3 columns: [genome_id, antibiotic:breakpoint_def, SIR].


