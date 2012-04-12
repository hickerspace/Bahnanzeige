#!/bin/bash

if [ "$1" == "-f" ]
then
	tail -n 100 -f debug.log | perl -pe 's/^.*?\* .*?$/\e[1;31m$&\e[0m/g'
else
	cat debug.log | perl -pe 's/^.*?\* .*?$/\e[1;31m$&\e[0m/g' | less -R +G
fi

