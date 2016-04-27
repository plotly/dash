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
