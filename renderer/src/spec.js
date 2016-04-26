export default {
    props: {
        id: 'test',
        style: {},
        className: 'parent'
    },
    type: 'div',
    children: [
        {

            type: 'p',
            props: {
                id: 'child',
                style: {fontSize: 20}
            },
            children: 'basic <p> component',
            droppable: true

            /*
             * since "editable-div-1" depends on "editable-div-2",
             * if "editable-div-2" changes then 2 POSTs are made:
             * 1 - update "editable-div-1" with new values
             * 2 - following that, update "child" with new values
             */
            dependencies: ['input-1', 'input-2']
        },

        {
            type: 'InputControl',
            props: {
                id: 'input-1',
                placeholder: 'input 1'
            },
            dependencies: ['input-2']
        },

        {
            type: 'InputControl',
            props: {
                id: 'input-2',
                placeholder: 'input 2'
            }
        },

        {
            type: 'EditableDiv',
            props: {
                editable: true,
                text: 'basic editable div',
                style: {
                    fontSize: 40
                }
            }
        }


    ]
};
