#!/bin/bash
# this script generates matrix files for a set of files

for x in gnome/gedit gnome/evolution gnome/glade gnome/gtk gnome/tomboy; do
    echo "Dumping dynetml for $x"
	python2.4 matrixDependency.py -x --nonew --nodead -p $x --onlysource
    echo "Dumping boring data for $x"
	python2.4 matrixDependency.py --nonew --nodead -p $x --onlysource
done
