#!/bin/sh

./soylentrecipes -OBec.conf.file=beagle.conf &
pid=$!
sleep 2
kill -9 $pid &&
less beagle.log
