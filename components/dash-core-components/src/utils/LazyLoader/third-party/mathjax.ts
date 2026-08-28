interface MathJaxObject {
    typeset: (elements?: (HTMLElement | null)[]) => void;
    config: {startup: {typeset: boolean}};
}

declare global {
    interface Window {
        MathJax?: MathJaxObject;
    }
}

export default function lazyLoadMathJax(
    mathjax?: boolean
): Promise<MathJaxObject | undefined> {
    return Promise.resolve(
        window.MathJax ||
            (mathjax === false
                ? undefined
                : import(/* webpackChunkName: "mathjax" */ './tex-svg').then(
                      () => window.MathJax
                  ))
    );
}
