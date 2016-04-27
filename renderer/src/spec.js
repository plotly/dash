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
        },

        // dependency tree

        {
            type: 'InputControl',
            props: {
                id: 'A',
                placeholder: 'A'
            },
            dependencies: []
        },
        {
            type: 'InputControl',
            props: {
                id: 'B',
                placeholder: 'B'
            },
            dependencies: ['A']
        },
        {
            type: 'InputControl',
            props: {
                id: 'C',
                placeholder: 'C'
            },
            dependencies: ['A']
        },
        {
            type: 'InputControl',
            props: {
                id: 'D',
                placeholder: 'D'
            },
            dependencies: ['A']
        },
        {
            type: 'InputControl',
            props: {
                id: 'E',
                placeholder: 'E'
            },
            dependencies: ['B', 'C']
        },
        {
            type: 'InputControl',
            props: {
                id: 'F',
                placeholder: 'F'
            },
            dependencies: ['A', 'D']
        },


        {
            type: 'EditableDiv',
            props: {
                id: 'editable-div-1',
                editable: true,
                text: 'basic editable div',
                style: {
                    fontSize: 25
                }
            }
        },

        {
            type: 'EditableDiv',
            props: {
                id: 'editable-div-2',
                editable: true,
                text: 'another editable div',
                style: {
                    fontSize: 25
                }
            }
        }


    ]
};
