interface MathJaxObject {
    typeset: (elements?: (HTMLElement | null)[]) => void;
    config: {startup: {typeset: boolean}};
}

declare global {
    interface Window {
        MathJax?: MathJaxObject;
    }
}

export default (mathjax?: boolean): Promise<MathJaxObject | undefined> =>
    Promise.resolve(
        window.MathJax ||
            (mathjax === false
                ? undefined
                : import(/* webpackChunkName: "mathjax" */ './tex-svg').then(
                      () => window.MathJax
                  ))
    );
