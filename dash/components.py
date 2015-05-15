def element(element='div', attributes={}, content=''):
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


def graph(id):
    return element('iframe', dict(
        id=id,
        src="https://plot.ly/~playground/7.embed",
        style="width: 100%; height: 500px; border: none;"
    ))
