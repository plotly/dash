from abc import ABC, abstractmethod

class BaseServerFactory(ABC):
    def __call__(self, server, *args, **kwargs):
        # Default: WSGI
        return server(*args, **kwargs)

    @abstractmethod
    def create_app(self, name="__main__", config=None):
        pass

    @abstractmethod
    def register_assets_blueprint(self, app, blueprint_name, assets_url_path, assets_folder):
        pass

    @abstractmethod
    def register_error_handlers(self, app):
        pass

    @abstractmethod
    def add_url_rule(self, app, rule, view_func, endpoint=None, methods=None):
        pass

    @abstractmethod
    def before_request(self, app, func):
        pass

    @abstractmethod
    def after_request(self, app, func):
        pass

    @abstractmethod
    def run(self, app, host, port, debug, **kwargs):
        pass

    @abstractmethod
    def make_response(self, data, mimetype=None, content_type=None):
        pass

    @abstractmethod
    def jsonify(self, obj):
        pass

    @abstractmethod
    def get_request_adapter(self):
        pass

