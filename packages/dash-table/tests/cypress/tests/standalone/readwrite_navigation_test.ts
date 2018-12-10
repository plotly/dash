import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
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
                DashTable.getCell(3, 1).click();
            });

            describe('from a focused cell input', () => {
                beforeEach(() => {
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').dblclick());
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('have.class', 'focused'));
                });

                it('does focus on next cell input on "enter"', () => {
                    DOM.focused.type(Key.Enter);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));

                    DashTable.getCell(4, 1).should('have.class', 'focused');
                    DashTable.getCell(4, 1).within(() => cy.get('.dash-cell-value').should('not.have.class', 'focused'));
                });

                it('does focus on next cell input on text + "enter"', () => {
                    DOM.focused.type(`abc${Key.Enter}`);
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
                    DOM.focused.type(inputText);
                    DOM.focused.type(Key.ArrowLeft);

                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').then($inputs => {
                        const input = $inputs[0] as HTMLInputElement;
                        expect(input.selectionStart).to.equal(inputText.length - 1);
                        expect(input.selectionEnd).to.equal(inputText.length - 1);
                    }));

                    DOM.focused.type(Key.ArrowRight);
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
                    DOM.focused.type('abc');
                    DOM.focused.type(Key.ArrowUp);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('have.class', 'focused'));
                    DashTable.getCell(2, 1).should('not.have.class', 'focused');
                });
                it('does not focus on next cell input on "arrow down"', () => {
                    DOM.focused.type('abc');
                    DOM.focused.type(Key.ArrowDown);
                    DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').should('have.class', 'focused'));
                    DashTable.getCell(4, 1).should('not.have.class', 'focused');
                });
            });

            // Note: Dropdown cell is a label when readonly. Making a special
            // version of the test for the read only table -- here is the
            // writable (dropdown) version.
            describe('into a dropdown cell', () => {
                beforeEach(() => {
                    DashTable.getCell(3, 5).click();
                });

                it('can move', () => {
                    DOM.focused.type(Key.ArrowRight);

                    DashTable.getCell(3, 6).should('have.class', 'focused');
                    DashTable.getCell(3, 6).get('.Select').should('exist');
                    DOM.focused.type(Key.ArrowLeft, { force: true });

                    DashTable.getCell(3, 6).should('not.have.class', 'focused');
                    DashTable.getCell(3, 5).should('have.class', 'focused');
                });
            });

            it('does not allow the caret to be moved, instead it will select the entire text', () => {
                DashTable.getCell(3, 1).click();
                DOM.focused.type('abc');
                // Click again - clicking with something like .click('right') doesn't work
                // for some reason: DOM.focused will fail.
                DashTable.getCell(3, 1).click();
                DOM.focused.type('def');
                cy.tab();

                DashTable.getCell(3, 1).within(() => cy.get('.dash-cell-value').then($inputs => {
                    const input = $inputs[0] as HTMLInputElement;
                    expect(input.innerHTML).to.equal('def');
                }));
            });
        });
    });
});