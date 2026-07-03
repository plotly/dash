'use strict';

const fs = require('fs');
const cheerio = require('cheerio');

const refUrl = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element';
const dataPath = './data/elements.txt';

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
        'portal',
        'fencedframe',
        'selectedcontent',
        // not a real HTML element (Geolocation API). MDN lists it with an
        // "Experimental" badge, so it only stays excluded if the badge text is
        // stripped from the cell first (see the first-line/trim normalization
        // in the map below).
        'geolocation',
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
            // Cell text can include an "Experimental"/"Deprecated" badge on a
            // following line (e.g. "geolocation \nExperimental\n"). Keep only the
            // element name from the first line and trim surrounding whitespace so
            // the exclusions above match regardless of badge formatting.
            return cheerio(el).text().replace(/[<>]/g, '').split('\n')[0].trim();
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

fetch(refUrl)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        const $ = cheerio.load(html);
        const elements = extractElements($);
        const out = elements.join('\n');

        fs.writeFileSync(dataPath, out);
    })
    .catch(error => {
        console.error(error);
        process.exit(-1);
    });
