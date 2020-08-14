import SyntaxTree from 'core/syntax-tree';

import queryLexicon from './lexicon/query';

export default class QuerySyntaxTree extends SyntaxTree {
    constructor(query: string) {
        super(queryLexicon, query);
    }
}
