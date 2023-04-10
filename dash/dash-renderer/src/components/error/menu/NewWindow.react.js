import {useRef, useState, useLayoutEffect, useEffect} from 'react';
import {createPortal} from 'react-dom';

export const NewWindow = props => {
    const windowRef = useRef(null);
    const containerRoot = useRef(null);
    const [ready, setReady] = useState(false);

    const useEnhancedEffect =
        typeof window !== 'undefined' ? useLayoutEffect : useEffect;

    useEnhancedEffect(() => {
        //`width=${window.screen.availWidth},top=${window.screen.availHeight}`

        let params = 'width=' + screen.width;
        params += ', height=' + screen.height;
        params += ', top=0, left=0';
        params += ', fullscreen=no';
        params += ', directories=no';
        params += ', location=no';
        params += ', menubar=no';
        params += ', resizable=no';
        params += ', scrollbars=no';
        params += ', status=no';
        params += ', toolbar=no';

        if (props.open) {
            windowRef.current = window.open('', String(props.name), params);

            /*       if (windowRef.current === null) {
                console.log('window value is null')
                windowRef.current = window.open(
                    '',
                    String(props.name),
                    params
                )
            } else {
                console.log('>>>> window exists')
            }
 */
            // We need to find a better way or find a way to resolved the issues when
            // https://stackoverflow.com/questions/172748/how-to-show-fullscreen-popup-window-in-javascript
            if (
                windowRef.current.outerWidth < screen.availWidth ||
                windowRef.current.outerHeight < screen.availHeight
            ) {
                // windowRef.current.moveTo(0, 0);
                //   windowRef.current.resizeTo(screen.availWidth-10, screen.availHeight-10);
            }

            // Clone all CSS from the original page to the new window
            props.css.forEach(htmlElement => {
                windowRef.current.document.head.appendChild(
                    htmlElement.cloneNode(true)
                );
            });

            containerRoot.current = document.createElement('div');
            containerRoot.current.id = 'CyContainerRoot';
            windowRef.current.document.body.appendChild(containerRoot.current);
            setReady(true);
        } else {
            windowRef.current?.close();
            setReady(false);
        }

        return () => {
            windowRef.current?.close();
            setReady(false);
        };
    }, [props.open]);

    return open && ready
        ? createPortal(
              props.children,
              windowRef.current.document.getElementById('CyContainerRoot')
          )
        : props.children;
};
