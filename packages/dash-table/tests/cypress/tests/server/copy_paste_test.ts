import DashTable, { State } from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('copy paste', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8082');
        cy.wait(1000);
    });

    it('can copy multiple rows', () => {
        DashTable.getCell(0, 0).click();
        DOM.focused.type(Key.Shift, { release: false });
        DashTable.getCell(2, 0).click();

        DOM.focused.type(`${Key.Meta}c`);
        DashTable.getCell(3, 0).click();
        DOM.focused.type(`${Key.Meta}v`);
        DashTable.getCell(0, 0, State.Any).click();

        for (let row = 0; row <= 2; ++row) {
            DashTable.getCell(row + 3, 0, State.Any).within(() => cy.get('.dash-cell-value').should('have.html', `${row}`));
        }
    });

    it('can copy rows 9 and 10', () => {
        DashTable.getCell(9, 0).click();
        DOM.focused.type(`${Key.Shift}${Key.ArrowDown}`);

        DOM.focused.type(`${Key.Meta}c`);
        DashTable.getCell(1, 0).click();
        DOM.focused.type(`${Key.Meta}v`);
        DashTable.getCell(0, 0, State.Any).click();

        DashTable.getCell(1, 0, State.Any).within(() => cy.get('.dash-cell-value').should('have.html', '9'));
        DashTable.getCell(2, 0, State.Any).within(() => cy.get('.dash-cell-value').should('have.html', '10'));

    });

    it('can copy multiple rows and columns', () => {
        DashTable.getCell(0, 1).click();
        DOM.focused.type(Key.Shift, { release: false });
        DashTable.getCell(2, 2).click();

        DOM.focused.type(`${Key.Meta}c`);
        DashTable.getCell(3, 1).click();
        DOM.focused.type(`${Key.Meta}v`);
        DashTable.getCell(0, 0, State.Any).click();

        for (let row = 0; row <= 2; ++row) {
            for (let column = 1; column <= 2; ++column) {
                let initialValue: string;

                DashTable.getCell(row, column, State.Any).within(() => cy.get('.dash-cell-value').then($cells => initialValue = $cells[0].innerHTML));
                DashTable.getCell(row + 3, column, State.Any).within(() => cy.get('.dash-cell-value').should('have.html', initialValue));
            }
        }
    });

    it('can copy multiple rows and columns from one table and paste to another', () => {
        DashTable.getCell(10, 0).click();
        DOM.focused.type(Key.Shift, { release: false });
        DashTable.getCell(13, 3).click();

        DOM.focused.type(`${Key.Meta}c`);
        cy.get(`#table2 tbody tr td.column-${0}`).eq(0).click();
        DOM.focused.type(`${Key.Meta}v`);
        cy.get(`#table2 tbody tr td.column-${3}`).eq(3).click();

        cy.wait(1000);

        DashTable.getCell(14, 0).click();
        DOM.focused.type(Key.Shift, { release: false });

        for (let row = 10; row <= 13; ++row) {
            for (let column = 0; column <= 3; ++column) {
                let initialValue: string;

                DashTable.getCell(row, column).within(() => cy.get('.dash-cell-value').then($cells => initialValue = $cells[0].innerHTML));
                cy.get(`#table2 tbody tr td.column-${column}`).eq(row - 10).within(() => cy.get('.dash-cell-value').should('have.html', initialValue));
            }
        }
    });

    describe('copy and paste with hideable columns', () => {
        it('copy multiple rows and columns within table', () => {
            DashTable.hideColumnById(0, '0');

            DashTable.getCell(0, 0).click();
            DOM.focused.type(Key.Shift, { release: false });
            DashTable.getCell(2, 2).click();

            DOM.focused.type(`${Key.Meta}c`);
            DashTable.getCell(3, 1).click();
            DOM.focused.type(`${Key.Meta}v`);
            DashTable.getCell(5, 3, State.Any).click();

            DashTable.getCell(6, 0, State.Any).click();
            DOM.focused.type(Key.Shift, { release: false });

            for (let row = 0; row <= 2; ++row) {
                for (let column = 0; column <= 2; ++column) {
                    let initialValue: string;

                    DashTable.getCell(row, column, State.Any).within(() => cy.get('.dash-cell-value').then($cells => initialValue = $cells[0].innerHTML));
                    DashTable.getCell(row + 3, column + 1, State.Any).within(() => cy.get('.dash-cell-value').should('have.html', initialValue));
                }
            }
        });

        it('copy multiple rows and columns from one table to another', () => {
            DashTable.hideColumnById(0, '0');

            DashTable.getCell(10, 0).click();
            DOM.focused.type(Key.Shift, { release: false });
            DashTable.getCell(13, 2).click();

            DOM.focused.type(`${Key.Meta}c`);
            cy.get(`#table2 tbody tr td.column-${0}`).eq(0).click();
            DOM.focused.type(`${Key.Meta}v`);
            cy.get(`#table2 tbody tr td.column-${3}`).eq(2).click();

            DashTable.getCell(16, 6).click();
            DOM.focused.type(Key.Shift, { release: false });

            for (let row = 10; row <= 13; ++row) {
                for (let column = 0; column <= 2; ++column) {
                    let initialValue: string;

                    DashTable.getCell(row, column).within(() => cy.get('.dash-cell-value').then($cells => initialValue = $cells[0].innerHTML));
                    cy.get(`#table2 tbody tr td.column-${column}`).eq(row - 10).within(() => cy.get('.dash-cell-value').should('have.html', initialValue));
                }
            }
        });
    });

    // Commenting this test as Cypress team is having issues with the copy/paste scenario
    // LINK: https://github.com/cypress-io/cypress/issues/2386
    describe('BE roundtrip on copy-paste', () => {
        it('on cell modification', () => {
            DashTable.getCell(0, 0).click();
            DOM.focused.type(`10${Key.Enter}`);

            cy.wait(1000);

            DashTable
                .getCell(0, 0, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.html', '10'))
                .then(() => {
                    DashTable.getCell(0, 1, State.Any)
                        .within(() => cy.get('.dash-cell-value').should('have.html', 'MODIFIED'));
                });
        });

        it('with unsorted, unfiltered data', () => {
            DashTable.getCell(0, 0).click();
            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(1, 0).click();
            DOM.focused.type(`${Key.Meta}v`);

            cy.wait(1000);

            DashTable
                .getCell(1, 1, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.html', 'MODIFIED'));
            DashTable
                .getCell(1, 0, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.value', '0'));

            DashTable.getCell(1, 1).click();
            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(2, 1).click();
            DOM.focused.type(`${Key.Meta}v`);

            cy.wait(1000);

            DashTable
                .getCell(2, 1, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.value', 'MODIFIED'));
        });

        it('BE rountrip with sorted, unfiltered data', () => {
            cy.get('#table tr th.column-2 .column-header--sort').last().click();

            DashTable.getCell(0, 0).click();
            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.value', '11'));

            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(1, 0).click();
            DOM.focused.type(`${Key.Meta}v`);

            cy.wait(1000);

            DashTable
                .getCell(1, 1, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.html', 'MODIFIED'));
            DashTable
                .getCell(1, 0, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.value', '11'));

            DashTable.getCell(1, 1).click();
            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(2, 1).click();
            DOM.focused.type(`${Key.Meta}v`);

            cy.wait(1000);

            DashTable
                .getCell(2, 1, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.value', 'MODIFIED'));
            DashTable
                .getCell(1, 0, State.Any)
                .within(() => cy.get('.dash-cell-value').should('have.html', '11'));
        });
    });
});

describe('copy/paste behaviour with markdown', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8087')
    });

    describe('single cell', () => {
        it('copy markdown to non-markdown', () => {
            DashTable.getCell(0, 3).click();
            DOM.focused.type(`${Key.Meta}c`);
            DashTable.getCell(0, 2).click();
            DOM.focused.type(`${Key.Meta}v`);
            DashTable.getCell(0, 2).within(() => {
                cy.get('.dash-cell-value').should('have.attr', 'value', '![Communication tactics](https://dash.plot.ly/assets/images/logo.png)');
            });
        });

        it('copy markdown to markdown', () => {
            DashTable.getCell(0, 1).click();
            DOM.focused.type(`${Key.Meta}c`);
            DashTable.getCell(0, 0).click();
            DOM.focused.type(`${Key.Meta}v`);
            DashTable.getCell(0, 0).within(() => {
                cy.get('.dash-cell-value > p > a').should('have.html', 'Debt collection');
                cy.get('.dash-cell-value > p > a').should('have.attr', 'href', 'plot.ly');
            });
        });

        describe('copy non-markdown to markdown', () => {
            it('null/empty value', () => {
                DashTable.getCell(0, 2).click();
                DOM.focused.type(`${Key.Meta}c`);
                DashTable.getCell(0, 1).click();
                DOM.focused.type(`${Key.Meta}v`);
                DashTable.getCell(0, 1).within(() => {
                    cy.get('.dash-cell-value > p').should('have.html', 'null');
                });
            });

            it('regular value', () => {
                DashTable.getCell(1, 2).click();
                DOM.focused.type(`${Key.Meta}c`);
                DashTable.getCell(1, 1).click();
                DOM.focused.type(`${Key.Meta}v`);
                DashTable.getCell(1, 1).within(() => {
                    cy.get('.dash-cell-value > p').should('have.html', 'Medical');
                });
            });
        });
    });
});
