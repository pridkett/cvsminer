#!/bin/sh

for x in rhythmbox gtk gimp tomboy glade epiphany; do
	python2.4 guessGrapher.py -p gnome/$x
	python2.4 guessClustering.py -p gnome/$x > gnome_$x.clustering
	cat plots.tmpl | sed -e "s/evolution/$x/g" > tmp.gpi
	gnuplot tmp.gpi
	rm tmp.gpi
done
