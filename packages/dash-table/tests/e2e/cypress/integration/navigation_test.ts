import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';
import Resolve from 'cypress/Resolve';

describe('navigate', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8080');
    });

    it('does not change column width', async () => {
        const startWidth = await Resolve(DashTable.getCell(3, 3)).then(res => res.outerWidth());

        await Resolve(DashTable.getCell(3, 3).click());

        const endWidth = await Resolve(DashTable.getCell(3, 3).then(res => res.outerWidth()));

        expect(endWidth).to.equal(startWidth);

    });

    describe('with keyboard', () => {
        beforeEach(() => {
            DashTable.getCell(3, 3).click();
        });

        describe('from a focused cell input', () => {
            beforeEach(() => {
                DOM.focused.type(Key.Enter);
                DashTable.getCellInput(3, 3).should('have.class', 'focused');
            });

            it('does not focus on next cell input on "enter"', () => {
                DOM.focused.type(Key.Enter);
                DashTable.getCell(3, 3).should('not.have.class', 'focused');

                DashTable.getCell(4, 3).should('have.class', 'focused');
                DashTable.getCellInput(4, 3).should('not.have.class', 'focused');
            });

            it('does not focus on next cell input on "tab"', async () => {
                cy.tab();

                DashTable.getCell(3, 3).should('not.have.class', 'focused');

                DashTable.getCell(3, 4).should('have.class', 'focused');
                DashTable.getCellInput(3, 4).should('not.have.class', 'focused');
            });
        });

        describe('into a dropdown cell', () => {
            beforeEach(() => {
                DashTable.getCell(3, 7).click();
            });

            it('can move', () => {
                DOM.focused.type(Key.ArrowRight);

                DashTable.getCell(3, 8).should('have.class', 'focused');
                DashTable.getCell(3, 8).get('.Select').should('exist');
                DOM.focused.type(Key.ArrowLeft);

                DashTable.getCell(3, 8).should('not.have.class', 'focused');
                DashTable.getCell(3, 7).should('have.class', 'focused');
            });
        });

        it('can move down', () => {
            DOM.focused.type(Key.ArrowDown);
            DashTable.getCell(4, 3).should('have.class', 'focused');
            DashTable.getCell(3, 3).should('not.have.class', 'focused');
        });

        it('can move left', () => {
            DOM.focused.type(Key.ArrowLeft);
            DashTable.getCell(3, 2).should('have.class', 'focused');
            DashTable.getCell(3, 3).should('not.have.class', 'focused');
        });

        it('can moved right', () => {
            DOM.focused.type(Key.ArrowRight);
            DashTable.getCell(3, 4).should('have.class', 'focused');
            DashTable.getCell(3, 3).should('not.have.class', 'focused');
        });

        it('can move up', () => {
            DOM.focused.type(Key.ArrowUp);
            DashTable.getCell(2, 3).should('have.class', 'focused');
            DashTable.getCell(3, 3).should('not.have.class', 'focused');
        });
    });

    describe('with mouse', () => {
        beforeEach(() => {
            DashTable.getCell(3, 3).click();
        });

        it('can select self', () => {
            DOM.focused.click();
            DashTable.getCell(3, 3).should('have.class', 'focused');
        });

        it('can select other', () => {
            DashTable.getCell(4, 4).click();
            DashTable.getCell(4, 4).should('have.class', 'focused');
            DashTable.getCell(3, 3).should('not.have.class', 'focused');
        });
    });
});
