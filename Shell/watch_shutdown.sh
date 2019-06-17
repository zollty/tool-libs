#!/bin/bash
# --------------------------------------
# check lightning-push shutdown status
# --------------------------------------
tail -f ../logs/app.log | while read line
do
a=`echo $line | grep "all app consumer managers shutdown" | wc -l`
if [ $a -gt 0 ];then
  sleep 5
  echo "-----------shutdown ok----------. now can kill tomcat."
  ./catalina.sh stop -force
  exit 0
fi
done
