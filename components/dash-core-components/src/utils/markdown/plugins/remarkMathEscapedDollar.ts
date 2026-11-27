import type {Processor} from 'unified';
import type {Code, Construct, Extension, State} from 'micromark-util-types';
import {math} from 'micromark-extension-math';

const DOLLAR = '$'.charCodeAt(0);
const BACKSLASH = '\\'.charCodeAt(0);
const ORDINARY_CHAR = 'A'.charCodeAt(0);

const original = math().text?.[DOLLAR] as Construct;

// Let remark-math parse normally, except escaped dollars inside math.
export default function remarkMathEscapedDollar(this: Processor) {
    // eslint-disable-next-line no-invalid-this
    const data = this.data() as {micromarkExtensions?: Extension[]};

    (data.micromarkExtensions ||= []).push({
        text: {
            36: {
                ...original,
                tokenize(effects, ok, nok) {
                    let slashes = 0;
                    let changed = false;
                    let mapped = false;
                    let finished = false;

                    const proxy = {
                        ...effects,
                        consume(code: Code) {
                            effects.consume(mapped ? DOLLAR : code);
                        },
                    };
                    const success = (code: Code) => {
                        finished = true;
                        return (changed ? ok : nok)(code);
                    };
                    const failure = (code: Code) => {
                        finished = true;
                        return nok(code);
                    };

                    let state = original.tokenize.call(
                        this,
                        proxy,
                        success,
                        failure
                    );

                    function next(code: Code): State | undefined {
                        mapped = code === DOLLAR && slashes % 2 === 1;
                        if (mapped) {
                            changed = true;
                        }

                        // Treat escaped '$' as ordinary text while
                        // consuming the original character.
                        state = state(mapped ? ORDINARY_CHAR : code);
                        slashes = code === BACKSLASH ? slashes + 1 : 0;
                        mapped = false;

                        return finished ? state : next;
                    }

                    return next;
                },
            },
        },
    });
}
