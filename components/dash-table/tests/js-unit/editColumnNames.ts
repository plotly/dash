import {expect} from 'chai';

import {changeColumnHeader} from 'dash-table/utils/actions';

describe('changeColumnHeader', () => {
    const columns = [
        {id: 'rows', type: 'numeric', name: 'rows', renamable: true},
        {
            id: 'aaaa',
            type: 'numeric',
            name: ['City', 'Canada', 'Toronto'],
            renamable: true
        },
        {
            id: 'bbbb',
            type: 'numeric',
            name: ['City', 'Canada', 'Montreal'],
            renamable: true
        },
        {
            id: 'cccc',
            type: 'numeric',
            name: ['City', 'America', 'Boston'],
            renamable: true
        },
        {
            id: 'dddd',
            type: 'numeric',
            name: ['', 'America', 'New York'],
            renamable: true
        }
    ];
    describe('merge_duplicate_headers = false', () => {
        const merge_duplicate_headers = false;

        it('change a header name with column names as array, name[1] of column[1] should be AAA', () => {
            const column = {
                id: 'aaaa',
                type: 'numeric',
                name: ['City', 'Canada', 'Toronto'],
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                1,
                merge_duplicate_headers,
                'AAA'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: 'rows',
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'AAA', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
        it('change a header name with column names as string, column[0] name should be array and name[0] should be BBB', () => {
            const column = {
                id: 'rows',
                type: 'numeric',
                name: 'rows',
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                0,
                merge_duplicate_headers,
                'BBB'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: ['BBB', 'rows', 'rows'],
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
        it('change a header name with column names as string, column[3] name should be array and name[2] should be CCC', () => {
            const column = {
                id: 'cccc',
                type: 'numeric',
                name: ['City', 'America', 'Boston'],
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                2,
                merge_duplicate_headers,
                'CCC'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: 'rows',
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'CCC'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
    });

    describe('merge_duplicate_headers = true', () => {
        const merge_duplicate_headers = true;

        it('change a header name with column names as array, all City should change to Ville', () => {
            const column = {
                id: 'aaaa',
                type: 'numeric',
                name: ['City', 'Canada', 'Toronto'],
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                0,
                merge_duplicate_headers,
                'Ville'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: 'rows',
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['Ville', 'Canada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['Ville', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['Ville', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
        it('change a header name with column names as array, all Canada should change to Kanada', () => {
            const column = {
                id: 'aaaa',
                type: 'numeric',
                name: ['City', 'Canada', 'Toronto'],
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                1,
                merge_duplicate_headers,
                'Kanada'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: 'rows',
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'Kanada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Kanada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
        it('change a header name with column names as array, New York should change to Maui', () => {
            const column = {
                id: 'dddd',
                type: 'numeric',
                name: ['', 'America', 'New York'],
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                2,
                merge_duplicate_headers,
                'Maui'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: 'rows',
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'Maui'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
        it('change a header name with column names as string, column[0] name should be [City, rows, rows ]', () => {
            const column = {
                id: 'rows',
                type: 'numeric',
                name: 'rows',
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                0,
                merge_duplicate_headers,
                'City'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: ['City', 'rows', 'rows'],
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
        it('change a header name with column names as string, column[0] name should be [rows, ABC, rows ]', () => {
            const column = {
                id: 'rows',
                type: 'numeric',
                name: 'rows',
                renamable: true
            };
            const returnColumn = changeColumnHeader(
                column,
                columns,
                1,
                merge_duplicate_headers,
                'ABC'
            );
            const expectedColumn = {
                columns: [
                    {
                        id: 'rows',
                        type: 'numeric',
                        name: ['rows', 'ABC', 'rows'],
                        renamable: true
                    },
                    {
                        id: 'aaaa',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Toronto'],
                        renamable: true
                    },
                    {
                        id: 'bbbb',
                        type: 'numeric',
                        name: ['City', 'Canada', 'Montreal'],
                        renamable: true
                    },
                    {
                        id: 'cccc',
                        type: 'numeric',
                        name: ['City', 'America', 'Boston'],
                        renamable: true
                    },
                    {
                        id: 'dddd',
                        type: 'numeric',
                        name: ['', 'America', 'New York'],
                        renamable: true
                    }
                ]
            };
            expect(expectedColumn).to.deep.equal(returnColumn);
        });
    });
});
