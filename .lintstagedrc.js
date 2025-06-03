// .lintstagedrc.js
const path = require("path");
const fs = require('fs')

// Helper to resolve path to venv executables
const venvBin = (command) => {
    let bin = "bin";
    if (process.platform == "win32") {
        bin = "Scripts";
    }
    if (fs.existsSync("venv")) {
        return path.join("venv", bin, command);
    }
    if (fs.existsSync(".venv")) {
        return path.join(".venv", bin, command);
    }
}

module.exports = {
    // Python checks (run from root, using root venv)
    "*.py": (filenames) => [
        `${venvBin("python")} -m pylint --rcfile=.pylintrc ${filenames.join(
            " "
        )}`, // Add your pylintrc if you have one
        `${venvBin("flake8")} ${filenames.join(" ")}`,
        `${venvBin("black")} --check ${filenames.join(" ")}`,
    ],

    // ESLint and Prettier for 'components/dash-core-components'
    "components/dash-core-components/**/*.{js,jsx,ts,tsx}": (filenames) => {
        const relativeFilePaths = filenames.map((f) =>
            path.relative(path.join("components", "dash-core-components"), f)
        );
        return [
            `cd components/dash-core-components && npx eslint --no-error-on-unmatched-pattern ${relativeFilePaths.join(
                " "
            )}`,
            `cd components/dash-core-components && npx prettier --check ${relativeFilePaths.join(
                " "
            )}`,
        ];
    },

    "components/dash-html-components/**/*.{js,jsx,ts,tsx}": (filenames) => {
        const relativeFilePaths = filenames.map((f) =>
            path.relative(path.join("components", "dash-html-components"), f)
        );
        return [
            `cd components/dash-html-components && npx eslint --no-error-on-unmatched-pattern ${relativeFilePaths.join(
                " "
            )}`,
        ];
    },

    "components/dash-table/**/*.{js,jsx,ts,tsx}": (filenames) => {
        const relativeFilePaths = filenames.map((f) =>
            path.relative(path.join("components", "dash-table"), f)
        );
        return [
            `cd components/dash-table && npx eslint --no-error-on-unmatched-pattern ${relativeFilePaths.join(
                " "
            )}`,
            `cd components/dash-table && npx prettier --check ${relativeFilePaths.join(
                " "
            )}`,
        ];
    },

    "dash/dash-renderer/**/*.{js,jsx,ts,tsx}": (filenames) => {
        const relativeFilePaths = filenames.map((f) =>
            path.relative(path.join("dash", "dash-renderer"), f)
        );
        return [
            `cd dash/dash-renderer && npx eslint --no-error-on-unmatched-pattern ${relativeFilePaths.join(
                " "
            )}`,
            `cd dash/dash-renderer && npx prettier --check ${relativeFilePaths.join(
                " "
            )}`,
        ];
    },
};
