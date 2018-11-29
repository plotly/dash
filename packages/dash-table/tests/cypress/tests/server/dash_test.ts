import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('dash basic', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8081');
    });

    it('can get cell', () => {
        DashTable.getCell(0, 0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '0'));

        cy.get('button.next-page').click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '250'));
    });

    it('cell click selects all text', () => {
        DashTable.getCell(0, 1).click();
        DashTable.getCell(0, 1).within(() =>
            cy.get('input').then($inputs => {
                const $input = $inputs[0];

                expect($input.selectionStart).to.equal(0);
                expect($input.selectionEnd).to.equal($input.value.length);
            })
        );
    });

    // https://github.com/plotly/dash-table/issues/50
    it('can edit last and update data on "enter"', () => {
        DashTable.getCell(249, 0).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

            DOM.focused.type(`abc${Key.Enter}`);

            cy.get('#container').should($container => {
                expect($container.first()[0].innerText).to.equal(`[249][0] = ${initialValue} -> abc`);
            });
        });
    });

    // https://github.com/plotly/dash-table/issues/107
    it('can edit last and update data on "tab"', () => {
        DashTable.getCell(249, 0).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

            DOM.focused.type(`abc`);

            cy.tab();

            cy.get('#container').should($container => {
                expect($container.first()[0].innerText).to.equal(`[249][0] = ${initialValue} -> abc`);
            });
        });
    });
    describe('ArrowKeys navigation', () => {
        describe('When active, but not focused', () => {
            // https://github.com/plotly/dash-table/issues/141
            it('can edit last, update data on "arrowleft", and move one cell to the left', () => {
                const startingCell = [249, 1];
                const targetCell = [249, 0];
                DashTable.getCell(startingCell[0], startingCell[1]).click();
                DOM.focused.then($input => {
                    const initialValue = $input.val();

                    DOM.focused.type(`abc${Key.ArrowLeft}`);

                    cy.get('#container').should($container => {
                        expect($container.first()[0].innerText).to.equal(`[249][1] = ${initialValue} -> abc`);
                    });
                });
                DashTable.getCell(targetCell[0], targetCell[1]).should('have.class', 'focused');
            });

            // https://github.com/plotly/dash-table/issues/141
            it('can edit last, update data on "arrowup", and move one cell up', () => {
                const startingCell = [249, 0];
                const targetCell = [248, 0];
                DashTable.getCell(startingCell[0], startingCell[1]).click();
                DOM.focused.then($input => {
                    const initialValue = $input.val();

                    DOM.focused.type(`abc${Key.ArrowUp}`);

                    cy.get('#container').should($container => {
                        expect($container.first()[0].innerText).to.equal(`[249][0] = ${initialValue} -> abc`);
                    });
                });
                DashTable.getCell(targetCell[0], targetCell[1]).should('have.class', 'focused');
            });

            // https://github.com/plotly/dash-table/issues/141
            it('can edit last, update data on "arrowright", and move one cell to the right', () => {
                const startingCell = [249, 0];
                const targetCell = [249, 1];
                DashTable.getCell(startingCell[0], startingCell[1]).click();
                DOM.focused.then($input => {
                    const initialValue = $input.val();

                    DOM.focused.type(`abc${Key.ArrowRight}`);

                    cy.get('#container').should($container => {
                        expect($container.first()[0].innerText).to.equal(`[249][0] = ${initialValue} -> abc`);
                    });
                });
                DashTable.getCell(targetCell[0], targetCell[1]).should('have.class', 'focused');
            });

            // https://github.com/plotly/dash-table/issues/141
            it('can edit last, update data on "arrowdown", and move one cell down', () => {
                const startingCell = [249, 0];
                const targetCell = [249, 1];
                DashTable.getCell(startingCell[0], startingCell[1]).click();
                DOM.focused.then($input => {
                    const initialValue = $input.val();

                    DOM.focused.type(`abc${Key.ArrowRight}`);

                    cy.get('#container').should($container => {
                        expect($container.first()[0].innerText).to.equal(`[249][0] = ${initialValue} -> abc`);
                    });
                });
                DashTable.getCell(targetCell[0], targetCell[1]).should('have.class', 'focused');
            });
        });
    });

    it('can edit last and update data when clicking outside of cell', () => {
        DashTable.getCell(249, 0).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

            DOM.focused.type(`abc`);
            DashTable.getCell(248, 0).click();

            cy.get('#container').should($container => {
                expect($container.first()[0].innerText).to.equal(`[249][0] = ${initialValue} -> abc`);
            });
        });
    });

    it('can get cell with double click', () => {
        DashTable.getCell(3, 1).within(() => cy.get('div').dblclick());
        DashTable.getCell(3, 1).should('have.class', 'focused');
    });
});