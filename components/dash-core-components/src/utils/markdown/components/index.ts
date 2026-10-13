import type {Components} from 'react-markdown';

import CodeRenderer from './Code';
import DccLinkRenderer from './DccLink';
import DccMarkdownRenderer from './DccMarkdown';
import MathJaxRenderer from './MathJax';

export const components: Components = {
    dcclink: DccLinkRenderer,
    dccmarkdown: DccMarkdownRenderer,
    dashmathjax: MathJaxRenderer,
    code: CodeRenderer,
};
