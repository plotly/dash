import DashTable from 'cypress/DashTable';

import { AppMode } from 'demo/AppMode';

Object.values([AppMode.ReadOnly]).forEach(mode => {
    describe(`sort (readonly), mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        it('can sort', () => {
            DashTable.getCell(0, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Wet'));
            DashTable.getCell(1, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Snowy'));
            DashTable.getCell(2, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Tropical Beaches'));
            DashTable.getCell(3, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));

            DashTable.getCell(0, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Wet'));
            DashTable.getCell(1, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Snowy'));
            DashTable.getCell(2, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Tropical Beaches'));
            DashTable.getCell(3, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            cy.get('tr th.column-6:not(.phantom-cell) .column-header--sort').last().click();
            DashTable.getCell(0, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            DashTable.getCell(1, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            DashTable.getCell(2, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            DashTable.getCell(3, 6).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));

            DashTable.getCell(0, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            DashTable.getCell(1, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            DashTable.getCell(2, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
            DashTable.getCell(3, 7).within(() => cy.get('.dash-cell-value').should('have.html', 'label: Humid'));
        });
    });
});