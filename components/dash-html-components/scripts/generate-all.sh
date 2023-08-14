#!/bin/sh
set -e

SCRIPT_DIR=`dirname $0`

node $SCRIPT_DIR/generate-components.js $SCRIPT_DIR/data/elements.txt
node $SCRIPT_DIR/generate-index.js
