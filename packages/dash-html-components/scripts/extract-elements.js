'use strict';

const fs = require('fs');
const cheerio = require('cheerio');
const request = require('request');

const refUrl = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element';
const dataPath = './data/elements.txt';

/**
 * From the MDN HTML elements reference, extract a list of elements.
 */
function extractElements($) {
    const excludeElements = ['html', 'head', 'body', 'style', 'h1–h6'];
    // `<section>` is for some reason missing from the reference tables.
    const addElements = ['section', 'h1', 'h2', 'h3', 'h4','h5', 'h6', 'iframe'];

    return $('td:first-child')
        .toArray()
        .map(el => {
            return cheerio(el).text().replace(/[\<\>]/g, '')
        })
        .reduce((list, element) => {
            const subList = element.split(', ');
            return list.concat(subList);
        }, [])
        .filter(element => excludeElements.indexOf(element) === -1)
        .concat(addElements);
}

request(refUrl, (error, response, html) => {
    if (error) {
        throw error;
    }
    const $ = cheerio.load(html);
    const elements = extractElements($);
    const out = elements.join('\n');

    fs.writeFileSync(dataPath, out);
});
