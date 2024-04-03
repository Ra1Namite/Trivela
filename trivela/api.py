import inspect
import os

from jinja2 import Environment, FileSystemLoader
from parse import parse
from requests import Session as RequestsSession
from webob import Request
from whitenoise import WhiteNoise
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

from .middleware import Middleware
from .response import Response


class API:
    def __init__(self, templates_dir="templates", static_dir="static"):
        self._routes = {}  # routes and its handler
        self._template_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )  # initialize jinja environment
        self._exception_handler = None  # custom exception handler
        self._white_noise = WhiteNoise(
            self.wsgi_app, root=static_dir
        )  # serving static contents
        self._middleware = Middleware(self)

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]
        if path_info.startswith("/static"):
            # requesting static content
            environ["PATH_INFO"] = path_info[
                len("/static") :
            ]  # remove static from path
            return self._white_noise(environ, start_response)  # serve static content
        return self._middleware(
            environ, start_response
        )  # run middlewares when not serving static contents

    def wsgi_app(self, environ, start_response):
        request = Request(environ)  # wrapper object around request
        response = self.handle_request(request)
        return response(environ, start_response)

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def handle_request(self, request):
        response = Response()  # wrapper object around response
        handler_data, kwargs = self.find_handler(request_path=request.path)
        try:
            if not handler_data:
                self.default_response(response)
                return response
            handler = handler_data["handler"]
            allowed_methods = handler_data["allowed_methods"]
            handler_is_function = inspect.isfunction(handler)
            if handler_is_function:
                if request.method.lower() not in allowed_methods:
                    raise AttributeError("Method not allowed", request.method)
            else:
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
        for path, handler_data in self._routes.items():
            parse_result = parse(
                path, request_path
            )  # match request path with existing path in system and gets arguments values in path
            if parse_result is not None:
                return handler_data, parse_result.named
        return None, None

    def route(self, path, allowed_methods=None):
        # register routes and its handler function
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def add_route(self, path, handler, allowed_methods=None):
        msg = f"Route already exists: {path}."
        assert path not in self._routes, msg
        if allowed_methods is None:
            allowed_methods = ("get", "post", "put", "patch", "delete", "options")

        self._routes[path] = {
            "handler": handler,
            "allowed_methods": allowed_methods,
        }  # register handler and allowed methods for given path

    def test_session(self, base_url="http://testserver"):
        """
        Build a test client to test the API without having to spin up the server.

        Since python's Requests library only ships with a single Transport Adapter, the HTTPAdapter,
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

    def template(self, template_name, context=None):
        # render html template
        if context is None:
            context = {}
        return self._template_env.get_template(template_name).render(**context)

    def add_exception_handler(self, exception_handler):
        # register custom exception handler
        self._exception_handler = exception_handler

    def add_middleware(self, middleware_cls):
        self._middleware.add(middleware_cls)
