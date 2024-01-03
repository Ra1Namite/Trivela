from webob import Request


class BaseMiddleware:
    def __init__(self):
        pass

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def process_request(self, req):
        pass

    def process_response(self, req, res):
        pass


class MiddlewareHandler:
    def __init__(self, app):
        self.app = app
        self._middleware_instances = []

    def add(self, middleware_cls):
        middleware_instance = middleware_cls()
        if middleware_instance not in self._middleware_instances:
            self._middleware_instances.append(middleware_instance)

    def handle_request(self, request):
        for m_ware in self._middleware_instances:
            m_ware.process_request(request)
        response = self.app.handle_request(request)
        for m_ware in self._middleware_instances:
            m_ware.process_response(request, response)
        return response

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)
