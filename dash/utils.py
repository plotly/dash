import os


def write_templates(blocks, app_name):
    runtime_template_dir = os.path.join('templates', 'runtime', app_name)
    if not os.path.exists(runtime_template_dir):
        os.makedirs(runtime_template_dir)

    for block in blocks:
        runtime_template_block = os.path.join(runtime_template_dir,
                                              block + '.html')
        with open(runtime_template_block, 'w') as f:
            template = '\n'.join(blocks[block])
            f.write(template)
