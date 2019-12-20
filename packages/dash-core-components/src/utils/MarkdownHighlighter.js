import lazyhljs from './LazyLoader/hljs';

const MarkdownHighlighter = {
    loadhljs: async function() {
        this.hljs = await lazyhljs();
        this.hljsResolve();
        this.isReady = true;
    },
};

const isReady = new Promise(resolve => {
    MarkdownHighlighter.hljsResolve = resolve;
});

MarkdownHighlighter.isReady = isReady;

export default MarkdownHighlighter;
