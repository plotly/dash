import { configure } from '@storybook/react';

const req = require.context('./../tests/visual/percy-storybook', true, /\.percy\./);
function loadStories() {
    req.keys().forEach(req);
}

configure(loadStories, module);