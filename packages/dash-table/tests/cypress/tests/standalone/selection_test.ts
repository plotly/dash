import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

Object.values(AppMode).forEach(mode => {
    describe(`select, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('with keyboard', () => {
            beforeEach(() => {
                DashTable.getCell(3, 1).click();
            });

            it('can select down', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(4, 1).should('have.class', 'cell--selected');
            });

            it('can select left', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowLeft}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(3, 0).should('have.class', 'cell--selected');
            });

            it('can select right', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowRight}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(3, 2).should('have.class', 'cell--selected');
            });

            it('can select up', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowUp}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(2, 1).should('have.class', 'cell--selected');
            });

            it('can select down twice', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowDown}`);
                DOM.focused.type(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.getSelectedCells().should('have.length', 3);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(4, 1).should('have.class', 'cell--selected');
                DashTable.getCell(5, 1).should('have.class', 'cell--selected');
            });

            it('can select down then up', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowDown}`);
                DOM.focused.type(`${Key.Shift}${Key.ArrowUp}`);
                DashTable.getSelectedCells().should('have.length', 1);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
            });

            it('can select down then right', () => {
                DOM.focused.type(`${Key.Shift}${Key.ArrowDown}`);
                DOM.focused.type(`${Key.Shift}${Key.ArrowRight}`);
                DashTable.getSelectedCells().should('have.length', 4);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(4, 1).should('have.class', 'cell--selected');
                DashTable.getCell(3, 2).should('have.class', 'cell--selected');
                DashTable.getCell(4, 2).should('have.class', 'cell--selected');
            });
        });

        describe('with mouse', () => {
            it('can select (5, 5)', () => {
                DashTable.getCell(3, 1).click();
                DOM.focused.type(Key.Shift, { release: false });
                DashTable.getCell(5, 3).click();
                DashTable.getSelectedCells().should('have.length', 9);

                for (let row = 3; row <= 5; ++row) {
                    for (let column = 1; column <= 3; ++column) {
                        DashTable.getCell(row, column).should('have.class', 'cell--selected');
                    }
                }
            });

            it('can select 9-10 correctly', () => {
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
            });
        });
    });
});