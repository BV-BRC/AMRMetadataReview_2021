#! /bin/bash
#
# run.sh [output_dir] [threads]

REPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
OUTDIR=$(echo $1 | sed 's/\/$//g')
THREAD=$2

if [ ! -d $REPDIR ]; then
	echo "Cannot find repo directory..."
	exit 1
fi

if [ ! -d $OUTDIR ]; then
	mkdir $OUTDIR
fi

cat $REPDIR/tabular/amr.*.filt.tab | cut -f1 -d$'\t' | sort -u > $OUTDIR/gids.lst

