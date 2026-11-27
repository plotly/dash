import React from 'react';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import Dropdown from '../../../src/components/Dropdown';

const options = [
    {label: 'Apple', value: 'apple'},
    {label: 'Banana', value: 'banana'},
];

async function findDropdownElements(container: HTMLElement) {
    const trigger = await waitFor(() => {
        const button = container.querySelector('button.dash-dropdown');
        expect(button).toBeInstanceOf(HTMLButtonElement);
        return button as HTMLButtonElement;
    });
    const focusTarget = container.querySelector('.dash-dropdown-focus-target');
    expect(focusTarget).toBeInstanceOf(HTMLInputElement);
    return {
        trigger,
        focusTarget: focusTarget as HTMLInputElement,
    };
}

describe('Dropdown focus target', () => {
    it('removes focus target from tab order when trigger button is focused directly and restores it on blur', async () => {
        const {container} = render(
            <div>
                <button type="button">Before</button>
                <Dropdown
                    id="test-dropdown"
                    options={options}
                    setProps={jest.fn()}
                />
                <button type="button">After</button>
            </div>
        );

        const {trigger, focusTarget} = await findDropdownElements(container);
        expect(focusTarget.tabIndex).toBe(0);

        // Simulates clicking the trigger or Radix returning focus after Escape/selection.
        fireEvent.focus(trigger);
        expect(focusTarget.tabIndex).toBe(-1);

        // Moving focus out restores the focus target so Safari Tab navigation still works.
        fireEvent.blur(trigger);
        expect(focusTarget.tabIndex).toBe(0);
    });

    it('keeps focus target untabbable when disabled', async () => {
        const {container} = render(
            <Dropdown
                id="disabled-dropdown"
                options={options}
                disabled
                setProps={jest.fn()}
            />
        );

        const {trigger, focusTarget} = await findDropdownElements(container);
        expect(focusTarget.tabIndex).toBe(-1);

        fireEvent.focus(trigger);
        expect(focusTarget.tabIndex).toBe(-1);

        fireEvent.blur(trigger);
        expect(focusTarget.tabIndex).toBe(-1);
    });

    it('delegates focus from focus target to trigger button when entering from another element', async () => {
        const {container} = render(
            <div>
                <button type="button">Before</button>
                <Dropdown
                    id="tab-dropdown"
                    options={options}
                    setProps={jest.fn()}
                />
            </div>
        );

        const beforeButton = screen.getByRole('button', {name: 'Before'});
        const {trigger, focusTarget} = await findDropdownElements(container);

        fireEvent.focus(focusTarget, {relatedTarget: beforeButton});

        expect(focusTarget.tabIndex).toBe(-1);
        expect(document.activeElement).toBe(trigger);
    });
});
