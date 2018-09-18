import DashTable from 'cypress/DashTable';

describe('sort', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8080');
    });

    it('can sort', () => {
        DashTable.getCell(0, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Wet'));
        DashTable.getCell(1, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Snowy'));
        DashTable.getCell(2, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Tropical Beaches'));
        DashTable.getCell(3, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Humid'));
        cy.get('tr th.column-8 .sort').click();
        DashTable.getCell(0, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Wet'));
        DashTable.getCell(1, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Wet'));
        DashTable.getCell(2, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Wet'));
        DashTable.getCell(3, 8).within(() => cy.get('.Select-value-label').should('have.html', 'Wet'));
    });
});
