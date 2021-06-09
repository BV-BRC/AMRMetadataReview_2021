# AMR Metadata Review

This is the repository for the AMR Metadata review.  It includes all the models that were built for the paper as well as the data required to generate the models and steps and scripts on how to download the fasta files required to download the data from the PATRIC FTP servers.  All models are built using the [Genomic Model Creator](https://github.com/Tinyman392/GenomicModelCreator) repository which will be linked in this repo.  Although command line code will be provided on how to build our models, there is additional information about the model building process in the GenomicModelCreator repo. 

# Setup

This repository includes another repository within it, so you must set that up when you clone this repository.  Cloning this repository is relatively straightforward:

```bash
git clone https://github.com/Tinyman392/AMRMetadataReview_2021
```

After cloning the repository, you'll want to go into the repo's directory then initialize the submodules (other repo).

```bash
cd AMRMetadataReview_2021
git submodule init
git submodule update
```

After doing this the repo is set up.  

# Repository Setup

This repository is split up with the following organization:
- Genomic Model Creator : This is an external repository, if you didn't initialize and update the submodules, this directory is empty.  Once the submodules are set up properly, it'll be populated with the GenomicModelCreator python scripts.
- tabular : This directory contains all the tabular files that are used to generate the model
- README.md : This file
- run.sh : Script used to run everything

# run.sh

This script downloads the fasta files from the PATRIC FTP and builds models.  Note that these models are very large and require lots of RAM and compute time to run appropriately.  

```bash
run.sh [PATH/TO/REPO] [output_dir] [threads]
```

The script has two arguments:
- PATH/TO/REPO : location of the repo on the machine.  Example: \~/AMRMetadataReview_2021/
- output_dir : output directory to put the results and fasta files.  Example \~/AMRModels_out/
- threads : number of threads to run with.  Don't choose a number higher than the number of cores on your machine!  Example: 128

For reference with respect to compute requirements: these models were built on a machine that has 144 total logical processors and 1 TB of RAM.  These models still required multiple days of training using this server.  

# Tabular Directory

This directory contains all the raw tabular files that were used to generate the models.  It contains 3 files:
- AMR.tbl.v4 : This is the raw file containing all the AMR metadata for each genome.  This file is parsed, cut, and filtered to generate the *amr.mic.filt.tab* and *amr.sir.filt.tab* files.
- amr.mic.filt.tab : This is the file used to train the MIC model.  It is filtered down to just contain all species-antibiotic combinations that have more than 450 samples.  It contains 3 columns: [genome_id, antibiotic:MIC, MIC_value].
- amr.sir.filt.tab : This is the file used to train the SIR model.  It is filtered down to contain all species-antibiotic combinations that have more than 50 samples in S and R.  The file contains 3 columns: [genome_id, antibiotic:breakpoint_def, SIR].


