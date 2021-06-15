#!/bin/sh -l

echo "Hello NO SIR $1"
time=$(date)
echo "::set-output name=time::$time"
