import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

Object.values(AppMode).forEach(mode => {
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
        });
    });
});