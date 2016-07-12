import React, {Component} from 'react';
import {Header, EditableDiv, InputControl} from '../src';

class Demo extends Component {
    render() {
        return (
            <div>
                <h1>Dash Core Component Suite Demo</h1>

                <hr/>
                <h2>Header</h2>
                <Header
                    name="Example Name"
                />
                <hr/>

                <h2>EditableDiv</h2>
                <EditableDiv
                    editable={true}
                    text="I am editable"
                />
                <hr/>

                <h2>InputControl</h2>
                <InputControl/>
                <hr/>
            </div>
        );
    }
}

export default Demo;
