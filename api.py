import inspect

from parse import parse
from requests import Session as RequestsSession
from webob import Request, Response
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter


def re_raise_error(err, message):
    err.args = (message,)
    raise


class API:
    def __init__(self):
        self._routes = {}

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def handle_request(self, request):
        response = Response()  # wrapper object around response
        handler, kwargs = self.find_handler(request_path=request.path)
        if not handler:
            self.default_response(response)
            return response
        handler_is_function = inspect.isfunction(handler)
        if handler_is_function:
            handler(request, response, **kwargs)
            return response
        # handler is class
        handler = getattr(handler(), request.method.lower())
        if handler is None:
            raise AttributeError("Method not allowed", request.method)

        handler(request, response, **kwargs)
        return response

    def find_handler(self, request_path):
        for path, handler in self._routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def route(self, path):
        msg = f"Route already exists: {path}"
        assert path not in self._routes, msg

        # register routes and its handler function
        def wrapper(handler):
            self._routes[path] = handler
            return handler

        return wrapper

    def __call__(self, environ, start_response):
        request = Request(environ)  # wrapper object around request body
        response = self.handle_request(request)
        return response(environ, start_response)

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session
