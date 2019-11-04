import {connect} from 'react-redux';
import './FrontEndError.css';
import {Component} from 'react';
import CollapseIcon from '../icons/CollapseIcon.svg';
import PropTypes from 'prop-types';
import '../Percy.css';
import {urlBase} from '../../../utils';

import werkzeugCss from '../werkzeug.css.txt';

class FrontEndError extends Component {
    constructor(props) {
        super(props);
        this.state = {
            collapsed: this.props.isListItem,
        };
    }

    render() {
        const {e, inAlertsTray} = this.props;
        const {collapsed} = this.state;

        const cardClasses =
            'dash-error-card__content' +
            (inAlertsTray ? ' dash-error-card--alerts-tray' : '');

        /* eslint-disable no-inline-comments */
        const errorHeader = (
            <div
                className="dash-fe-error-top test-devtools-error-toggle"
                onClick={() => this.setState({collapsed: !collapsed})}
            >
                <span className="dash-fe-error-top__group">
                    ⛑️
                    <span className="dash-fe-error__title">
                        {e.error.message || 'Error'}
                    </span>
                </span>
                <span className="dash-fe-error-top__group">
                    <span className="dash-fe-error__timestamp percy-hide">
                        {`${e.timestamp.toLocaleTimeString()}`}
                    </span>
                    <span className="dash-fe-error__timestamp percy-show">
                        {/* Special percy timestamp for visual testing.
                         * Hidden during regular usage.
                         */}
                        00:00:00 PM
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
        /* eslint-enable no-inline-comments */

        return collapsed ? (
            <div className="dash-error-card__list-item">{errorHeader}</div>
        ) : (
            <div className={cardClasses}>
                {errorHeader}
                <ErrorContent error={e.error} />
            </div>
        );
    }
}

/* eslint-disable no-inline-comments, no-magic-numbers */
function UnconnectedErrorContent({error, base}) {
    return (
        <div className="error-container">
            {/*
             * 40 is a rough heuristic - if longer than 40 then the
             * message might overflow into ellipses in the title above &
             * will need to be displayed in full in this error body
             */}
            {typeof error.message !== 'string' ||
            error.message.length < 40 ? null : (
                <div className="dash-fe-error__st">
                    <div className="dash-fe-error__info dash-fe-error__curved">
                        {error.message}
                    </div>
                </div>
            )}

            {typeof error.stack !== 'string' ? null : (
                <div className="dash-fe-error__st">
                    <div className="dash-fe-error__info">
                        <details>
                            <summary>
                                <i>
                                    (This error originated from the built-in
                                    JavaScript code that runs Dash apps. Click
                                    to see the full stack trace or open your
                                    browser's console.)
                                </i>
                            </summary>

                            {error.stack.split('\n').map(line => (
                                <p>{line}</p>
                            ))}
                        </details>
                    </div>
                </div>
            )}
            {/* Backend Error */}
            {typeof error.html !== 'string' ? null : error.html.indexOf(
                  '<!DOCTYPE HTML'
              ) !== -1 ? (
                <div className="dash-be-error__st">
                    <div className="dash-backend-error">
                        {/* Embed werkzeug debugger in an iframe to prevent
                        CSS leaking - werkzeug HTML includes a bunch
                        of CSS on base html elements like `<body/>`
                      */}

                        <iframe
                            srcDoc={error.html
                                .replace(
                                    '</head>',
                                    `<style type="text/css">${werkzeugCss}</style></head>`
                                )
                                .replace(
                                    '="?__debugger__',
                                    `="${base}?__debugger__`
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
            ) : (
                <div className="dash-be-error__str">
                    <div
                        className="dash-backend-error"
                        style={{
                            width: 'calc(600px - 67px)',
                            height: '75vh',
                            border: 'none',
                        }}
                    >
                        {error.html}
                    </div>
                </div>
            )}
        </div>
    );
}
/* eslint-enable no-inline-comments, no-magic-numbers */

const errorPropTypes = PropTypes.shape({
    message: PropTypes.string,

    /* front-end error messages */
    stack: PropTypes.string,

    /* backend error messages */
    html: PropTypes.string,
});

UnconnectedErrorContent.propTypes = {
    error: errorPropTypes,
    base: PropTypes.string,
};

const ErrorContent = connect(state => ({base: urlBase(state.config)}))(
    UnconnectedErrorContent
);

FrontEndError.propTypes = {
    e: PropTypes.shape({
        myUID: PropTypes.string,
        timestamp: PropTypes.object,
        error: errorPropTypes,
    }),
    inAlertsTray: PropTypes.bool,
    isListItem: PropTypes.bool,
};

FrontEndError.defaultProps = {
    inAlertsTray: false,
    isListItem: false,
};

export {FrontEndError};
