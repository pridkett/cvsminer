#!/bin/bash

#
# this is a simple script that renames and places the networks created by the
# allSiena.sh script.
#

OUTDIR="sienaNetworks"

if [ -d ${OUTDIR} ]; then
  rm -rf ${OUTDIR}
fi

mkdir ${OUTDIR}
for x in gnome/f-spot gnome/evolution gnome/rhythmbox gnome/glade gnome/evince gnome/beagle; do
	NF=$(echo $x | sed -e 's/\//_/')
	mkdir ${OUTDIR}/$NF
	mkdir ${OUTDIR}/$NF/code
	mkdir ${OUTDIR}/$NF/code/all
	mkdir ${OUTDIR}/$NF/code/minimal
	mkdir ${OUTDIR}/$NF/mail
	mkdir ${OUTDIR}/$NF/mail/all
	mkdir ${OUTDIR}/$NF/mail/minimal

	CTR=0
	for x in $(ls -t $NF-mail-all*dev-dev.dat); do
		let CTR=$CTR+1
		OUTFILE=n$(printf "%02d" $CTR).dat
		cp $x ${OUTDIR}/$NF/mail/all/${OUTFILE}
	done

	CTR=0
	for x in $(ls -t $NF-mail*mail-dev-dev.dat); do
		let CTR=$CTR+1
		OUTFILE=n$(printf "%02d" $CTR).dat
		cp $x ${OUTDIR}/$NF/mail/minimal/${OUTFILE}
	done

	CTR=0
	for x in $(ls -t $NF-*.code-all-dev-dev.dat); do
		let CTR=$CTR+1
		OUTFILE=n$(printf "%02d" $CTR).dat
		cp $x ${OUTDIR}/$NF/code/all/${OUTFILE}
	done

	CTR=0
	for x in $(ls -t $NF-*.code-dev-dev.dat); do
		let CTR=$CTR+1
		OUTFILE=n$(printf "%02d" $CTR).dat
		cp $x ${OUTDIR}/$NF/code/minimal/${OUTFILE}
	done

done

tar -czvf ${OUTDIR}.tar.gz ${OUTDIR}
