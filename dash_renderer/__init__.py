# For reasons that I don't fully understand,
# unless I include __file__ in here, the packaged version
# of this module will just be a .egg file, not a .egg folder.
# And if it's just a .egg file, it won't include the necessary
# dependencies from MANIFEST.in.
# Found the __file__ clue by inspecting the `python setup.py install`
# command in the dash_html_components package which printed out:
# `dash_html_components.__init__: module references __file__`
# TODO - Understand this better
__file__
