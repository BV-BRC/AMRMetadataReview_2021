#! /bin/bash
#
# run.sh [output_dir] [threads]

# check arguments, output help if improper
if [ $# -lt 2 ]; then
	echo "run.sh [output_dir] [threads]"
	exit 1
fi

# get the repo directory, output directory, and thread count
# clean up the repo and output directories to not have ending '/'
REPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
OUTDIR=$(echo $1 | sed 's/\/$//g')
THREAD=$2

# make sure repo directory exists
# it probably should
if [ ! -d $REPDIR ]; then
	echo "Cannot find repo directory..."
	exit 2
fi

# if output directory doesn't exist, make it
if [ ! -d $OUTDIR ]; then
	mkdir $OUTDIR
fi

###
# Get genome ID list
###

# get list of all genome IDs, and output to a file in the output
# directory
cat $REPDIR/tabular/amr.*.filt.tab | cut -f1 -d$'\t' | sort -u > $OUTDIR/gids.lst

###
# Download fasta files
###

# if fasta directory doesn't exist in the output directory, make it
if [ ! -d $OUTDIR/fasta ]; then
	mkdir $OUTDIR/fasta
fi

# for each genome ID
# check to see if fasta file exists for genome ID
# if not, download it, if so, skip
for i in $(cat $OUTDIR/gids.lst); do
	if [ ! -f $OUTDIR/fasta/$i.fasta ]; then
		echo "downloading $i fasta"
		wget -q ftp://ftp.patricbrc.org/genomes/$i/$i.fna -O $OUTDIR/fasta/$i.fasta
	else
		echo "already have $i fasta"
	fi
done

echo python $REPDIR/GenomicModelCreator/buildModel.py

