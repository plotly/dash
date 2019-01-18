EXIT_STATE=0

python -m unittest tests.development.test_base_component || EXIT_STATE=$?
python -m unittest tests.development.test_component_loader || EXIT_STATE=$?
python -m unittest tests.test_integration || EXIT_STATE=$?
python -m unittest tests.test_resources || EXIT_STATE=$?
python -m unittest tests.test_configs || EXIT_STATE=$?

if [ $EXIT_STATE -ne 0 ]; then
    echo "One or more tests failed"
else
    echo "All tests passed!"
fi

exit $EXIT_STATE
