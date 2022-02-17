// NOTE: need to pin fontawesome-svg-core to <1.3 and free-*-svg-icons to <6
// or we break IE11
import {library} from '@fortawesome/fontawesome-svg-core';
import {faEyeSlash, faTrashAlt} from '@fortawesome/free-regular-svg-icons';
import {
    faEraser,
    faPencilAlt,
    faSort,
    faSortDown,
    faSortUp
} from '@fortawesome/free-solid-svg-icons';
import {
    faAngleLeft,
    faAngleRight,
    faAngleDoubleLeft,
    faAngleDoubleRight
} from '@fortawesome/free-solid-svg-icons';

library.add(
    faEraser,
    faEyeSlash,
    faPencilAlt,
    faSort,
    faSortDown,
    faSortUp,
    faTrashAlt,
    faAngleLeft,
    faAngleRight,
    faAngleDoubleLeft,
    faAngleDoubleRight
);
