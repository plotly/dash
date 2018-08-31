#!/usr/bin/env bash

pyversion="$(python -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')"

if [ "$pyversion" -ge "37" ]; then
    exit $(black dash --check)
else
    exit 0
fi