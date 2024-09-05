import cssProperties from './cssProperties';

export type StyleProperty = string | number;

export const toCamelCase = (fragments: string[]) =>
    fragments
        .map((f, i) => (i ? f.charAt(0).toUpperCase() + f.substring(1) : f))
        .join('');

const toKebabCase = (fragments: string[]) => fragments.join('-');
const toSnakeCase = (fragments: string[]) => fragments.join('_');

const camels: string[] = [];
const entries: [string, string][] = [];

cssProperties.forEach(prop => {
    const camel = toCamelCase(prop);

    camels.push(camel);

    entries.push([camel, camel]);
    entries.push([toKebabCase(prop), camel]);
    entries.push([toSnakeCase(prop), camel]);
});

export default new Map<string, string>(entries);

export const KnownCssProperties = camels;
