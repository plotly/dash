import type {PluggableList} from 'unified';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeRaw from 'rehype-raw';

import rehypeDashMath from './rehypeDashMath';
import rehypeDccComponents from './rehypeDccComponents';
import rehypeStripTags from './rehypeStripTags';

// remark plugin for GitHub Flavored Markdown: tables, strikethrough,
// task lists, autolinks, etc.
export const remarkGfmPlugins: PluggableList = [remarkGfm];

// remark plugin for the `mathjax` prop: remark-math parses `$...$`/`$$...$$` in
// Markdown at the token level, so it leaves `\$` and `&#36;` as literal dollars.
export const remarkMathPlugins: PluggableList = [remarkMath];

// rehype plugin for the `mathjax` prop: routes both Markdown and raw-HTML math
// into <dashmathjax>. Must run before rehype-raw.
export const rehypeMathPlugins: PluggableList = [rehypeDashMath];

// rehype pipeline that powers raw-HTML support for `dangerously_allow_html`.
// Order matters: rehype-raw must come first.
export const rawHtmlPlugins: PluggableList = [
    rehypeRaw,
    rehypeStripTags,
    rehypeDccComponents,
];
