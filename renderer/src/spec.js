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
                style: {color: 'blue', fontSize: 20}
            },
            children: 'paragram',
            droppable: true
        },
        {
            type: 'input',
            onChange: true
        },
        {
            type: 'Header',
            props: {name: 'rolo yoloz'},
            draggable: true
        },
        {
            type: 'div',
            props: {id: 'd_2'},
            children: [
                {
                    type: 'div',
                    props: {id: 'd_2_0'},
                    children: [
                        {
                            type: 'div',
                            props: {id: 'd_2_0_0'}
                        },
                        {
                            type: 'div',
                            props: {id: 'd_2_0_1'}
                        }
                    ]
                },
                {
                    type: 'div',
                    props: {id: 'd_2_1'},
                    children: [
                        {
                            type: 'div',
                            props: {id: 'd_2_1_0'}
                        }
                    ]
                }
            ]
        }
    ]
};
