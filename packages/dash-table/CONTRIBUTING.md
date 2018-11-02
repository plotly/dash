## Setup
1. Install Python 3.x (python 3 is required to run the demo apps and tests)
2. Install Node v8+
3. Install CircleCI CLI (https://circleci.com/docs/2.0/local-cli/)

`npm install`

## Local Demo
#### Local Server JS Example (Hot reload)
Use to verify the frontend functionality of the table during development or initial testing. This will run the example in the `/demo` directory.

1. Run `npm run build.watch`
2. Visit [http://localhost:8080/](http://localhost:8080/)
#### Local Server Review Apps
Use the review apps to verify callback functionality (note these examples are written in Python: the end-user syntax). This will run `index.py` found in the root of the directory and run the examples found in: `/tests/dash/`. To add more examples create a `.py` file in the `/tests/dash/` directory prepended with `app_` ie: `app_your_example.py`. This example will automatically get added to the example index page.
1. We recommend creating a virtual enviornment to install the requirements and run the examples. Create a virtual env with `virtualenv venv` and run with: `source venv/bin/activate`.
2. Run `pip install -r requirements.txt` from the root of the directory to install the requirements.
3. From the root of the directory run `gunicorn index:server`
4. Visit [http://127.0.0.1:8000](http://localhost:8000)

## Running Tests
#### Run tests locally
`npm test`
#### Run tests locally with hot reload:
`npm run test.watch`
#### Run tests in CircleCI CLI
`circleci build --job test`

## Local Build
`npm run build:js && npm run build:py`

## Local Dist Build
`python setup.py sdist`

Note: Distributable file will be located in ./dist
