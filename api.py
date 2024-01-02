import inspect
import os

from jinja2 import Environment, FileSystemLoader
from parse import parse
from requests import Session as RequestsSession
from webob import Request, Response
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter


class API:
    def __init__(self, templates_dir="templates"):
        self._routes = {}
        self._template_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )
        self._exception_handler = None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def handle_request(self, request):
        response = Response()  # wrapper object around response
        handler, kwargs = self.find_handler(request_path=request.path)
        try:
            if not handler:
                self.default_response(response)
                return response
            handler_is_function = inspect.isfunction(handler)
            if handler_is_function:
                handler(request, response, **kwargs)
                return response
            # handler is class
            handler = getattr(handler(), request.method.lower(), None)
            if handler is None:
                raise AttributeError("Method not allowed", request.method)

            handler(request, response, **kwargs)
        except Exception as e:
            if self._exception_handler is None:
                raise e
            else:
                self._exception_handler(request, response, e)
        return response

    def find_handler(self, request_path):
        for path, handler in self._routes.items():
            parse_result = parse(
                path, request_path
            )  # match request path with existing path in system and gets arguments values in path
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def route(self, path):
        # register routes and its handler function
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def __call__(self, environ, start_response):
        request = Request(environ)  # wrapper object around request
        response = self.handle_request(request)
        return response(environ, start_response)

    def test_session(self, base_url="http://testserver"):
        """
        since python's Requests library only ships with a single Transport Adapter, the HTTPAdapter,
        we'd have to fire up Gunicorn before each test run in order to use it in the unit tests.
        That defeats the purpose of unit tests, though: Unit tests should be self-sustained.
        Fortunately, we can use the WSGI Transport Adapter for Requests library to create
        a test client that will make the tests self-sustained.
        """
        session = RequestsSession()  # test client
        session.mount(
            prefix=base_url, adapter=RequestsWSGIAdapter(self)
        )  # any request made using this test_session whose URL starts with the given prefix, will use the given RequestsWSGIAdapter.
        return session

    def add_route(self, path, handler):
        msg = f"Route already exists: {path}."
        assert path not in self._routes, msg

        self._routes[path] = handler

    def template(self, template_name, context=None):
        if context is None:
            context = {}
        return self._template_env.get_template(template_name).render(**context)

    def add_exception_handler(self, exception_handler):
        self._exception_handler = exception_handler
