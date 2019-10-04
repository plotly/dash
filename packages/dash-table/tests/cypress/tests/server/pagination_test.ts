import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

const pagination_modes = ['native', 'custom']

describe('table pagination', () => {

    pagination_modes.forEach(mode => {

        describe(`can change pages with ${mode} page_action`, () => {

            before(() => {
                cy.visit(`http://localhost:8086?page_action=${mode}&page_count=29`);

                // initial state: first page, previous/first buttons disabled
                DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));
                cy.get('button.first-page').should('be.disabled');
                cy.get('button.previous-page').should('be.disabled');
                cy.get('input.current-page').should('have.attr', 'placeholder', '1');
                cy.get('.last-page').should('have.html', '29');
                cy.get('button.next-page').should('not.be.disabled');
                cy.get('button.last-page').should('not.be.disabled');

            });

            describe('with the navigation buttons', () => {

                it('with the next-page navigation button', () => {

                    // go forward by five pages
                    for (let i = 0; i < 5; i++) {
                        cy.get('button.next-page').click();
                    }

                    cy.get('button.first-page').should('not.be.disabled');
                    cy.get('button.previous-page').should('not.be.disabled');
                    cy.get('input.current-page').should('have.attr', 'placeholder', '6');
                    cy.get('.last-page').should('have.html', '29');
                    cy.get('button.next-page').should('not.be.disabled');
                    cy.get('button.last-page').should('not.be.disabled');

                    DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '26'));

                });

                it('with the previous-page navigation button', () => {
                    // go back by three pages
                    for (let i = 0; i < 3; i++) {
                        cy.get('button.previous-page').click();
                    }

                    cy.get('button.first-page').should('not.be.disabled');
                    cy.get('button.previous-page').should('not.be.disabled');
                    cy.get('input.current-page').should('have.attr', 'placeholder', '3');
                    cy.get('.last-page').should('have.html', '29');
                    cy.get('button.next-page').should('not.be.disabled');
                    cy.get('button.last-page').should('not.be.disabled');

                    DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '11'));

                });

                it('with the first page button', () => {
                    cy.get('button.first-page').click();

                    cy.get('button.first-page').should('be.disabled');
                    cy.get('button.previous-page').should('be.disabled');
                    cy.get('input.current-page').should('have.attr', 'placeholder', '1');
                    cy.get('.last-page').should('have.html', '29');
                    cy.get('button.next-page').should('not.be.disabled');
                    cy.get('button.last-page').should('not.be.disabled');

                    DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));

                });

                it('with the last page button', () => {
                    cy.get('button.last-page').click();

                    cy.get('button.first-page').should('not.be.disabled');
                    cy.get('button.previous-page').should('not.be.disabled');
                    cy.get('input.current-page').should('have.attr', 'placeholder', '29');
                    cy.get('.last-page').should('have.html', '29');
                    cy.get('button.next-page').should('be.disabled');
                    cy.get('button.last-page').should('be.disabled');

                    DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '141'));

                });
            });

            describe('with the text input box', () => {
                describe('correctly navigates to the desired page', () => {
                    it('with unfocus', () => {
                        cy.get('input.current-page').click();
                        DOM.focused.type(`14`);
                        cy.get('input.current-page').blur();

                        cy.get('button.first-page').should('not.be.disabled');
                        cy.get('button.previous-page').should('not.be.disabled');
                        cy.get('input.current-page').should('have.attr', 'placeholder', '14');
                        cy.get('.last-page').should('have.html', '29');
                        cy.get('button.next-page').should('not.be.disabled');
                        cy.get('button.last-page').should('not.be.disabled');

                        DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '66'));
                    }),
                        it('with enter', () => {
                            cy.get('input.current-page').click();
                            DOM.focused.type(`18${Key.Enter}`);

                            cy.get('button.first-page').should('not.be.disabled');
                            cy.get('button.previous-page').should('not.be.disabled');
                            cy.get('input.current-page').should('have.attr', 'placeholder', '18');
                            cy.get('input.current-page').should('not.be.focused');
                            cy.get('.last-page').should('have.html', '29');
                            cy.get('button.next-page').should('not.be.disabled');
                            cy.get('button.last-page').should('not.be.disabled');

                            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '86'));
                        })
                });

                describe('can handle invalid page numbers', () => {
                    it('zero value', () => {
                        cy.get('input.current-page').click();
                        DOM.focused.type('0');
                        cy.get('input.current-page').blur();

                        cy.get('button.first-page').should('be.disabled');
                        cy.get('button.previous-page').should('be.disabled');
                        cy.get('input.current-page').should('have.attr', 'placeholder', '1');
                        cy.get('.last-page').should('have.html', '29');
                        cy.get('button.next-page').should('not.be.disabled');
                        cy.get('button.last-page').should('not.be.disabled');

                        DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));

                    });

                    it('value higher than last page', () => {
                        cy.get('input.current-page').click();
                        DOM.focused.type('100');
                        cy.get('input.current-page').blur();
                        cy.get('button.first-page').should('not.be.disabled');
                        cy.get('button.previous-page').should('not.be.disabled');
                        cy.get('input.current-page').should('have.attr', 'placeholder', '29');
                        cy.get('.last-page').should('have.html', '29');
                        cy.get('button.next-page').should('be.disabled');
                        cy.get('button.last-page').should('be.disabled');

                        DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '141'));
                    });

                    it('negative value', () => {

                        cy.get('input.current-page').click();
                        DOM.focused.type('-1');
                        cy.get('input.current-page').blur();

                        cy.get('button.first-page').should('be.disabled');
                        cy.get('button.previous-page').should('be.disabled');
                        cy.get('input.current-page').should('have.attr', 'placeholder', '1');
                        cy.get('.last-page').should('have.html', '29');
                        cy.get('button.next-page').should('not.be.disabled');
                        cy.get('button.last-page').should('not.be.disabled');

                        DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));

                    });

                    it('non-numerical value', () => {
                        cy.get('input.current-page').click();
                        DOM.focused.type('10');
                        cy.get('input.current-page').blur();

                        cy.get('button.first-page').should('not.be.disabled');
                        cy.get('button.previous-page').should('not.be.disabled');
                        cy.get('input.current-page').should('have.attr', 'placeholder', '10');
                        cy.get('.last-page').should('have.html', '29');
                        cy.get('button.next-page').should('not.be.disabled');
                        cy.get('button.last-page').should('not.be.disabled');

                        DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '46'));

                        cy.get('input.current-page').click();
                        DOM.focused.type('hello');
                        cy.get('input.current-page').blur();

                        cy.get('button.first-page').should('not.be.disabled');
                        cy.get('button.previous-page').should('not.be.disabled');
                        cy.get('input.current-page').should('have.attr', 'placeholder', '10');
                        cy.get('.last-page').should('have.html', '29');
                        cy.get('button.next-page').should('not.be.disabled');
                        cy.get('button.last-page').should('not.be.disabled');

                        DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '46'));

                    });
                });
            });
        });
    });

    describe('handles other page_count values', () => {

        describe('hides pagination', () => {
            it('on single page', () => {
                cy.visit(`http://localhost:8086?page_action=custom&page_count=1`);

                cy.get('.previous-next-container').should('not.exist');

                DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));

            });

            it('on negative/zero values', () => {
                cy.visit(`http://localhost:8086?page_action=custom&page_count=-1`);

                cy.get('.previous-next-container').should('not.exist');

                DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));
            });
        });

        it('undefined/none', () => {

            cy.visit(`http://localhost:8086?page_action=custom`);

            cy.get('.page-number').children().should('have.length', 1);
            cy.get('.current-page').should('exist');
            cy.get('button.next-page').should('not.be.disabled');
            cy.get('button.last-page').should('be.disabled');

            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));

        });

        it('limits pages', () => {
            cy.visit(`http://localhost:8086?page_action=custom&page_count=10`);
            cy.get('button.last-page').click();

            cy.get('button.first-page').should('not.be.disabled');
            cy.get('button.previous-page').should('not.be.disabled');
            cy.get('input.current-page').should('have.attr', 'placeholder', '10');
            cy.get('.last-page').should('have.html', '10');
            cy.get('button.next-page').should('be.disabled');
            cy.get('button.last-page').should('be.disabled');

            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '46'));
        });
    });
});
