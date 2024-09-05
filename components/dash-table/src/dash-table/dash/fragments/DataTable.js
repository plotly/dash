import React, {Component} from 'react';

import RealTable from 'dash-table/components/Table';

import genRandomId from 'dash-table/utils/generate';
import isValidProps from '../validate';
import Sanitizer from '../Sanitizer';

import {propTypes, defaultProps} from '../DataTable';

export default class DataTable extends Component {
    constructor(props) {
        super(props);
        let id;
        this.getId = () => (id = id || genRandomId('table-'));
        this.sanitizer = new Sanitizer();
    }

    render() {
        if (!isValidProps(this.props)) {
            return <div>Invalid props combination</div>;
        }

        const sanitizedProps = this.sanitizer.sanitize(this.props);
        return this.props.id ? (
            <RealTable {...sanitizedProps} />
        ) : (
            <RealTable {...sanitizedProps} id={this.getId()} />
        );
    }
}

DataTable.defaultProps = defaultProps;
DataTable.propTypes = propTypes;
