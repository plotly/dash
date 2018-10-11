import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('edit cell', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8080');
    });

    it('can delete dropdown', () => {
        DashTable.getCell(0, 6).trigger('mouseover');
        DashTable.getCell(0, 6).within(() => cy.get('.Select-clear').click());
        DashTable.getCell(0, 6).within(() => cy.get('.Select-placeholder').should('exist'));
    });

    it('can delete dropdown and set value', () => {
        DashTable.getCell(0, 6).trigger('mouseover');
        DashTable.getCell(0, 6).within(() => cy.get('.Select-clear').click());
        DashTable.getCell(0, 6).within(() => cy.get('.Select-placeholder').should('exist'));

        DashTable.getCell(0, 6).within(() => cy.get('.Select-arrow').click()).then(() => {
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

    it('can edit on 2nd page', () => {
        DashTable.getCell(0, 0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '1'));
        cy.get('button.next-page').click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '251'));

        DOM.focused.type(`abc${Key.Enter}`);
        DashTable.getCell(0, 0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', 'abc'));
    });

    it('can delete then edit on 2nd page', () => {
        DashTable.getCell(0, 0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '1'));
        cy.get('button.next-page').click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '251'));
        DashTable.getDelete(0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '252'));

        DOM.focused.type(`abc${Key.Enter}`);
        DashTable.getCell(0, 0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', 'abc'));
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