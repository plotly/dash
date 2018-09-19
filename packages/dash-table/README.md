# Dash Spreadsheet 3.0

## Setup

1. Install Node v8+
2. Install CircleCI CLI (https://circleci.com/docs/2.0/local-cli/)

npm install

## Local Server (Hot reload)

npm run build.watch

## Local Build

npm run build:js && npm run build:py

## Run tests locally

npm test

## Run tests locally (Hot reload)

npm run test.watch

## Run tests in CircleCI CLI

circleci build --job test

## Local Dist Build

python setup.py sdist

Note: Distributable file will be located in ./dist