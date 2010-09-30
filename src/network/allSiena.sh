#!/bin/bash

for x in gnome/f-spot gnome/evolution gnome/rhythmbox gnome/glade gnome/evince gnome/beagle; do
	NF=$(echo $x | sed -e 's/\//_/')
	echo $NF

	rm -rf $NF*
	python2.4 sienaNetworks.py -l debug -w 32 -o 4 -p $x --onlyagents --binary --startdate 20010101 --stopdate 20050501
	python2.4 exportSienaNetworks.py $NF-*.dynetml -l debug
done

# now package and compress the files
./zipDat.sh
