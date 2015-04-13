def WriteTemplate(name_of_block, list_of_elements):
    template = '\n'.join(list_of_elements)
    with open('templates/'+name_of_block + '.html', 'w') as f:
        f.write(template)


def HTMLElement(element='div', attributes={}, content=''):
        element = element
        attributes = attributes
        if element in ['input', 'img']:
            is_closing = False
        else:
            is_closing = True
        if not is_closing and content != '':
            raise Exception('Cant have content in a non-closing HTML tag!')

        if element in ['input', 'select'] and 'name' not in attributes:
            raise Exception('"name" attribute not found in {}. '
                            'This element will not appear in '
                            'the app_state.'.format(element))

        content = content

        el = '<{}'.format(element)
        for attribute, value in attributes.iteritems():
            el += ' {}="{}"'.format(attribute, value)
        el += '>'

        el += content

        if is_closing:
            el += '</{}>'.format(element)
        return el
