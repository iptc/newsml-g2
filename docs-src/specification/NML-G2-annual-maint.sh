#!/bin/sh
# This is a comment
cd ./_includes/chapters
for i in *
do
    export i
    echo "Processing ... file $i"
    `sed -I "" -f ../../sed-script $i`
    sleep 1
done
