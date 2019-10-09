import * as R from 'ramda';

import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
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
                DashTable.getCell(3, 1).click();
            });

            // Note: Dropdown cell is a label when readonly. Making a special
            // version of the test for the read only table.
            describe('into a dropdown cell', () => {
                beforeEach(() => {
                    DashTable.getCellById(3, 'ggg').click();
                });

                it('can move', () => {
                    R.forEach(() => {
                        DOM.focused.type(Key.ArrowRight);

                        DashTable.getCellById(3, 'bbb').should('have.class', 'focused');
                        DOM.focused.type(Key.ArrowLeft, { force: true });

                        DashTable.getCellById(3, 'bbb').should('not.have.class', 'focused');
                        DashTable.getCellById(3, 'ggg').should('have.class', 'focused');
                    }, R.range(0, 2));
                });
            });

            describe('into a label cell', () => {
                beforeEach(() => {
                    DashTable.getCellById(3, 'eee').click();
                });

                it('can move', () => {
                    R.forEach(() => {
                        DOM.focused.type(Key.ArrowRight);

                        DashTable.getCellById(3, 'fff').should('have.class', 'focused');
                        DOM.focused.type(Key.ArrowLeft, { force: true });

                        DashTable.getCellById(3, 'fff').should('not.have.class', 'focused');
                        DashTable.getCellById(3, 'eee').should('have.class', 'focused');
                    }, R.range(0, 2));
                });
            });
        });
    });
});