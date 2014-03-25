#!/bin/sh

./soylentrecipes -OBec.conf.file=../../src/beagle.conf &
pid=$!
sleep 2
kill -9 $pid &&
less beagle.log
