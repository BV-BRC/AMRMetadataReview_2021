# AMR Metadata Review

This is the repository for the AMR Metadata review.  It includes all the models that were built for the paper as well as the data required to generate the models and steps and scripts on how to download the fasta files from the PATRIC FTP servers.  All models are built using the [Genomic Model Creator](https://github.com/Tinyman392/GenomicModelCreator) repository which will be linked in this repo.  Although command line code will be provided on how to build our models, there is additional information about the model building process in the GenomicModelCreator repo. 

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

Once this is done, the repo is set up.

# Requirements

Although this specific repository doesn't have any specific requirements, the GenomicModelCreator which is used to train the models does have some requirements and tools that are needed for it to run.  

There are some additional python libraries that are needed to run the *buildModel.py* script (installed version are in parenthesis):
- [XGBoost](https://xgboost.readthedocs.io/en/latest/) (v 0.82)
- [Numpy](https://numpy.org) (1.16.5)
- [SciPy](https://www.scipy.org) (1.2.1)
- [SciKit-Learn](https://scikit-learn.org/stable/) (0.20.3)

On top of this, [KMC](http://sun.aei.polsl.pl/REFRESH/index.php?page=projects&project=kmc&subpage=about) is also needed to run the scripts.  Specifically, *kmc* and *kmc_dump* must both be in *PATH*.

Note that the *run.sh* script does require quite a bit of resources to run.  For reference, our machine is has 144 logical cores and 1 TB of RAM.  During testing, utilizing 128 cores the training portion of the script took 2-3 days total to run while using upwards of 128 GB of RAM on the machine.  Besides this, the script requires a total of 220 GB of fasta files to be downloaded used to train with.  An additional 1-2 GB of store is used during training.  In our tests on a machine utilizing 128 of 144 cores and 1 TB of RAM, the total runtime for the script was about 36 hours:
- 5 hours downloading files
- 19 hours to train SIR model
- 12 hours to train MIC model

# Repository Structure

This repository is split up with the following organization:
- Genomic Model Creator : This is an external repository, if you didn't initialize and update the submodules, this directory is empty.  Once the submodules are set up properly, it'll be populated with the GenomicModelCreator python scripts.
- tabular : This directory contains all the tabular files that are used to generate the model
- models : This directory contains the two AMR models generated for the paper
- README.md : This file
- run.sh : Script used to run everything
- getAccBySpc.py : Script used to compute accuracies by species.

# run.sh

This script downloads the fasta files and [*genome_lineage*](ftp://ftp.patricbrc.org/RELEASE_NOTES/genome_lineage) file from the PATRIC FTP and builds the cross-validated SIR and MIC models (the first 5 of 10 total folds are run).  Afterwards, it computes model stats for each model using the *getAccBySpc.py* script.  Note that these models require lots of RAM and compute time to run appropriately.  

```bash
bash PATH/TO/run.sh [output_dir] [threads]
```

The script has two arguments:
- output_dir : output directory to put the results and fasta files.  Example \~/AMRModels_out/
- threads : number of threads to run with.  Don't choose a number higher than the number of cores on your machine!  Example: 128

The download of the 59200 individual fasta files can be very time consuming based on the speed of your internet.  If a fasta file exists in the *[output_dir]/fasta/* directory, the script will not redownload that file.  It is normal for the first initial download to take over 4 hours to run.  Note that the total download size is 220GB!  

The output directory will contain the following:
- fasta : directory containing all fasta files that were downloaded from the PATRIC FTP and used to train with.  This should contain 59200 fasta files totaling 220 GB of data.  
- gids.lst : list of genome IDs used to train with.  This list is also used to download genomes from the PATRIC FTP.  
- model_mic : MIC model directory.
- model_sir : SIR model directory.
- temp : temporary directory used while training.  

For reference with respect to compute requirements: these models were built on a machine that has 144 total logical processors and 1 TB of RAM.  These models still required multiple *days* of training using this server while utilizing upwards of 128 GB of RAM.  In our tests on a machine utilizing 128 of 144 cores and 1 TB of RAM, the total runtime for the script was about 36 hours:
- 5 hours downloading files
- 19 hours to train SIR model
- 12 hours to train MIC model

# GenomicModelCreator Directory

This directory contains the scripts needed to build AMR models for this repository.  Please see the README in the *GenomicModelCreator* directory for more information about this.  

# Tabular Directory

This directory contains all the raw tabular files that were used to generate the models.  It contains 3 files:
- AMR.tbl.v4 : This is the raw file containing all the AMR metadata for each genome.  This file is parsed, cut, and filtered to generate the *amr.mic.filt.tab* and *amr.sir.filt.tab* files.
- amr.mic.filt.tab : This is the file used to train the MIC model.  It is filtered down to just contain all species-antibiotic combinations that have more than 450 samples.  It contains 3 columns: [genome_id, antibiotic:MIC, MIC_value].
- amr.sir.filt.tab : This is the file used to train the SIR model.  It is filtered down to contain all species-antibiotic combinations that have more than 50 samples in S and R.  The file contains 3 columns: [genome_id, antibiotic:breakpoint_def, SIR].

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
