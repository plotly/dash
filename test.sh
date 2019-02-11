EXIT_STATE=0

python -m unittest tests.development.test_base_component || EXIT_STATE=$?
python -m unittest tests.development.test_component_loader || EXIT_STATE=$?
python -m unittest tests.test_integration || EXIT_STATE=$?
python -m unittest tests.test_resources || EXIT_STATE=$?
python -m unittest tests.test_configs || EXIT_STATE=$?

pylint dash setup.py --rcfile=$PYLINTRC || EXIT_STATE=$?
pylint tests -d all -e C0410,C0411,C0412,C0413,W0109 || EXIT_STATE=$?
flake8 dash setup.py || EXIT_STATE=$?
flake8 --ignore=E123,E126,E501,E722,E731,F401,F841,W503,W504 --exclude=metadata_test.py tests || EXIT_STATE=$?

if [ $EXIT_STATE -ne 0 ]; then
    echo "One or more tests failed"
else
    echo "All tests passed!"
fi

exit $EXIT_STATE
