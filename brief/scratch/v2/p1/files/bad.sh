#!/usr/bin/env bash
file=$1
count=$(grep -c ERROR $file)
if [ $count -gt 0 ]
then
  echo "found $count errors in $file"
fi
