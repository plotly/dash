import plotly
from six import iteritems


def create_or_overwrite_dash_app(filename, sharing, app_url):
    required_args = {
        'filename': filename,
        'sharing': sharing,
        'app_url': app_url
    }
    for arg_name, arg_value in iteritems(required_args):
        if arg_value is None:
            raise Exception('{} is required'.format(arg_name))
    if sharing not in ['private', 'secret', 'public']:
        raise Exception(
            "The privacy argument must be equal "
            "to 'private', 'public', or 'secret'.\n"
            "You supplied '{}'".format(sharing)
        )
    payload = {
        'filename': filename,
        'share_key_enabled': True if sharing == 'secret' else False,
        'world_readable': True if sharing == 'public' else False,
        'app_url': app_url
    }

    try:
        # TODO - Handle folders
        res = plotly.api.v2.files.lookup(filename)
    except Exception as e:
        print(e)
        # TODO - How to check if it is a
        # plotly.exceptions.PlotlyRequestException?
        res_create = plotly.api.v2.dash_apps.create(payload)
        fid = res_create.json()['file']['fid']
    else:
        fid = res.json()['fid']
        # TODO - Does plotly.api call `raise_for_status`?
        res = plotly.api.v2.dash_apps.update(fid, payload)
        res.raise_for_status()
    return fid
