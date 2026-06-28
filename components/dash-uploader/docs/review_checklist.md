# Code Review Checklist

## Code quality & design

-   Is your code clear? If you had to go back to it in a month, would you be happy to? If someone else had to contribute to it, would they be able to?

    A few suggestions:

    -   Make your variable names descriptive and use the same naming conventions throughout the code.

    -   For more complex pieces of logic, consider putting a comment, and maybe an example.

    -   In the comments, focus on describing _why_ the code does what it does, rather than describing _what_ it does. The reader can most likely read the code, but not necessarily understand why it was necessary.

    -   Don't overdo it in the comments. The code should be clear enough to speak for itself. Stale comments that no longer reflect the intent of the code can hurt code comprehension.

*   Don't repeat yourself. Any time you see that the same piece of logic can be applied in multiple places, factor it out into a function, or variable, and reuse that code.
*   Scan your code for expensive operations (large computations, DOM queries, React re-renders). Have you done your possible to limit their impact? If not, it is going to slow your app down.
*   Can you think of cases where your current code will break? How are you handling errors? Should the user see them as notifications? Should your app try to auto-correct them for them?

## Component API

-   Have you tested your component on the Python side by creating an app in `usage.py` ?

    Do all of your component's props work when set from the back-end?

    Should all of them be settable from the back-end or are some only relevant to user interactions in the front-end?

-   Have you provided some basic documentation about your component? The Dash community uses [react docstrings](https://github.com/plotly/dash-docs/blob/master/tutorial/plugins.py#L45) to provide basic information about dash components. Take a look at this [Checklist component example](https://github.com/plotly/dash-core-components/blob/master/src/components/Checklist.react.js) and others from the dash-core-components repository.

    At a minimum, you should describe what your component does, and describe its props and the features they enable.

    Be careful to use the correct formatting for your docstrings for them to be properly recognized.

## Tests

-   The Dash team uses integration tests extensively, and we highly encourage you to write tests for the main functionality of your component. In the `tests` folder of the boilerplate, you can see a sample integration test. By launching it, you will run a sample Dash app in a browser. You can run the test with:
    ```
    python -m tests.test_render
    ```
    [Browse the Dash component code on GitHub for more examples of testing.](https://github.com/plotly/dash-core-components)

## Ready to publish? Final scan

-   Take a last look at the external resources that your component is using. Are all the external resources used [referenced in `MANIFEST.in`](https://github.com/plotly/dash-docs/blob/0b2fd8f892db720a7f3dc1c404b4cff464b5f8d4/tutorial/plugins.py#L55)?

-   [You're ready to publish!](https://github.com/plotly/dash-component-boilerplate/blob/master/%7B%7Bcookiecutter.project_shortname%7D%7D/README.md#create-a-production-build-and-publish)
