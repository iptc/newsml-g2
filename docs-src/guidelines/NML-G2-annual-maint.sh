#!/bin/sh
#  NML-G2-annual-maint.sh
#  Creates a copy of Guidelines Chapters and Code Examples with schema references,
#  standard version, catalog refs and all dates and versions indexed to the next version of the Guidelines.
#  How to use:
#  1.  Use 'git pull' to create or update your local copy of the newsml-g2-guidelines project
#  2.  Create a new branch in the 'newsml-g2-guidelines' project (locally)
#  3.  Edit the file 'sed-script' in the project home folder
#      Change the version numbers and dates to be consistent with the existing
#      and new version. For example the line:
#        s/NewsML-G2, version 2.28/NewsML-G2, version 2.29/
#      would be changed to:
#        s/NewsML-G2, version 2.29/NewsML-G2, version 2.30/
#  4.  Run this shell script in a Bash shell in the project home folder
#  5.  Check it worked OK using "git diff"
#  6.  download the latest NewsML-G2 Schema into the GuidelinesCodeExamples
#      folder and remove the previous schema
#  7.  Run the asciidoctor script to generate a new index.html file
#  8.  use "git add..." to add the new schema to the tracked files
#  9.  use "git commit -a -m"comments...." to commit all changes
#  10. Push the new branch to the GitHub repo.
#  11. On GitHub, open a Pull Request based on the new branch
#
#  NML-G2-annual-maint.sh
#
#  Created by Kelvin Holland on 23/08/2018.
#  
cd ./_includes/GuidelinesChapters
for i in *
    do
        export i
        echo "Processing ... file $i"
        sed -f ../../sed-script -I "" "$i"
        sleep 1
    done
cd ../GuidelinesCodeExamples
for i in *
    do
        export i
        echo "Processing ... file $i"
        sed -f ../../sed-script -I "" "$i"
        sleep 1
    done
