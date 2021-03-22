import {expect} from 'chai';

import {derivedPartialDataEdges} from 'dash-table/derived/edges/data';
import Environment from 'core/environment';
import {IConvertedStyle} from 'dash-table/derived/style';

const converter: Omit<IConvertedStyle, 'style'> = {
    checksColumn: () => false,
    checksDataRow: () => false,
    checksFilter: () => false,
    checksHeaderRow: () => false,
    checksState: () => false,
    checksStateActive: () => false,
    checksStateSelected: () => false,
    matchesActive: () => true,
    matchesColumn: () => true,
    matchesDataRow: () => true,
    matchesFilter: () => true,
    matchesHeaderRow: () => true,
    matchesSelected: () => true
};

describe('data edges', () => {
    const edgesFn = derivedPartialDataEdges();

    it('without data has no edges', () => {
        const res = edgesFn(
            [{id: 'id', name: 'id'}],
            [],
            [],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.equal(undefined);
    });

    it('without one data row', () => {
        const res = edgesFn([], [], [{id: 1}], {columns: 0, rows: 0}, false);

        expect(res).to.equal(undefined);
    });

    it('uses `undefined` default style', () => {
        const res = edgesFn(
            [{id: 'id', name: 'id'}],
            [],
            [{id: 1}],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.not.equal(undefined);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(2);
            expect(horizontal[0].length).to.equal(1);
            expect(horizontal[1].length).to.equal(1);
            expect(horizontal[0][0]).to.equal(Environment.defaultEdge);
            expect(horizontal[1][0]).to.equal(Environment.defaultEdge);

            expect(vertical.length).to.equal(1);
            expect(vertical[0].length).to.equal(2);
            expect(vertical[0][0]).to.equal(Environment.defaultEdge);
            expect(vertical[0][1]).to.equal(Environment.defaultEdge);
        }
    });

    it('uses default style', () => {
        const res = edgesFn(
            [{id: 'id', name: 'id'}],
            [],
            [{id: 1}],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.not.equal(undefined);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(2);
            expect(horizontal[0].length).to.equal(1);
            expect(horizontal[1].length).to.equal(1);
            expect(horizontal[0][0]).to.equal(Environment.defaultEdge);
            expect(horizontal[1][0]).to.equal(Environment.defaultEdge);

            expect(vertical.length).to.equal(1);
            expect(vertical[0].length).to.equal(2);
            expect(vertical[0][0]).to.equal(Environment.defaultEdge);
            expect(vertical[0][1]).to.equal(Environment.defaultEdge);
        }
    });

    it('uses default style on multiple rows & columns', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [],
            [
                {id: 1, name: 'a'},
                {id: 1, name: 'b'},
                {id: 2, name: 'a'},
                {id: 2, name: 'b'}
            ],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.not.equal(undefined);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(5);
            horizontal.forEach(edges => {
                expect(edges.length).to.equal(2);

                edges.forEach(edge => {
                    expect(edge).to.equal(Environment.defaultEdge);
                });
            });

            expect(vertical.length).to.equal(4);
            vertical.forEach(edges => {
                expect(edges.length).to.equal(3);

                edges.forEach(edge => {
                    expect(edge).to.equal(Environment.defaultEdge);
                });
            });
        }
    });

    it('applies `border`', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [
                {
                    style: {border: '1px solid green'},
                    ...converter
                }
            ],
            [
                {id: 1, name: 'a'},
                {id: 1, name: 'b'},
                {id: 2, name: 'a'},
                {id: 2, name: 'b'}
            ],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.not.equal(undefined);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(5);
            horizontal.forEach(edges => {
                expect(edges.length).to.equal(2);

                edges.forEach(edge => {
                    expect(edge).to.equal('1px solid green');
                });
            });

            expect(vertical.length).to.equal(4);
            vertical.forEach(edges => {
                expect(edges.length).to.equal(3);

                edges.forEach(edge => {
                    expect(edge).to.equal('1px solid green');
                });
            });
        }
    });

    it('applies `borderLeft` and `borderTop`', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [
                {
                    style: {
                        borderLeft: '1px solid green',
                        borderTop: '1px solid darkgreen'
                    },
                    ...converter
                }
            ],
            [
                {id: 1, name: 'a'},
                {id: 1, name: 'b'},
                {id: 2, name: 'a'},
                {id: 2, name: 'b'}
            ],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.not.equal(undefined);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(5);
            horizontal.forEach((edges, rowIndex) => {
                expect(edges.length).to.equal(2);

                edges.forEach(edge => {
                    expect(edge).to.equal(
                        rowIndex === horizontal.length - 1
                            ? Environment.defaultEdge
                            : '1px solid darkgreen'
                    );
                });
            });

            expect(vertical.length).to.equal(4);
            vertical.forEach(edges => {
                expect(edges.length).to.equal(3);

                edges.forEach((edge, index) => {
                    expect(edge).to.equal(
                        index === edges.length - 1
                            ? Environment.defaultEdge
                            : '1px solid green'
                    );
                });
            });
        }
    });

    it('applies `borderLeft` overridden by higher precedence `borderRight`', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [
                {
                    style: {borderLeft: '1px solid green'},
                    ...converter
                },
                {
                    style: {borderRight: '1px solid darkgreen'},
                    ...converter
                }
            ],
            [{id: 1, name: 'a'}],
            {columns: 0, rows: 0},
            false
        );

        expect(res).to.not.equal(undefined);
        if (res) {
            const {vertical} = res.getEdges();

            expect(vertical.length).to.equal(1);
            expect(vertical[0].length).to.equal(3);
            expect(vertical[0][0]).to.equal('1px solid green');
            expect(vertical[0][1]).to.equal('1px solid darkgreen');
            expect(vertical[0][2]).to.equal('1px solid darkgreen');
        }
    });

    it('applies `borderLeft` not overridden by lower precedence `borderRight`', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [
                {
                    style: {borderRight: '1px solid darkgreen'},
                    ...converter
                },
                {
                    style: {borderLeft: '1px solid green'},
                    ...converter
                }
            ],
            [{id: 1, name: 'a'}],
            {columns: 0, rows: 0},
            false
        );

        expect(res === undefined).to.equal(false);
        if (res) {
            const {vertical} = res.getEdges();

            expect(vertical.length).to.equal(1);
            expect(vertical[0].length).to.equal(3);
            expect(vertical[0][0]).to.equal('1px solid green');
            expect(vertical[0][1]).to.equal('1px solid green');
            expect(vertical[0][2]).to.equal('1px solid darkgreen');
        }
    });

    it('applies `borderLeft` overridden by higher precedence `border`', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [
                {
                    style: {borderLeft: '1px solid darkgreen'},
                    ...converter
                },
                {
                    style: {border: '1px solid green'},
                    ...converter
                }
            ],
            [{id: 1, name: 'a'}],
            {columns: 0, rows: 0},
            false
        );

        expect(res !== undefined).to.equal(true);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(2);
            horizontal.forEach(edges => {
                expect(edges.length).to.equal(2);

                edges.forEach(edge => {
                    expect(edge).to.equal('1px solid green');
                });
            });

            expect(vertical.length).to.equal(1);
            vertical.forEach(edges => {
                expect(edges.length).to.equal(3);

                edges.forEach(edge => {
                    expect(edge).to.equal('1px solid green');
                });
            });
        }
    });

    it('applies `border` overridden by higher precedence `borderLeft`', () => {
        const res = edgesFn(
            [
                {id: 'id', name: 'id'},
                {id: 'name', name: 'name'}
            ],
            [
                {
                    style: {border: '1px solid green'},
                    ...converter
                },
                {
                    style: {borderLeft: '1px solid darkgreen'},
                    ...converter
                }
            ],
            [{id: 1, name: 'a'}],
            {columns: 0, rows: 0},
            false
        );

        expect(res !== undefined).to.equal(true);
        if (res) {
            const {horizontal, vertical} = res.getEdges();

            expect(horizontal.length).to.equal(2);
            horizontal.forEach(edges => {
                expect(edges.length).to.equal(2);

                edges.forEach(edge => {
                    expect(edge).to.equal('1px solid green');
                });
            });

            expect(vertical.length).to.equal(1);
            vertical.forEach(edges => {
                expect(edges.length).to.equal(3);

                edges.forEach((edge, j) => {
                    expect(edge).to.equal(
                        j + 1 === edges.length
                            ? '1px solid green'
                            : '1px solid darkgreen'
                    );
                });
            });
        }
    });
});
