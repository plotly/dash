import {expect} from 'chai';
import * as R from 'ramda';

import SyntaxTree from 'core/syntax-tree';

import {
    QuerySyntaxTree,
    MultiColumnsSyntaxTree,
    SingleColumnSyntaxTree
} from 'dash-table/syntax-tree';

export interface ICase {
    name: string;
    query: string;
    target: object;
    valid: boolean;
    evaluate?: boolean;
}

export function processCases(
    getSyntaxer: (query: string) => SyntaxTree,
    cases: ICase[]
) {
    R.forEach(
        c =>
            it(c.name, () => {
                const tree = getSyntaxer(c.query);

                expect(tree.isValid).to.equal(c.valid);
                if (!c.valid) {
                    return;
                }

                expect(tree.evaluate(c.target)).to.equal(c.evaluate);
            }),
        cases
    );
}
const getQuerySyntaxTree = (query: string): any => new QuerySyntaxTree(query);
const getMultiColumnSyntaxTree = (query: string): any =>
    new MultiColumnsSyntaxTree(query);
const getSingleColumnSyntaxTree = (query: string): any =>
    new SingleColumnSyntaxTree(query, {
        id: 'a'
    });

describe('Dash Table Queries', () => {
    R.forEach(
        c => {
            describe(c.name, () => {
                describe('relational operator', () => {
                    describe('eq', () => {
                        processCases(c.syntaxer, [
                            {
                                name: 'compares "1" to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1.0" to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: '1.0'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1.0" to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: '1.0'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to 1.0',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to "1.0"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1.0"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1.1" to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1.0`,
                                target: {a: '1.1'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "1.1" to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: '1.1'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "1" to 0x1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 0x1`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to "0x1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "0x1"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },

                            {
                                name: 'compares 1 to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: 1},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares 1 to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: 1},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares 1.1 to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: 1.1},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares 1.1 to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: 1.1},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares 1 to 0x1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 0x1`,
                                target: {a: 1},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares 1 to "0x1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "0x1"`,
                                target: {a: 1},
                                valid: true,
                                evaluate: true
                            },

                            {
                                name: 'compares "x1" to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: 'x1'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "x1" to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: 'x1'},
                                valid: true,
                                evaluate: false
                            },

                            {
                                name: 'compares "1x" to 1',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1`,
                                target: {a: '1x'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "1x" to "1"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1"`,
                                target: {a: '1x'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares 1 to 1x',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1x`,
                                target: {a: 1},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares 1 to "1x"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1x"`,
                                target: {a: 1},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "1" to 1x',
                                query: `${c.hideOperand ? '' : '{a} '}eq 1x`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "1" to "1x"',
                                query: `${c.hideOperand ? '' : '{a} '}eq "1x"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: false
                            },

                            {
                                name: 'compares "1" to " 1 "',
                                query: `${c.hideOperand ? '' : '{a} '}eq " 1 "`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to "\t1\t"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }eq "\t1\t"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to "\r\n1\r\n"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }eq "\r\n1\r\n"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "\t1\t" to "\r\n1\r\n"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }eq "\r\n1\r\n"`,
                                target: {a: '\t1\t'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "\r\n1\r\n" to "\t1\t"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }eq "\t1\t"`,
                                target: {a: '\r\n1\r\n'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: "compare 'abc' to 'ABC' (insensitive)",
                                query: `${c.hideOperand ? '' : '{a} '}ieq ABC`,
                                target: {a: 'abc'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: "compare 'abc' to 'ABC' (sensitive)",
                                query: `${c.hideOperand ? '' : '{a} '}seq ABC`,
                                target: {a: 'abc'},
                                valid: true,
                                evaluate: false
                            }
                        ]);
                    });

                    describe('contains', () => {
                        processCases(c.syntaxer, [
                            {
                                name: 'compares "11" to 1',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains 1`,
                                target: {a: '11'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'insensitive compares "abc" to A',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }icontains A`,
                                target: {a: 'abc'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'cannot compare 11 to 1',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains 1`,
                                target: {a: 11},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "11" to "1"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "1"`,
                                target: {a: '11'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares 11 to "1"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "1"`,
                                target: {a: 11},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "1" to "1.0"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "1.0"`,
                                target: {a: '1'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares 1 to "1.0"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "1.0"`,
                                target: {a: 1},
                                valid: true,
                                evaluate: false
                            },

                            {
                                name: 'compares "abc" to "b"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "b"`,
                                target: {a: 'abc'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "abc" to " b"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains " b"`,
                                target: {a: 'abc'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "abc" to "b "',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "b "`,
                                target: {a: 'abc'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'compares "a bc" to " b"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains " b"`,
                                target: {a: 'a bc'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'compares "ab c" to "b "',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }contains "b "`,
                                target: {a: 'ab c'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: "compare 'ab c' to 'B' (insensitive)",
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }icontains B`,
                                target: {a: 'ab c'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: "compare 'ab c' to 'b' (insensitive)",
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }icontains b`,
                                target: {a: 'ab c'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: "compare 'ab c' to 'B' (sensitive)",
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }scontains B`,
                                target: {a: 'ab c'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: "compare 'ab c' to 'b' (sensitive)",
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }scontains b`,
                                target: {a: 'ab c'},
                                valid: true,
                                evaluate: true
                            }
                        ]);
                    });

                    describe('datestartswith', () => {
                        processCases(c.syntaxer, [
                            {
                                name: '0yyy in "0"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "0"`,
                                target: {a: '0987'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: '0 in "0yyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "0987"`,
                                target: {a: '0'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: '0yyy in "0yyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "0987"`,
                                target: {a: '0987'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2006"`,
                                target: {a: '2005'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy in yyyy',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005`,
                                target: {a: '2005'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01-01'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01-01T10'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01-01T10:00'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01-01 10:00:00'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxx in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01-01 10:00:00.000'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxxxxxxxx in "yyyy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005"`,
                                target: {a: '2005-01-01 10:00:00.000000000'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm in "yyyy-mm"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2005-01"`,
                                target: {a: '2005-01'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01-01'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01-01T10'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01-01T10:00'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01-01 10:00:00'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxx in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01-01 10:00:00.000'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxxxxxxxx in yyyy-mm',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01`,
                                target: {a: '2005-01-01 10:00:00.000000000'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxx in yyyy-mm-ddThh:mm:ss.xxx',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T10:00:00.000`,
                                target: {a: '2005-01-01 10:00:00.000'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxx in yyyy-mm-ddThh:mm:ss.xxx000',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T10:00:00.000000`,
                                target: {a: '2005-01-01 10:00:00.000'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.xxx in yyyy-mm-ddThh:mm:ss.xxx111',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T10:00:00.000111`,
                                target: {a: '2005-01-01 10:00:00.000'},
                                valid: true,
                                evaluate: false
                            },

                            {
                                name: 'yyyy-01 in yyyy-02',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-02`,
                                target: {a: '2005-01'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm-01 in yyyy-mm-02',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-02`,
                                target: {a: '2005-01-01'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm-dd 00 in yyyy-mm-dd 01',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T01`,
                                target: {a: '2005-01-01 00'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm-dd hh:00 in yyyy-mm-dd hh:01',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T00:01`,
                                target: {a: '2005-01-01 00:00'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:00 in yyyy-mm-dd hh:mm:01',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T00:00:01`,
                                target: {a: '2005-01-01 00:00:00'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yyyy-mm-dd hh:mm:ss.000 in yyyy-mm-dd hh:mm:ss.001',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith 2005-01-01T00:00:00.001`,
                                target: {a: '2005-01-01 00:00:00.000'},
                                valid: true,
                                evaluate: false
                            },

                            {
                                name: '20yy in "yy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "19"`,
                                target: {a: '2019'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: '19yy in "yy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "19"`,
                                target: {a: '1919'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yy in "19yy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "1999"`,
                                target: {a: '99'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yy in "20yy"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "2099"`,
                                target: {a: '99'},
                                valid: true,
                                evaluate: false
                            },
                            {
                                name: 'yy in yy',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "79"`,
                                target: {a: '79'},
                                valid: true,
                                evaluate: true
                            },
                            {
                                name: 'yy in YY"',
                                query: `${
                                    c.hideOperand ? '' : '{a} '
                                }datestartswith "79"`,
                                target: {a: '78'},
                                valid: true,
                                evaluate: false
                            }
                        ]);
                    });
                });
            });
        },
        [
            {name: 'Query Syntax Tree', syntaxer: getQuerySyntaxTree},
            {
                name: 'Multi Columns Syntax Tree',
                syntaxer: getMultiColumnSyntaxTree
            },
            {
                name: 'Single Column Syntax Tree',
                syntaxer: getSingleColumnSyntaxTree,
                hideOperand: true
            }
        ]
    );
});
