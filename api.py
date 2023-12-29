from parse import parse
from webob import Request, Response


class API:
    def __init__(self):
        self._routes = {}

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def handle_request(self, request):
        response = Response()  # wrapper object around response
        handler, kwargs = self.find_handler(request_path=request.path)
        if handler:
            handler(request, response, **kwargs)
        else:
            self.default_response(response)
        return response

    def find_handler(self, request_path):
        for path, handler in self._routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def route(self, path):
        # register routes and its handler function
        def wrapper(handler):
            self._routes[path] = handler
            return handler

        return wrapper

    def __call__(self, environ, start_response):
        request = Request(environ)  # wrapper object around request body
        response = self.handle_request(request)
        return response(environ, start_response)
