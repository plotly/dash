import {useRef, useEffect, useState} from 'react';
import {createPortal} from 'react-dom';

export const NewWindow = props => {
    const windowRef = useRef(null);
    const containerRoot = useRef(null);
    const [ready, setReady] = useState(false);

    // run only once at setup
    useEffect(() => {
        if (props.open) {
            windowRef.current = window.open(
                '',
                String(props.name),
                `width=${window.screen.availWidth},top=${window.screen.availHeight}`
            );

            containerRoot.current = document.createElement('div');
            containerRoot.current.id = 'CyContainer';
            windowRef.current.document.body.appendChild(containerRoot.current);
            setTimeout(() => {
                props.rebindEvents();
                //console.log('CHANGED');
            }, 2000);

            setReady(true);
        } else {
            //windowRef.current?.close();
            setReady(false);
        }

        //console.log(windowRef)
        //console.log(containerRoot)
    }, [props.open]);

    return open && ready
        ? createPortal(
              props.children,
              windowRef.current.document.getElementById('CyContainer')
          )
        : props.children;
};
