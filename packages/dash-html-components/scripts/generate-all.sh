#!/bin/sh

SCRIPT_DIR=`dirname $0`

node $SCRIPT_DIR/extract-attributes.js
node $SCRIPT_DIR/generate-components.js $SCRIPT_DIR/data/block-elements.txt
node $SCRIPT_DIR/generate-components.js $SCRIPT_DIR/data/inline-elements.txt
node $SCRIPT_DIR/generate-index.js
