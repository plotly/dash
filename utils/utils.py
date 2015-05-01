def write_templates(fn, blocks, layout='base.html'):
    for block in blocks:
        with open('templates/dash/' + block + '.html', 'w') as f:
            template = '\n'.join(blocks[block])
            f.write(template)
