import DashTable from 'cypress/DashTable';

import { AppMode } from 'demo/AppMode';

Object.values([AppMode.ReadOnly]).forEach(mode => {
    describe(`sort (readonly), mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        it('can sort', () => {
            DashTable.getCell(0, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Wet'));
            DashTable.getCell(1, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Snowy'));
            DashTable.getCell(2, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Tropical Beaches'));
            DashTable.getCell(3, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Humid'));
            cy.get('tr th.column-6 .sort').last().click();
            DashTable.getCell(0, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Humid'));
            DashTable.getCell(1, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Humid'));
            DashTable.getCell(2, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Humid'));
            DashTable.getCell(3, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'Humid'));
        });
    });
});