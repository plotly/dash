import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';
import Resolve from 'cypress/Resolve';

describe('copy paste', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8082');
    });

    it('can do BE roundtrip on cell modification', () => {
        DashTable.getCell(0, 0).click();
        DOM.focused.type(`1${Key.Enter}`);

        DashTable
            .getCell(0, 0)
            .within(() => cy.get('.cell-value').should('have.html', '10'));

        DashTable.getCell(0, 1)
            .within(() => cy.get('.cell-value').should('have.html', 'MODIFIED'));
    });

    it('can do BE roundtrip on copy-paste', async () => {
        await Resolve(DashTable.getCell(0, 0).click());
        await Resolve(DOM.focused.type(`${Key.Control}c`));

        await Resolve(DashTable.getCell(1, 0).click());
        await Resolve(DOM.focused.type(`${Key.Control}v`));

        DashTable
            .getCell(1, 1)
            .within(() => cy.get('.cell-value').should('have.html', 'MODIFIED'));

    });
});
