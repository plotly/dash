import React from 'react';
// A react component with all of the available proptypes to run tests over

/**
 * This is a description of the component.
 * It's multiple lines long.
 */
export default function ReactComponent({id, children}: {id: string; children?: React.ReactNode}) {
    <div id={id}>{children}</div>

}
