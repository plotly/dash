#!/bin/bash
file=./build/dash_renderer.min.js
if [ ! -f "$file" ]; then
    echo "dash-renderer did not build correctly"
    exit 1
fi
