import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';

import { ReadWriteModes } from 'demo/AppMode';

Object.values(ReadWriteModes).forEach(mode => {
    describe(`navigate (readwrite), mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('with keyboard', () => {
            beforeEach(() => {
                DashTable.clickCell(3, 1);
            });

            describe('from a focused cell input', () => {
                beforeEach(() => {
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').dblclick({ force: true }));
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('have.class', 'focused'));
                });

                it('does focus on next cell input on "enter"', () => {
                    DashTable.focusedType(Key.Enter);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));

                    DashTable.getCell(4, 1).should('have.class', 'focused');
                    DashTable.getCell(4, 1).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));
                });

                it('does focus on next cell input on text + "enter"', () => {
                    DashTable.focusedType(`abc${Key.Enter}`);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));

                    DashTable.getCell(4, 1).should('have.class', 'focused');
                    DashTable.getCell(4, 1).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));
                });

                it('does focus on next cell input on "tab"', () => {
                    cy.tab();

                    DashTable.getCell(3, 1).should('not.have.class', 'focused');

                    DashTable.getCell(3, 2).should('have.class', 'focused');
                    DashTable.getCell(3, 2).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));
                });

                it('pressing left and right arrows moves caret', () => {
                    const inputText = 'abc';
                    DashTable.focusedType(inputText);
                    DashTable.focusedType(Key.ArrowLeft);

                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').then($inputs => {
                        const input = $inputs[0] as HTMLInputElement;
                        expect(input.selectionStart).to.equal(inputText.length - 1);
                        expect(input.selectionEnd).to.equal(inputText.length - 1);
                    }));

                    DashTable.focusedType(Key.ArrowRight);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').then($inputs => {
                        const input = $inputs[0] as HTMLInputElement;
                        expect(input.selectionStart).to.equal(inputText.length);
                        expect(input.selectionEnd).to.equal(inputText.length);
                    }));
                });
                // TODO: same test but for up and down arrows as above ^. This currently isn't working
                // because Cypress doesn't move the input cursor upon up and down keys,
                // so the test will fail. For now, we test if up and down arrows at least
                // don't move focus to other cell
                it('does not focus on next cell input on "arrow up"', () => {
                    DashTable.focusedType('abc');
                    DashTable.focusedType(Key.ArrowUp);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('have.class', 'focused'));
                    DashTable.getCell(2, 1).should('not.have.class', 'focused');
                });
                it('does not focus on next cell input on "arrow down"', () => {
                    DashTable.focusedType('abc');
                    DashTable.focusedType(Key.ArrowDown);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('have.class', 'focused'));
                    DashTable.getCell(4, 1).should('not.have.class', 'focused');
                });
            });

            // Note: Dropdown cell is a label when readonly. Making a special
            // version of the test for the read only table -- here is the
            // writable (dropdown) version.
            describe('into a dropdown cell', () => {
                beforeEach(() => {
                    DashTable.clickCell(3, 5);
                });

                it('can move', () => {
                    DashTable.focusedType(Key.ArrowRight);

                    DashTable.getCell(3, 6).should('have.class', 'focused');
                    DashTable.getCell(3, 6).get('.Select').should('exist');
                    DashTable.focusedType(Key.ArrowLeft);

                    DashTable.getCell(3, 6).should('not.have.class', 'focused');
                    DashTable.getCell(3, 5).should('have.class', 'focused');
                });
            });

            it('does not allow the caret to be moved, instead it will select the entire text', () => {
                DashTable.clickCell(3, 1);
                DashTable.focusedType('abc');
                // Click again - clicking with something like .click('right') doesn't work
                // for some reason: DOM.focused will fail.
                DashTable.clickCell(3, 1);
                DashTable.focusedType('def');
                cy.tab();

                DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').then($inputs => {
                    const input = $inputs[0] as HTMLInputElement;
                    expect(input.innerHTML).to.equal('def');
                }));
            });
        });
    });
});