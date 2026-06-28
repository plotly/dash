# The default upload api endpoint
# The du.configure_upload can change this
upload_api = "/API/resumable"

# Needed if using a proxy; when dash.Dash is used
# with a `requests_pathname_prefix`.
# The front-end will prefix this string to the requests
# that are made to the proxy server
requests_pathname_prefix = "/"

# From dash source code:
# Note that `requests_pathname_prefix` is the prefix for the AJAX calls that
# originate from the client (the web browser) and `routes_pathname_prefix` is
# the prefix for the API routes on the backend (this flask server).
# `url_base_pathname` will set `requests_pathname_prefix` and
# `routes_pathname_prefix` to the same value.
# If you need these to be different values then you should set
# `requests_pathname_prefix` and `routes_pathname_prefix`,
# not `url_base_pathname`.
routes_pathname_prefix = "/"
