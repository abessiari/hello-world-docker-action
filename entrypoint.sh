#!/bin/sh -l

echo "Hello PATH SIR $1"
time=$(date)
echo "::set-output name=time::$time"
