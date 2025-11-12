import React, {useMemo} from 'react';

import {useDevtool, useDevtoolMenuButtonClassName} from './DevtoolContext';

import './PlotlyCloud.css';
import CloudSlashIcon from '../icons/CloudSlashIcon.svg';

const CLOUD_POPUP = 'cloud';

const PlotlyCloud = () => {
    const {popup, setPopup} = useDevtool();

    const className = useDevtoolMenuButtonClassName(CLOUD_POPUP);

    const isOpen = useMemo(() => popup === CLOUD_POPUP, [popup]);

    const onClick = () => {
        if (popup === CLOUD_POPUP) {
            setPopup('');
        } else {
            setPopup(CLOUD_POPUP);
        }
    };

    const onCopy = () => {
        navigator.clipboard.writeText('pip install "dash[cloud]"');
    };

    return (
        <>
            <button className={className} onClick={onClick}>
                <CloudSlashIcon
                    className='dash-debug-menu__icon'
                    width={16}
                    height={16}
                    fill='currentColor'
                />{' '}
                Plotly Cloud
            </button>
            {isOpen ? (
                <div className='plotly-cloud-modal-overlay'>
                    <div className='plotly-cloud-modal-content'>
                        <div className='plotly-cloud-modal-header'>
                            <h3 key='modal-title'>Plotly Cloud</h3>
                            <button
                                key='modal-close'
                                className='plotly-cloud-modal-close'
                                onClick={() => setPopup('')}
                            >
                                ×
                            </button>
                        </div>
                        <div
                            key='modal-body'
                            className='plotly-cloud-modal-body'
                        >
                            <div>
                                Install the extension to publish to Plotly
                                Cloud.
                            </div>
                            <div className='plotly-cloud-copy-install'>
                                <span>{'pip install "dash[cloud]"'}</span>
                                <button
                                    onClick={onCopy}
                                    className='plotly-cloud-modal-button'
                                >
                                    Copy
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            ) : null}
        </>
    );
};

export default PlotlyCloud;
