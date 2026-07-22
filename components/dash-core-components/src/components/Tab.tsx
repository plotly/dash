import React from 'react';
import './css/tabs.css';
import {TabProps} from '../types';

/**
 * Part of dcc.Tabs - this is the child Tab component used to render a tabbed page.
 * Its children will be set as the content of that tab, which if clicked will become visible.
 */
function Tab({
    children,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    disabled = false,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    disabled_style = {color: 'var(--Dash-Text-Disabled)'},
}: TabProps) {
    return <>{children}</>;
}

export default Tab;
