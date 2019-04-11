import './FrontEndError.css';
import {Component} from 'react';
import CollapseIcon from '../icons/CollapseIcon.svg';
import PropTypes from 'prop-types';

import werkzeugCss from '../werkzeug.css.txt';

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

        let cardClasses;
        // if resolve is defined, the error should be a standalone card
        if (resolve) {
            cardClasses = 'dash-error-card';
        } else {
            cardClasses = 'dash-error-card__content';
        }
        if (inAlertsTray) {
            cardClasses += ' dash-error-card--alerts-tray';
        }

        const errorHeader = (
            <div
                className="dash-fe-error-top"
                onClick={() => this.setState({collapsed: !collapsed})}
            >
                <span className="dash-fe-error-top__group">
                    <span className="dash-fe-error__title">
                        {e.error.message || 'Error'}
                    </span>
                </span>

                <span className="dash-fe-error-top__group">
                    <span className="dash-fe-error__timestamp">
                        {`${e.timestamp.toLocaleTimeString()}`}
                    </span>

                    <CollapseIcon
                        className={`dash-fe-error__collapse ${
                            collapsed ? 'dash-fe-error__collapse--flipped' : ''
                        }`}
                        onClick={() => this.setState({collapsed: !collapsed})}
                    />
                </span>
            </div>
        );

        return collapsed ? (
            <div className="dash-error-card__list-item">{errorHeader}</div>
        ) : (
            <div className={cardClasses}>
                {errorHeader}
                <ErrorContent error={e.error} type={e.type} />
            </div>
        );
    }
}

/* eslint-disable no-inline-comments */
function ErrorContent({error, type}) {
    return (
        <div className="error-container">
            {!error.message || type === 'backEnd' ? null : (
                <div className="dash-fe-error__st">
                    <div className="dash-fe-error__info dash-fe-error__curved">
                        {error.message}
                    </div>
                </div>
            )}

            {!error.stack ? null : (
                <div className="dash-fe-error__st">
                    <div className="dash-fe-error__info_title dash-fe-error__curved-top">
                        {'JS Stack trace (see browser\'s console for details)'}
                    </div>
                    <div className="dash-fe-error__info dash-fe-error__curved-bottom">
                        <hr/>
                        {error.stack.split('\n').map(line => (
                            <p>{line}</p>
                        ))}
                    </div>
                </div>
            )}
            {/* Backend Error */}
            {!error.html ? null : (
                <div className="dash-be-error__st">
                    <div className="dash-backend-error">
                        {/* Embed werkzeug debugger in an iframe to prevent
                        CSS leaking - werkzeug HTML includes a bunch
                        of CSS on base html elements like `<body/>`
                      */}

                        <iframe
                            srcDoc={error.html.replace(
                                '</head>',
                                `<style type="text/css">${werkzeugCss}</style></head>`
                            )}
                            style={{
                                /*
                                 * 67px of padding and margin between this
                                 * iframe and the parent container.
                                 * 67 was determined manually in the
                                 * browser's dev tools.
                                 */
                                width: 'calc(600px - 67px)',
                                height: '75vh',
                                border: 'none',
                            }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}

const errorPropTypes = PropTypes.shape({
    message: PropTypes.string,

    /* front-end error messages */
    stack: PropTypes.string,

    /* backend error messages */
    html: PropTypes.string,
});

ErrorContent.propTypes = {
    error: errorPropTypes,
    type: PropTypes.oneOf(['backEnd', 'frontEnd'])
};

FrontEndError.propTypes = {
    e: PropTypes.shape({
        myUID: PropTypes.string,
        timestamp: PropTypes.object,
        type: PropTypes.oneOf(['backEnd', 'frontEnd']),
        error: errorPropTypes,
    }),
    resolve: PropTypes.func,
    inAlertsTray: PropTypes.bool,
    isListItem: PropTypes.bool,
};

FrontEndError.defaultProps = {
    inAlertsTray: false,
    isListItem: false,
};

export {FrontEndError};
