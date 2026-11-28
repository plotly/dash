import type {PluggableList} from 'unified';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkMathEscapedDollar from './remarkMathEscapedDollar';
import rehypeRaw from 'rehype-raw';

import rehypeBlockCode from './rehypeBlockCode';
import rehypeDashMath from './rehypeDashMath';
import rehypeDccComponents from './rehypeDccComponents';
import rehypeLinkTarget from './rehypeLinkTarget';
import rehypeStripTags from './rehypeStripTags';

// remark plugin for GitHub Flavored Markdown: tables, strikethrough,
// task lists, autolinks, etc.
export const remarkGfmPlugins: PluggableList = [remarkGfm];

// Parse Markdown math and keep escaped dollars inside math expressions.
export const remarkMathPlugins: PluggableList = [
    remarkMath,
    remarkMathEscapedDollar,
];

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

// Always last, so they also see elements that rehype-raw parsed from raw HTML.
export const rehypeBlockCodePlugins: PluggableList = [rehypeBlockCode];
export const linkTargetPlugins = (target: string): PluggableList => [
    [rehypeLinkTarget, target],
];
