// Custom HTML tags need to be added to a global namespace for type safety
// Registering them here is the approach react-markdown's authors endorse
// (https://github.com/remarkjs/react-markdown/issues/622)
import 'react';

declare global {
    namespace JSX {
        interface IntrinsicElements {
            dcclink: React.HTMLAttributes<HTMLElement>;
            dccmarkdown: React.HTMLAttributes<HTMLElement>;
            dashmathjax: React.HTMLAttributes<HTMLElement>;
        }
    }
}
