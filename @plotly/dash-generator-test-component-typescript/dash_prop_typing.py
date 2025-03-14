ignore_props = ['ignored_prop']

custom_imports = {
    "*": ["import json"]
}

def generate_style(*_):
    return "dict"

custom_props = {
    "*": {
        "obj": generate_style
    }
}
