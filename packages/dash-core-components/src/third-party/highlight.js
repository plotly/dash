import highlightjs from 'highlight.js/lib/highlight';
import '../components/css/highlight.css';

import bash from 'highlight.js/lib/languages/bash';
import css from 'highlight.js/lib/languages/css';
import http from 'highlight.js/lib/languages/http';
import javascript from 'highlight.js/lib/languages/javascript';
import json from 'highlight.js/lib/languages/json';
import markdown from 'highlight.js/lib/languages/markdown';
import python from 'highlight.js/lib/languages/python';
import r from 'highlight.js/lib/languages/r';
import ruby from 'highlight.js/lib/languages/ruby';
import shell from 'highlight.js/lib/languages/shell';
import sql from 'highlight.js/lib/languages/sql';
import xml from 'highlight.js/lib/languages/xml';
import yaml from 'highlight.js/lib/languages/yaml';

highlightjs.registerLanguage('bash', bash);
highlightjs.registerLanguage('css', css);
highlightjs.registerLanguage('http', http);
highlightjs.registerLanguage('javascript', javascript);
highlightjs.registerLanguage('json', json);
highlightjs.registerLanguage('markdown', markdown);
highlightjs.registerLanguage('python', python);
highlightjs.registerLanguage('r', r);
highlightjs.registerLanguage('ruby', ruby);
highlightjs.registerLanguage('shell', shell);
highlightjs.registerLanguage('sql', sql);
highlightjs.registerLanguage('xml', xml);
highlightjs.registerLanguage('yaml', yaml);

export default highlightjs;
