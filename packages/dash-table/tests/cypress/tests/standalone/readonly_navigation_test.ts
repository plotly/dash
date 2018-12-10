import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

Object.values([AppMode.ReadOnly]).forEach(mode => {
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
                    DashTable.getCell(3, 5).click();
                });

                it('can move', () => {
                    DOM.focused.type(Key.ArrowRight);

                    DashTable.getCell(3, 6).should('have.class', 'focused');
                    DOM.focused.type(Key.ArrowLeft, { force: true });

                    DashTable.getCell(3, 6).should('not.have.class', 'focused');
                    DashTable.getCell(3, 5).should('have.class', 'focused');
                });
            });
        });
    });
});