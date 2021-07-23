import {expect} from 'chai';

import derivedFragmentStyles from 'dash-table/derived/table/fragmentStyles';

function validate(style, width) {
    expect(style.length).to.equal(2);
    expect(style[0]).to.not.equal(undefined);
    expect(style[1]).to.not.equal(undefined);
    expect(style[0].length).to.equal(2);
    expect(style[1].length).to.equal(2);
    expect(style[0][1]).to.not.equal(undefined);
    expect(style[0][1].fragment).to.not.equal(undefined);
    expect(style[0][1].fragment.marginRight).to.equal(width);
}

describe('fragment styles', () => {
    const cell = {height: 30};
    const headers = [];
    const padding = {before: 0, after: 0};
    const scrollbarWidth = 20;
    const uiViewport = {scrollTop: 0, scrollLeft: 0, height: 0, width: 0};
    const viewport = {data: [], indices: []};

    describe('of "ready" virtualized table', () => {
        it('includes scrollbar width styling', () => {
            const style: any = derivedFragmentStyles(
                true,
                cell,
                headers,
                uiViewport,
                viewport,
                padding,
                scrollbarWidth
            );

            validate(style, scrollbarWidth);
        });
    });

    describe('of "inprogress" virtualized table', () => {
        it('includes scrollbar width styling', () => {
            const style: any = derivedFragmentStyles(
                true,
                undefined,
                undefined,
                undefined,
                viewport,
                padding,
                scrollbarWidth
            );

            validate(style, scrollbarWidth);
        });
    });

    describe('of "ready" non-virtualized table', () => {
        it('includes scrollbar width styling', () => {
            const style: any = derivedFragmentStyles(
                false,
                undefined,
                undefined,
                undefined,
                viewport,
                padding,
                scrollbarWidth
            );

            validate(style, scrollbarWidth);
        });
    });

    describe('of "inprogress" non-virtualized table', () => {
        it('includes scrollbar width styling', () => {
            const style: any = derivedFragmentStyles(
                false,
                undefined,
                undefined,
                undefined,
                viewport,
                padding,
                scrollbarWidth
            );

            validate(style, scrollbarWidth);
        });
    });
});
