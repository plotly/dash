import React, {useEffect, useMemo} from 'react';
import {isNil} from 'ramda';

import LoadingElement from '../utils/_LoadingElement';
import {LinkProps} from '../types';

type LinkComponentProps = LinkProps & {
    setProps?: (props: Record<string, unknown>) => void;
};

/**
 * Link allows you to create a clickable link within a multi-page app.
 *
 * For links with destinations outside the current app, `html.A` is a better
 * component to use.
 */
const Link = ({
    refresh = false,
    scrollToTop = true,
    ...props
}: LinkComponentProps) => {
    const {className, style, id, href, children, title, target, setProps} =
        props;
    const cleanUrl = window.dash_clientside.clean_url;
    const sanitizedUrl = useMemo(() => {
        return href ? cleanUrl(href) : undefined;
    }, [href]);

    const updateLocation = (e: React.MouseEvent<HTMLAnchorElement>) => {
        const hasModifiers = e.metaKey || e.shiftKey || e.altKey || e.ctrlKey;

        if (hasModifiers) {
            return;
        }
        if (target !== '_self' && !isNil(target)) {
            return;
        }
        // prevent anchor from updating location
        e.preventDefault();
        if (refresh) {
            window.location.href = sanitizedUrl as string;
        } else {
            window.history.pushState({}, '', sanitizedUrl);
            window.dispatchEvent(new CustomEvent('_dashprivate_pushstate'));
        }
        if (scrollToTop) {
            window.scrollTo(0, 0);
        }
    };

    useEffect(() => {
        if (sanitizedUrl && sanitizedUrl !== href) {
            setProps?.({
                _dash_error: new Error(`Dangerous link detected:: ${href}`),
            });
        }
    }, [href, sanitizedUrl]);

    return (
        <LoadingElement>
            {loadingProps => (
                <a
                    id={id}
                    className={className}
                    style={style}
                    href={sanitizedUrl}
                    onClick={updateLocation}
                    title={title}
                    target={target}
                    {...loadingProps}
                >
                    {isNil(children) ? sanitizedUrl : children}
                </a>
            )}
        </LoadingElement>
    );
};

export default Link;
