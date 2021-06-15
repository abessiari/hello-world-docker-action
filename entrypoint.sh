#!/bin/sh -l

echo "Hello YES SIR $1"
time=$(date)
echo "::set-output name=time::$time"
