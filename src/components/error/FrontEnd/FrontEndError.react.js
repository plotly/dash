import './FrontEndError.css';
import {Component} from 'react';
import ErrorIcon from '../icons/ErrorIcon.svg';
import CloseIcon from '../icons/CloseIcon.svg';
import CollapseIcon from '../icons/CollapseIcon.svg';
import PropTypes from 'prop-types';

class FrontEndError extends Component {
    constructor(props) {
        super(props);
        this.state = {
            collapsed: this.props.isListItem,
        };
    }

    render() {
        const {e, resolve, inAlertsTray} = this.props;
        const {collapsed} = this.state;

        let closeButton, cardClasses;
        // if resolve is defined, the error should be a standalone card
        if (resolve) {
            closeButton = (
                <CloseIcon
                    className="dash-fe-error__icon-close"
                    onClick={() => resolve('frontEnd', e.myUID)}
                />
            );
            cardClasses = 'dash-error-card';
        } else {
            cardClasses = 'dash-error-card__content';
        }
        if (inAlertsTray) {
            cardClasses += ' dash-error-card--alerts-tray';
        }
        return collapsed ? (
            <div className="dash-error-card__list-item">
                <ErrorIcon className="dash-fe-error__icon-error" />
                <h6 className="dash-fe-error__title">
                    {e.error.message ||
                        'An error was thrown that was not an Error object, so info could not be gathered.'}
                </h6>
                <CollapseIcon
                    className="dash-fe-error__collapse"
                    onClick={() => this.setState({collapsed: false})}
                />
            </div>
        ) : (
            <div className={cardClasses}>
                <div className="dash-fe-error-top">
                    <ErrorIcon className="dash-fe-error__icon-error" />
                    <h6 className="dash-fe-error__title">
                        {e.error.message ||
                            'An error was thrown that was not an Error object, so info could not be gathered.'}
                    </h6>
                    {this.props.isListItem ? (
                        <CollapseIcon
                            className="dash-fe-error__collapse dash-fe-error__collapse--flipped"
                            onClick={() => this.setState({collapsed: true})}
                        />
                    ) : (
                        closeButton
                    )}
                </div>
                <div className="dash-fe-error__st">
                    {e.error.stack &&
                        e.error.stack.split('\n').map(line => <p>{line}</p>)}
                </div>
            </div>
        );
    }
}

FrontEndError.propTypes = {
    e: PropTypes.object,
    resolve: PropTypes.func,
    inAlertsTray: PropTypes.bool,
    isListItem: PropTypes.bool,
};

FrontEndError.defaultProps = {
    inAlertsTray: false,
    isListItem: false,
};

export {FrontEndError};
