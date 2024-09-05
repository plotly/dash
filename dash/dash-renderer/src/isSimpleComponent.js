import {includes, type} from 'ramda';

const SIMPLE_COMPONENT_TYPES = ['String', 'Number', 'Null', 'Boolean'];

export default component => includes(type(component), SIMPLE_COMPONENT_TYPES);
