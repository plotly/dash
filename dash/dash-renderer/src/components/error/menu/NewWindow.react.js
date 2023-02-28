import {useMemo} from 'react';
import {createPortal} from 'react-dom';

export const NewWindow = ({name, children}) => {
    // doesn't create a new window after you close it... need to figure out a way

    const newWindow = useMemo(
        () =>
            window.open(
                '', // this should be left blank
                String(name),
                `width=${window.screen.availWidth},top=${window.screen.availHeight}`
            ),
        []
    ); // []  is mandatory since otherwise a new windows will open / focus on each re-render of anything in the app

    newWindow.blur();

    /* css.forEach(htmlElement => {
      newWindow.document.head.appendChild(htmlElement.cloneNode(true));
  }); */

    if (
        newWindow.outerWidth < screen.availWidth ||
        newWindow.outerHeight < screen.availHeight
    ) {
        newWindow.moveTo(0, 0);
        newWindow.resizeTo(screen.availWidth, screen.availHeight);
    }

    //useEffect(() => () => newWindow.close());
    //newWindow.
    return createPortal(children, newWindow.document.body);
};

/*  
  const findCSS = () => {
    return document.querySelectorAll('link, style');
} */

/*   const modalRoot = document.getElementById("overlay-portal")!;


//we use useRef here to only initialize el once and not recreate it on every rerender, which would cause bugs
  const el = useRef(document.createElement("div"));

  useEffect(() => {
    modalRoot.appendChild(el.current);

    return () => {
      modalRoot.removeChild(el.current);
    };
  }, []); */

//  const openWindow = () => {

//if (popup && !popup.closed) {
//  popup.focus();
/* or do something else, e.g. close the popup or alert a warning */
//} else {
/*     const divText = document.getElementById('testtest').outerHTML;
      const popup = window.open('', 'popup', 'fullscreem=1, location=0, menubar=0, resizable=0, scrollbars=0,status=0,toolbar=no, titlebar=no');
      if (popup.outerWidth < screen.availWidth || popup.outerHeight < screen.availHeight)
      {
        popup.moveTo(0,0);
        popup.resizeTo(screen.availWidth, screen.availHeight);
      }
      const doc = popup.document;
      doc.open();
      doc.write('<html><head><title>Print it!</title><link rel="stylesheet" type="text/css" href="styles.css"></head><body>');
      doc.write(divText);
      win.document.write('</body></html>');
      doc.close();
   */ // }
// }
//}
