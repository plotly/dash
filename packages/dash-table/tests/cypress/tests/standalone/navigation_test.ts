import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';

import { BasicModes, AppMode } from 'demo/AppMode';

Object.values([...BasicModes, AppMode.Markdown, AppMode.MixedMarkdown]).forEach(mode => {
    describe(`navigate-1, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        it('does not change column width', () => {
            DashTable.getCell(3, 1).then(startCell => {
                const startWidth = startCell.outerWidth();

                DashTable.getCell(3, 1).then(endCell => {
                    const endWidth = endCell.outerWidth();

                    expect(endWidth).to.equal(startWidth);
                });
            });
        });

        describe('with mouse', () => {
            beforeEach(() => {
                DashTable.clickCell(3, 1);
            });

            it('can select self', () => {
                DashTable.clickCell(3, 1);
                DashTable.getCell(3, 1).should('have.class', 'focused');
            });

            it('can select other', () => {
                DashTable.clickCell(4, 2);
                DashTable.getCell(4, 2).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can select a cell and scroll it out of the viewport', () => {
                DashTable.toggleScroll(true);
                DashTable.clickCell(4, 2);
                DashTable.scrollToBottom();
                DashTable.getCellInLastRowOfColumn(3).click();
                DashTable.getCell(4, 2).should('not.have.class', 'focused');
            });
        });
    });
});

Object.values(BasicModes).forEach(mode => {
    describe(`navigate-2, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('with keyboard', () => {
            beforeEach(() => {
                DashTable.clickCell(3, 1);
            });

            it('can navigate 9-10 selected cells', () => {
                DashTable.clickCell(9, 1);
                DashTable.focusedType(Key.Shift, { release: false });
                DashTable.clickCell(10, 1);
                DashTable.focusedType(Key.Shift, { release: false });
                DashTable.clickCell(10, 2);

                for (let row = 9; row <= 10; ++row) {
                    for (let column = 1; column <= 2; ++column) {
                        DashTable.getCell(row, column).should('have.class', 'cell--selected');
                    }
                }

                DashTable.getCell(10, 2).should('have.class', 'cell--selected');
                DashTable.focusedType(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(9, 1).should('have.class', 'cell--selected');
                DashTable.focusedType(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(9, 2).should('have.class', 'cell--selected');
                DashTable.focusedType(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(10, 1).should('have.class', 'cell--selected');
                DashTable.focusedType(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(10, 2).should('have.class', 'cell--selected');
            });

            // Issue: https://github.com/plotly/dash-table/issues/49
            it('can move after ctrl+c', () => {
                DashTable.focusedType(`${Key.Meta}c`);
                DashTable.focusedType(Key.ArrowDown);
                DashTable.getCell(4, 1).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move down', () => {
                DashTable.focusedType(Key.ArrowDown);
                DashTable.getCell(4, 1).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move left', () => {
                DashTable.focusedType(Key.ArrowLeft);
                DashTable.getCell(3, 0).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move right', () => {
                DashTable.focusedType(Key.ArrowRight);
                DashTable.getCell(3, 2).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move up', () => {
                DashTable.focusedType(Key.ArrowUp);
                DashTable.getCell(2, 1).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move out of the viewport in virtualized mode', () => {
                DashTable.toggleScroll(true);
                for (let i = 0; i < 25; i++) {
                    DashTable.focusedType(Key.ArrowDown);
                }
                DashTable.focusedType(Key.ArrowRight);
                DashTable.getCellFromDataDash(28, 2).should('have.class', 'focused');
            });
        });
    });
});
