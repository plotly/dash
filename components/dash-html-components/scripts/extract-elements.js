'use strict';

const fs = require('fs');
const cheerio = require('cheerio');
const request = require('request');

const refUrl = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element';
const dataPath = './data/elements.txt';
const expectedElCount = 125;

/**
 * From the MDN HTML elements reference, extract a list of elements.
 */
function extractElements($) {
    const excludeElements = [
        'html', 'head', 'body', 'style', 'h1–h6', 'input', 'search',
        // out of scope, different namespaces - but Mozilla added these to the
        // above reference page Jan 2021 so we need to exclude them now.
        // see https://github.com/mdn/content/pull/410
        'svg', 'math',
        // obsolete, non-standard, or deprecated tags
        'image', 'dir', 'tt', 'applet', 'noembed', 'bgsound', 'menu', 'menuitem',
        'noframes',
        // experimental, don't add yet
        'portal'
    ];
    // `<section>` is for some reason missing from the reference tables.
    const addElements = [
        'base',
        'basefont',
        'blink',
        'keygen',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'hgroup',
        'iframe',
        'section',
        'spacer',
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
        console.error(error);
        process.exit(-1);
    }
    const $ = cheerio.load(html);
    const elements = extractElements($);
    if (elements.length !== expectedElCount) {
        try {
            const prevEls = fs.readFileSync(dataPath, 'utf8').split('\n');
            const added = elements.filter(n => prevEls.indexOf(n) === -1);
            const removed = prevEls.filter(n => elements.indexOf(n) === -1);

            console.error(
                'Found new elements not seen before: [' + added.join(',') +
                '] and did not find expected elements: [' + removed.join(',') + ']'
            );
        }
        catch(e) {
            console.log('no previous elements found');
            console.log(e);
        }
        console.error(
            'Unexpected number of elements extracted from ' + refUrl +
            ' - Found ' + elements.length + ' but expected ' + expectedElCount +
            ' Check the output and edit expectedElCount if this is intended.'
        );
        process.exit(-1);
    }
    const out = elements.join('\n');

    fs.writeFileSync(dataPath, out);
});
