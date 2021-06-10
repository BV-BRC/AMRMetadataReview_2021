#! /bin/bash
#
# run.sh [output_dir] [threads]

if [ $# -lt 2 ]; then
	echo "run.sh [output_dir] [threads]"
	exit 1
fi

REPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
OUTDIR=$(echo $1 | sed 's/\/$//g')
THREAD=$2

if [ ! -d $REPDIR ]; then
	echo "Cannot find repo directory..."
	exit 2
fi

if [ ! -d $OUTDIR ]; then
	mkdir $OUTDIR
fi

cat $REPDIR/tabular/amr.*.filt.tab | cut -f1 -d$'\t' | sort -u > $OUTDIR/gids.lst

if [ ! -d $OUTDIR/fasta ]; then
	mkdir $OUTDIR/fasta
fi

for i in $(cat $OUTDIR/gids.lst); do
	if [ ! -f $OUTDIR/fasta/$i.fasta ]; then
		echo "downloading $i fasta"
		wget -q ftp://ftp.patricbrc.org/genomes/$i/$i.fna -O $OUTDIR/fasta/$i.fasta
	else
		echo "already have $i fasta"
	fi
done