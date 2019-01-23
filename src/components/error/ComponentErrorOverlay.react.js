import React, {Component} from 'react';
import PropTypes from 'prop-types';
import './ComponentErrorOverlay.css';

export default class ComponentErrorOverlay extends Component {
    render() {
        const {
            componentId,
            componentType,
        } = this.props;
        const errorLocationString =
            `Error in ${componentType} (id=${componentId})`;

        return (
            <div
                className={'dash-error-overlay'}
            >
                {errorLocationString}
            </div>
        );
    }
}

ComponentErrorOverlay.propTypes = {
    children: PropTypes.object,
    oldChildren: PropTypes.object,
    error: PropTypes.object,
    componentId: PropTypes.string,
    componentType: PropTypes.string,
    resolve: PropTypes.func,
};
