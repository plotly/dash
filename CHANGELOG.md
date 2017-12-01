# 0.19.0 - 2017-10-16
## Changed
- 🔒  CSRF protection measures were removed as CSRF style attacks are not relevant
to Dash apps. Dash's API uses `POST` requests with content type
`application/json` which are not susceptible to unwanted requests from 3rd
party sites. See https://github.com/plotly/dash/issues/141 for more.
- 🔒  Setting `app.server.secret_key` is no longer required since CSRF protection was
removed. Setting `app.server.secret_key` was difficult to document and
a very common source of confusion, so it's great that users won't get bitten
by this anymore :tada:

# 0.18.3 - 2017-09-08
## Added
- `app.config` is now a `dict` instead of a class. You can set config variables with
  `app.config['suppress_callback_exceptions'] = True` now. The previous class-based
  syntax (e.g. `app.config.suppress_callback_exceptions`) has been maintained for
  backwards compatibility

## Fixed
- 0.18.2 introduced a bug that removed the ability for dash to serve the app on
  any route besides `/`. This has been fixed.
- 0.18.0 introduced a bug with the new config variables when used in a multi-app setting.
  These variables would be shared across apps. This issue has been fixed.
  Originally reported in https://community.plot.ly/t/flask-endpoint-error/5691/7
- The config setting `supress_callback_exceptions` has been renamed to
  `suppress_callback_exceptions`. Previously, `suppress` was spelled wrong.
  The original config variable is kept for backwards compatibility.

# 0.18.3rc1 - 2017-09-08
The prerelease for 0.18.3

# 0.18.2 - 2017-09-07
## Added
- 🔧 Added an `endpoint` to each of the URLs to allow for multiple routes (https://github.com/plotly/dash/pull/70)

# 0.18.1 - 2017-09-07
## Fixed
- 🐛 If `app.layout` was supplied a function, then it used to be called excessively. Now it is called just once on startup and just once on page load. https://github.com/plotly/dash/pull/128

# 0.18.0 - 2017-09-07
## Changed
- 🔒  Removes the `/static/` folder and endpoint that is implicitly initialized by flask. This is too implicit for my comfort level: I worry that users will not be aware that their files in their `static` folder are accessible
- ⚡️  Removes all API calls to the Plotly API (https://api.plot.ly/), the authentication endpoints and decorators, and the associated `filename`, `sharing` and `app_url` arguments. This was never documented or officially supported and authentication has been moved to the [`dash-auth` package](https://github.com/plotly/dash-auth)
- ✏️ Sorts the prop names in the exception messages (#107)

## Added
- 🔧 Add two new `config` variables: `routes_pathname_prefix` and `requests_pathname_prefix` to provide more flexibility for API routing when Dash apps are run behind proxy servers. `routes_pathname_prefix` is a prefix applied to the backend routes and `requests_pathname_prefix` prefixed in requests made by Dash's front-end. `dash-renderer==0.8.0rc3` uses these endpoints.
- 🔧 Added id to KeyError exception in components (#112)


## Fixed
- ✏️  Fix a typo in an exception
- 🔧 Replaced all illegal characters in environment variable

##🔧 Maintenance
- 📝  Update README.md
- ✅  Fix CircleCI tests. Note that the [`dash-renderer`](https://github.com/plotly/dash-renderer) contains the bulk of the integration tests.
- 💄 Flake8 fixes and tests (fixes #99 )
- ✨ Added this CHANGELOG.md

# 0.17.3 - 2017-06-22
✨ This is the initial open-source release of Dash
