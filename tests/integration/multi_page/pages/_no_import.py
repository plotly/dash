from dash import register_page

register_page(__name__)

raise Exception("files starting with _ should not be imported")
