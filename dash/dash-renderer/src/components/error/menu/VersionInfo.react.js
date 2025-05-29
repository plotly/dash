import React, {useEffect, useState} from 'react';

import './VersionInfo.css';

const DAY_IN_MS = 86400000;

function compareVersions(v1, v2) {
    // Remove any non-numeric characters from the version strings
    // and anything after them (e.g. 1.2.3-rc.1 -> 1.2.3, 1.2.3+build.1 -> 1.2.3)
    v1 = v1.replace(/\.?[^0-9.].*$/, '');
    v2 = v2.replace(/\.?[^0-9.].*$/, '');

    const v1Parts = v1.split('.').map(Number);
    const v2Parts = v2.split('.').map(Number);

    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
        const part1 = v1Parts[i] || 0;
        const part2 = v2Parts[i] || 0;

        if (part1 > part2) return 1;
        if (part1 < part2) return -1;
    }

    return 0;
}

async function requestDashVersionInfo(config) {
    const {
        dash_version: currentDashVersion,
        dash_version_url: dashVersionUrl,
        python_version: pythonVersion,
        ddk_version: ddkVersion,
        plotly_version: plotlyVersion
    } = config;
    let cachedVersionInfo, cachedNewDashVersionLink, lastFetched;
    try {
        cachedVersionInfo = localStorage.getItem('cachedNewDashVersion');
        cachedNewDashVersionLink = localStorage.getItem(
            'cachedNewDashVersionLink'
        );
        lastFetched = localStorage.getItem('lastFetched');
    } catch (e) {
        // If localStorage is not available, return an empty object
        return {};
    }
    if (
        lastFetched &&
        Date.now() - Number(lastFetched) < DAY_IN_MS &&
        cachedVersionInfo
    ) {
        return {
            version: JSON.parse(cachedVersionInfo),
            link: cachedNewDashVersionLink
        };
    } else if (shouldRequestDashVersion(config)) {
        const queryParams = new URLSearchParams({
            dash_version: currentDashVersion,
            python_version: pythonVersion,
            ddk_version: ddkVersion,
            plotly_version: plotlyVersion
        }).toString();
        return fetch(dashVersionUrl + '?' + queryParams, {mode: 'cors'})
            .then(response => response.json())
            .then(body => {
                if (body && body.version && body.link) {
                    try {
                        localStorage.setItem(
                            'cachedNewDashVersion',
                            JSON.stringify(body.version)
                        );
                        localStorage.setItem(
                            'cachedNewDashVersionLink',
                            body.link
                        );
                        localStorage.setItem('lastFetched', Date.now());
                    } catch (e) {
                        // Ignore errors if localStorage is not available
                    }
                    return body;
                } else {
                    return {};
                }
            })
            .catch(() => {
                return {};
            });
    }
}

function shouldRequestDashVersion(config) {
    // If version check is disabled, return false to avoid
    // checking localStorage unnecessarily
    if (config.disable_version_check) {
        return false;
    }
    let showNotifications, lastFetched;
    try {
        showNotifications =
            localStorage.getItem('showNotifications') !== 'false';
        lastFetched = localStorage.getItem('lastFetched');
    } catch (e) {
        // If localStorage is not available, return false
        return false;
    }
    return (
        showNotifications &&
        (!lastFetched || Date.now() - Number(lastFetched) > DAY_IN_MS)
    );
}

function shouldShowUpgradeNotification(
    currentDashVersion,
    newDashVersion,
    config
) {
    // If version check is disabled, return false to avoid
    // checking localStorage unnecessarily
    if (config.disable_version_check) {
        return false;
    }
    let showNotifications, lastDismissed, lastDismissedVersion;
    try {
        showNotifications =
            localStorage.getItem('showNotifications') !== 'false';
        lastDismissed = localStorage.getItem('lastDismissed');
        lastDismissedVersion = localStorage.getItem('lastDismissedVersion');
    } catch (e) {
        // If localStorage is not available, return false
        return false;
    }
    if (
        newDashVersion === undefined ||
        compareVersions(currentDashVersion, newDashVersion) >= 0 ||
        !showNotifications
    ) {
        return false;
    } else if (
        lastDismissed &&
        Date.now() - Number(lastDismissed) > DAY_IN_MS
    ) {
        return true;
    } else if (
        lastDismissedVersion &&
        !lastDismissed &&
        compareVersions(lastDismissedVersion, newDashVersion) < 0
    ) {
        return true;
    } else {
        return !lastDismissed && !lastDismissedVersion;
    }
}

export const VersionInfo = ({config}) => {
    const [newDashVersion, setNewDashVersion] = useState(undefined);
    const [newDashVersionLink, setNewDashVersionLink] = useState(undefined);
    const [upgradeTooltipOpened, setUpgradeTooltipOpened] = useState(false);

    const setDontShowAgain = () => {
        // Set local storage to record the last dismissed notification
        try {
            localStorage.setItem('showNotifications', false);
        } catch (e) {
            // Ignore errors if localStorage is not available
        }
        setUpgradeTooltipOpened(false);
    };

    const setRemindMeLater = () => {
        // Set local storage to record the last dismissed notification
        try {
            localStorage.setItem('lastDismissed', Date.now());
        } catch (e) {
            // Ignore errors if localStorage is not available
        }
        setUpgradeTooltipOpened(false);
    };

    const setSkipThisVersion = () => {
        // Set local storage to record the last dismissed version
        try {
            localStorage.setItem('lastDismissedVersion', newDashVersion);
        } catch (e) {
            // Ignore errors if localStorage is not available
        }
        setUpgradeTooltipOpened(false);
    };

    useEffect(() => {
        requestDashVersionInfo(config).then(body => {
            if (body) {
                setNewDashVersionLink(body.link);
                setNewDashVersion(body.version);
            }
        });
    }, []);

    useEffect(() => {
        const hideUpgradeTooltip = e => {
            if (
                upgradeTooltipOpened &&
                !e.target.matches(
                    '.dash-debug-menu__version, .dash-debug-menu__version *'
                )
            ) {
                setUpgradeTooltipOpened(false);
            }
        };
        // Close the upgrade tooltip if the user clicks outside of it
        document.addEventListener('click', hideUpgradeTooltip);

        return () => document.removeEventListener('click', hideUpgradeTooltip);
    }, [upgradeTooltipOpened]);

    return (
        <div className='dash-debug-menu__version'>
            {upgradeTooltipOpened ? (
                <div className='dash-debug-menu__upgrade-tooltip'>
                    {newDashVersionLink ? (
                        <a target='_blank' href={newDashVersionLink}>
                            Read details
                        </a>
                    ) : null}
                    <button onClick={setSkipThisVersion}>
                        Skip this version
                    </button>
                    <button onClick={setRemindMeLater}>
                        Remind me tomorrow
                    </button>
                    <button onClick={setDontShowAgain}>
                        Silence all version notifications
                    </button>
                </div>
            ) : null}
            <span>v{config.dash_version}</span>
            {shouldShowUpgradeNotification(
                config.dash_version,
                newDashVersion,
                config
            ) ? (
                <button
                    className='dash-debug-menu__upgrade-button'
                    onClick={() =>
                        setUpgradeTooltipOpened(!upgradeTooltipOpened)
                    }
                >
                    Dash update available - v{newDashVersion}
                </button>
            ) : null}
        </div>
    );
};
