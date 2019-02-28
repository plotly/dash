import React from 'react';
import ReactDOM from 'react-dom';

import {Tabs, Tab} from '../src';
import Demo from './Demo.react';
import LoadingDemo from './LoadingDemo.react';

ReactDOM.render(
    <div>
        <Tabs>
            <Tab value="tab-1" label='Loading Demo'>
                <LoadingDemo />
            </Tab>
            <Tab value="tab-2" label='Component Gallery'>
                <Demo />
            </Tab>
        </Tabs>
    </div>,
    document.getElementById('react-demo-entry-point')
);
