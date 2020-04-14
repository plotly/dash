import * as R from 'ramda';

import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

Object.values([AppMode.ReadOnly, AppMode.SomeReadOnly]).forEach(mode => {
    describe(`navigate (readonly), mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('with keyboard', () => {
            beforeEach(() => {
                DashTable.clickCell(3, 1);
            });

            // Note: Dropdown cell is a label when readonly. Making a special
            // version of the test for the read only table.
            describe('into a dropdown cell', () => {
                beforeEach(() => {
                    DashTable.clickCellById(3, 'ggg');
                });

                it('can move', () => {
                    R.forEach(() => {
                        DashTable.focusedType(Key.ArrowRight);

                        DashTable.getCellById(3, 'bbb').should('have.class', 'focused');
                        DashTable.focusedType(Key.ArrowLeft);

                        DashTable.getCellById(3, 'bbb').should('not.have.class', 'focused');
                        DashTable.getCellById(3, 'ggg').should('have.class', 'focused');
                    }, R.range(0, 2));
                });
            });

            describe('into a label cell', () => {
                beforeEach(() => {
                    DashTable.clickCellById(3, 'eee');
                });

                it('can move', () => {
                    R.forEach(() => {
                        DashTable.focusedType(Key.ArrowRight);

                        DashTable.getCellById(3, 'fff').should('have.class', 'focused');
                        DashTable.focusedType(Key.ArrowLeft);

                        DashTable.getCellById(3, 'fff').should('not.have.class', 'focused');
                        DashTable.getCellById(3, 'eee').should('have.class', 'focused');
                    }, R.range(0, 2));
                });
            });
        });
    });
});