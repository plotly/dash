'use strict';

const fs = require('fs');
const cheerio = require('cheerio');
const request = require('request');

const refUrl = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element';
const dataPath = './data/elements.txt';
const expectedElCount = 131;

/**
 * From the MDN HTML elements reference, extract a list of elements.
 */
function extractElements($) {
    const excludeElements = [
        'html', 'head', 'body', 'style', 'h1–h6', 'input',
        // out of scope, different namespaces - but Mozilla added these to the
        // above reference page Jan 2021 so we need to exclude them now.
        // see https://github.com/mdn/content/pull/410
        'svg', 'math',
        // obsolete, non-standard, or deprecated tags
        'image', 'dir', 'tt', 'applet', 'noembed', 'bgsound', 'menu', 'menuitem',
        'noframes'
    ];
    // `<section>` is for some reason missing from the reference tables.
    const addElements = [
        'base',
        'section',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'iframe'
    ];

    return $('td:first-child')
        .toArray()
        .map(el => {
            return cheerio(el).text().replace(/[<>]/g, '')
        })
        .reduce((list, element) => {
            const subList = element.split(', ');
            return list.concat(subList);
        }, [])
        .filter(element => excludeElements.indexOf(element) === -1)
        .concat(addElements)
        .sort()
        .reduce((list, element) => {
            if(!list.length || element !== list[list.length - 1]) {
                list.push(element);
            }
            return list;
        }, []);
}

request(refUrl, (error, response, html) => {
    if (error) {
        throw error;
    }
    const $ = cheerio.load(html);
    const elements = extractElements($);
    if (elements.length !== expectedElCount) {
        throw new Error(
            'Unexpected number of elements extracted from ' + refUrl +
            ' Check the output and edit expectedElCount if this is intended.'
        );
    }
    const out = elements.join('\n');

    fs.writeFileSync(dataPath, out);
});
