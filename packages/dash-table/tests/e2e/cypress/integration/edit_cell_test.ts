import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('edit cell', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8080');
    });

    it('can edit dropdown', () => {
        let initialValue: string;
        let expectedValue: string;

        DashTable.getCell(0, 8).within(() => {
            cy.get('.Select-value-label').then($valueLabel => {
                initialValue = $valueLabel[0].innerHTML;
                cy.log('initial value', initialValue);
            });
        });

        DashTable.getCell(0, 8).within(() => cy.get('div.Select').click()).then(() => {
            DashTable.getCell(0, 8).within(() => {
                cy.get('.Select-option').then($options => {
                    const target = Array.from($options).find($option => $option.innerHTML !== initialValue);
                    if (target) {
                        cy.wrap(target).click({ force: true });

                        expectedValue = target.innerHTML;
                        cy.log('expected value', expectedValue);
                    }
                });
            });
        });

        DashTable.getCell(0, 8).within(() => {
            cy.get('.Select-value-label').should('have.html', expectedValue);
        });
    });

    // https://github.com/plotly/dash-table/issues/50
    it('can edit on "enter"', () => {
        DashTable.getCell(0, 3).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

        DOM.focused.type(`abc${Key.Enter}`);
            DashTable.getCell(0, 3).within(() => cy.get('.cell-value').should('have.html', `abc${initialValue}`));
        });
    });

    it('can edit when clicking outside of cell', () => {
        DashTable.getCell(0, 3).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

        DOM.focused.type(`abc`);
        DashTable.getCell(0, 2).click();
            DashTable.getCell(0, 3).within(() => cy.get('.cell-value').should('have.html', `abc${initialValue}`));
        });
    });
});