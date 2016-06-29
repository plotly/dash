const fs = require('fs');
const cheerio = require('cheerio');
const request = require('request');

const htmlURL = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes';

/**
 * From the MDN attributes reference, extract a map of attributes with
 * descriptions and supported elements.
 */
function extractAttributes($) {
    const $table = $('#Attribute_list').next('table');
    const attributes = {};

    $table.find('tbody tr').each((i, row) => {
        const $children = cheerio(row).find('td');
        const attribute = $children.eq(0).text();
        const elements = $children.eq(1).text()
            .replace(/[\<\>\s]/g, '')
            .split(',');
        const description = $children.eq(2).text()
            .replace(/\n/g, '')
            .trim();

        attributes[attribute] = {
            elements,
            description
        };
    });

    return attributes;
}

/**
 * Create a map of elements to attributes e.g. {div: ['id', 'name']}
 */
function extractElements(attributes) {
    return Object.keys(attributes)
        .reduce((elementMap, attributeName) => {
            const attribute = attributes[attributeName];
            const elements = attribute.elements;

            elements.forEach((element) => {
                elementMap[element] = elementMap[element] || [];
                elementMap[element].push(attributeName);
            });

            return elementMap;
        }, {});
}

// A local copy of the MDN attributes web page has been saved for reference:
// fs.readFile('./data/attributes.html', 'utf-8', (error, html) => {
request(htmlURL, (error, response, html) => {
    if (error) {
        throw error;
    }
    const $ = cheerio.load(html);
    const attributes = extractAttributes($);
    const elements = extractElements(attributes);
    const out = {
        attributes,
        elements
    };

    fs.writeFileSync('./attributes.json', JSON.stringify(out));
});

