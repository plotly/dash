import { configure, getStorybook, setAddon } from '@storybook/react';

import createPercyAddon from '@percy-io/percy-storybook';
const { percyAddon, serializeStories } = createPercyAddon();
setAddon(percyAddon);

const req = require.context('./../tests/visual/percy-storybook', true, /\.percy\./);
function loadStories() {
    req.keys().forEach(req);
}

configure(loadStories, module);
serializeStories(getStorybook);