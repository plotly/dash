import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode, ReadWriteModes } from 'demo/AppMode';

Object.values(ReadWriteModes).forEach(mode => {
    describe(`edit, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('readonly cell', () => {
            describe('with input', () => {
                it('does not modify value', () => {
                    DashTable.getCellById(0, 'aaa-readonly').click();
                    DashTable.getCellById(0, 'aaa-readonly').within(() => {
                        cy.get('input').should('not.exist');
                    });
                });
            });

            describe('with dropdown', () => {
                it('does not modify value', () => {
                    DashTable.getCellById(0, 'bbb-readonly').click();
                    DashTable.getCellById(0, 'bbb-readonly').within(() => {
                        cy.get('.Select-value-label').should('not.exist');
                    });
                });
            });

            describe('paste', () => {
                let copiedValue;

                beforeEach(() => {
                    DashTable.getCellById(0, 'rows').within(
                        () => cy.get('.dash-cell-value').then($cells => copiedValue = $cells[0].innerHTML)
                    );

                    DashTable.getCellById(0, 'rows').click();
                    DOM.focused.type(`${Key.Meta}c`);
                });

                it('does nothing', () => {
                    DashTable.getCellById(0, 'bbb-readonly').click();
                    DOM.focused.type(`${Key.Meta}v`);
                    DashTable.getCellById(0, 'bbb-readonly').within(
                        () => cy.get('.dash-cell-value').should('not.have.html', copiedValue)
                    );
                });
            });
        });

        it('can delete dropdown', () => {
            DashTable.getCell(0, 6).trigger('mouseover', { force: true });
            DashTable.getCell(0, 6).within(() => cy.get('.Select-clear').click({ force : true }));
            DashTable.getCell(0, 6).within(() => cy.get('.Select-placeholder').should('exist'));
        });

        it('can delete dropdown and set value', () => {
            DashTable.getCell(0, 6).trigger('mouseover', { force: true });
            DashTable.getCell(0, 6).within(() => cy.get('.Select-clear').click({ force: true }));
            DashTable.getCell(0, 6).within(() => cy.get('.Select-placeholder').should('exist'));

            DashTable.getCell(0, 6).within(() => cy.get('.Select-arrow').click({ force: true })).then(() => {
                DashTable.getCell(0, 6).within(() => {
                    cy.get('.Select-option').then($options => {
                        const target = $options[0];
                        if (target) {
                            cy.wrap(target).click({ force: true });
                        }
                    });
                });
            });

            DashTable.getCell(0, 6).within(() => cy.get('.Select-placeholder').should('not.exist'));
        });

        it('can edit dropdown', () => {
            let initialValue: string;
            let expectedValue: string;

            DashTable.getCell(0, 6).within(() => {
                cy.get('.Select-value-label').then($valueLabel => {
                    initialValue = $valueLabel[0].innerHTML;
                    cy.log('initial value', initialValue);
                });
            });

            DashTable.getCell(0, 6).within(() => cy.get('.Select-arrow').click());

            DashTable.getCell(0, 6).within(() => {
                cy.get('.Select-option').then($options => {
                    const target = Array.from($options).find($option => $option.innerHTML !== initialValue);
                    if (target) {
                        cy.wrap(target).click({ force: true });

                        expectedValue = target.innerHTML;
                        cy.log('expected value', expectedValue);
                    }
                });
            });

            DashTable.getCell(0, 6).within(() => {
                cy.get('.Select-value-label').should('have.html', expectedValue);
            });
        });

        // https://github.com/plotly/dash-table/issues/50
        it('can edit on "enter"', () => {
            DashTable.getCell(0, 1).click();
            DOM.focused.type(`abc${Key.Enter}`);
            DashTable.getCell(0, 1).within(() => cy.get('.dash-cell-value').should('have.html', `abc`));
        });

        it('can edit when clicking outside of cell', () => {
            DashTable.getCell(0, 1).click();
            DOM.focused.type(`abc`);
            DashTable.getCell(0, 0).click();
            DashTable.getCell(0, 1).within(() => cy.get('.dash-cell-value').should('have.html', `abc`));
        });
    });
});

describe(`edit, mode=${AppMode.Typed}`, () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Typed}`);
        DashTable.toggleScroll(false);
    });

    it('can edit number cell with a number string', () => {
        DashTable.getCellById(0, 'ccc').click();
        DOM.focused.type(`123${Key.Enter}`);
        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', `123`));
    });

    it('cannot edit number cell with a non-number string', () => {
        DashTable.getCellById(0, 'ccc').click();
        DOM.focused.type(`abc${Key.Enter}`);
        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('not.have.html', `abc`));
    });

    describe('copy/paste', () => {
        describe('string into a number', () => {
            let copiedValue;

            beforeEach(() => {
                DashTable.getCellById(0, 'bbb-readonly').within(
                    () => cy.get('.dash-cell-value').then($cells => copiedValue = $cells[0].innerHTML)
                );

                DashTable.getCellById(0, 'bbb-readonly').click();
                DOM.focused.type(`${Key.Meta}c`);
            });

            it('does nothing', () => {
                DashTable.getCellById(0, 'ccc').click();
                DOM.focused.type(`${Key.Meta}v`);
                DashTable.getCellById(0, 'ccc').within(
                    () => cy.get('.dash-cell-value').should('not.have.value', copiedValue)
                );
            });
        });

        describe('number into a number', () => {
            let copiedValue;

            beforeEach(() => {
                DashTable.getCellById(0, 'ddd').within(
                    () => cy.get('.dash-cell-value').then($cells => copiedValue = $cells[0].innerHTML)
                );

                DashTable.getCellById(0, 'ddd').click();
                DOM.focused.type(`${Key.Meta}c`);
            });

            it('copies value', () => {
                DashTable.getCellById(0, 'ccc').click();
                DOM.focused.type(`${Key.Meta}v`);
                DashTable.getCellById(0, 'ccc').within(
                    () => cy.get('.dash-cell-value').should('have.value', copiedValue)
                );
            });
        });
    });
});