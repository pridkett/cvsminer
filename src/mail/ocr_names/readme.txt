The files in this directory are used for processing and loading all of the
different names that may be in the commit logs. The first step is to run the
following command to get all of names from the logs:

find  /home/ibmocrds/Projects/gnome/data/commit_logs/ -name logs.txt -exec cat {} \; | egrep --color=never "Author:[[:space:]]+.* <.*@.*>" | sed -e "s/Author:[[:space:]]\+\([^[:space:]].*\) <\(.*@.*\)>/\1 :: \2/" | sort | uniq > names.txt

Then run nameimporter.py

This will take care of ensuring that all of the names and emails present in
names.txt have people loaded for them in the database.  In theory this should
make the process of loading mailing lists a little bit easier.
