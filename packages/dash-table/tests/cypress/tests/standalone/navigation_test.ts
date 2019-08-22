import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { BasicModes } from 'demo/AppMode';

Object.values(BasicModes).forEach(mode => {
    describe(`navigate, mode=${mode}`, () => {
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

        describe('with keyboard', () => {
            beforeEach(() => {
                DashTable.getCell(3, 1).click();
            });

            it('can navigate 9-10 selected cells', () => {
                DashTable.getCell(9, 1).click();
                DOM.focused.type(Key.Shift, { release: false });
                DashTable.getCell(10, 1).click();
                DOM.focused.type(Key.Shift, { release: false });
                DashTable.getCell(10, 2).click();

                for (let row = 9; row <= 10; ++row) {
                    for (let column = 1; column <= 2; ++column) {
                        DashTable.getCell(row, column).should('have.class', 'cell--selected');
                    }
                }

                DashTable.getCell(10, 2).should('have.class', 'cell--selected');
                DOM.focused.type(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(9, 1).should('have.class', 'cell--selected');
                DOM.focused.type(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(9, 2).should('have.class', 'cell--selected');
                DOM.focused.type(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(10, 1).should('have.class', 'cell--selected');
                DOM.focused.type(`${Key.Enter}${Key.Enter}`);
                DashTable.getCell(10, 2).should('have.class', 'cell--selected');
            });

            // Issue: https://github.com/plotly/dash-table/issues/49
            it('can move after ctrl+c', () => {
                DOM.focused.type(`${Key.Meta}c`);
                DOM.focused.type(Key.ArrowDown);
                DashTable.getCell(4, 1).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move down', () => {
                DOM.focused.type(Key.ArrowDown);
                DashTable.getCell(4, 1).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move left', () => {
                DOM.focused.type(Key.ArrowLeft);
                DashTable.getCell(3, 0).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can moved right', () => {
                DOM.focused.type(Key.ArrowRight);
                DashTable.getCell(3, 2).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move up', () => {
                DOM.focused.type(Key.ArrowUp);
                DashTable.getCell(2, 1).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can move out of the viewport in virtualized mode', () => {
                DashTable.toggleScroll(true);
                for (let i = 0; i < 25; i++) {
                    DOM.focused.type(Key.ArrowDown);
                }
                DOM.focused.type(Key.ArrowRight);
                DashTable.getCellFromDataDash(28, 2).should('have.class', 'focused');
            });
        });

        describe('with mouse', () => {
            beforeEach(() => {
                DashTable.getCell(3, 1).click();
            });

            it('can select self', () => {
                DOM.focused.click();
                DashTable.getCell(3, 1).should('have.class', 'focused');
            });

            it('can select other', () => {
                DashTable.getCell(4, 2).click();
                DashTable.getCell(4, 2).should('have.class', 'focused');
                DashTable.getCell(3, 1).should('not.have.class', 'focused');
            });

            it('can select a cell and scroll it out of the viewport', () => {
                DashTable.toggleScroll(true);
                DashTable.getCell(4, 2).click();
                DashTable.scrollToBottom();
                DashTable.getCellInLastRowOfColumn(3).click();
                DashTable.getCell(4, 2).should('not.have.class', 'focused');
            });
        });
    });
});