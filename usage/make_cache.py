from flask_caching import Cache
from dash import get_app

app = get_app()
serverside_cache = Cache(
    app.server,
    config={
        # 'CACHE_TYPE': 'redis',
        # Note that filesystem cache doesn't work on systems with ephemeral
        # filesystems like Heroku.
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        # should be equal to maximum number of users on the app at a single time
        # higher numbers will store more data in the filesystem / redis cache
        "CACHE_THRESHOLD": 200,
    },
)
