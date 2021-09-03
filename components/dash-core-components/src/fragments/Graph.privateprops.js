import PropTypes from 'prop-types';

export const privatePropTypes = {
    _dashprivate_transformConfig: PropTypes.func,
    _dashprivate_transformFigure: PropTypes.func,
    _dashprivate_onFigureModified: PropTypes.func,
};

export const privateDefaultProps = {
    _dashprivate_transformConfig: c => c,
    _dashprivate_transformFigure: f => f,
    _dashprivate_onFigureModified: f => f,
};
