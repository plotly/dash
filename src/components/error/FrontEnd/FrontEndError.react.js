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
                {!e.error.stack ? null: (
                    <div className="dash-fe-error__st">
                        {e.error.stack &&
                            e.error.stack.split('\n').map(line => <p>{line}</p>)}
                    </div>
                )}
                {!e.error.html ? null : (
                    <div className="dash-be-error__st">
                        <div className="dash-backend-error">
                            {/* Embed werkzeug debugger in an iframe to prevent
                                CSS leaking - werkzeug HTML includes a bunch
                                of CSS on base html elements like `<body/>`
                              */}
                            <iframe
                                style={{
                                    'width': '600px',
                                    'height': '75vh',
                                    'border': 'none'
                                }}
                                srcDoc={e.error.html.replace(
                                '</head>',
`
<style type="text/css">
    {
        font-family: Roboto;
    }
    .traceback {
        background-color: white;
        border: 2px solid #dfe8f3;
        border-radius: 0px 0px 4px 4px;
        color: #506784;
    }
    h2.traceback {
        background-color: #f3f6fa;
        border: 2px solid #dfe8f3;
        border-bottom: 0px;
        box-sizing: border-box;
        border-radius: 4px 4px 0px 0px;
        color: #506784;
    }
    h2.traceback em{
        color: #506784;
        font-weight: 100;
    }
    .traceback pre, .debugger textarea{
        background-color: #F3F6FA;
    }
    .debugger h1{
        color: #506784;
        font-family: Roboto;
    }
    .explanation {
        color: #A2B1C6;
    }
     /* Hide the Don't Panic! footer */
     .debugger .footer {
         display: none;
     }

    /* Messing around */
     .traceback > ul > li {
         display: none;
     }
     .traceback > ul > li:nth-last-child(-n+3) {
         display: block;
     }
     .debugger h1 {
         display: none;
     }

     .debugger .errormsg {
         margin: 0;
         color: #506784;
         font-size: 16px;
         background-color: #f3f6fa;
         border: 2px solid #dfe8f3;
         box-sizing: border-box;
         border-radius: 4px;
         padding: 10px;
     }

    .debugger .pastemessage input {
        display: none;
    }

    .debugger .explanation {
        display: none;
    }
    .debugger div.plain {
        border-radius: 4px;
        border-width: 2px;
        color: #506784;
    }

    body {
        padding: 0px;
        margin: 0px;
    }
</style>
</head>`
                            )}/>
                        </div>
                    </div>
                )}
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
