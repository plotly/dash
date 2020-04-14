import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';

import { BasicModes } from 'demo/AppMode';

Object.values(BasicModes).forEach(mode => {
    describe(`select, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('with keyboard', () => {
            beforeEach(() => {
                DashTable.clickCell(3, 1);
            });

            it('can select down', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(4, 1).should('have.class', 'cell--selected');
            });

            it('can select left', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowLeft}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(3, 0).should('have.class', 'cell--selected');
            });

            it('can select right', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowRight}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(3, 2).should('have.class', 'cell--selected');
            });

            it('can select up', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowUp}`);
                DashTable.getSelectedCells().should('have.length', 2);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(2, 1).should('have.class', 'cell--selected');
            });

            it('can select down twice', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.focusedType(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.getSelectedCells().should('have.length', 3);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(4, 1).should('have.class', 'cell--selected');
                DashTable.getCell(5, 1).should('have.class', 'cell--selected');
            });

            it('can select down then up', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.focusedType(`${Key.Shift}${Key.ArrowUp}`);
                DashTable.getSelectedCells().should('have.length', 1);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
            });

            it('can select down then right', () => {
                DashTable.focusedType(`${Key.Shift}${Key.ArrowDown}`);
                DashTable.focusedType(`${Key.Shift}${Key.ArrowRight}`);
                DashTable.getSelectedCells().should('have.length', 4);
                DashTable.getCell(3, 1).should('have.class', 'cell--selected');
                DashTable.getCell(4, 1).should('have.class', 'cell--selected');
                DashTable.getCell(3, 2).should('have.class', 'cell--selected');
                DashTable.getCell(4, 2).should('have.class', 'cell--selected');
            });
        });

        describe('with mouse', () => {
            it('can select (5, 5)', () => {
                DashTable.clickCell(3, 1);
                DashTable.focusedType(Key.Shift, { release: false });
                DashTable.clickCell(5, 3);
                DashTable.getSelectedCells().should('have.length', 9);

                for (let row = 3; row <= 5; ++row) {
                    for (let column = 1; column <= 3; ++column) {
                        DashTable.getCell(row, column).should('have.class', 'cell--selected');
                    }
                }
            });

            it('can select 9-10 correctly', () => {
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
            });
        });
    });
});