from dash import register_page

register_page(__name__)

raise Exception("files in directories starting with . should not be imported")
