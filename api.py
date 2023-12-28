from webob import Request, Response


class API:
    def __init__(self):
        self._routes = {}

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def handle_request(self, request):
        response = Response()  # wrapper object around response body
        try:
            handler = self._routes[request.path]
            handler(request, response)
            return response
        except KeyError:
            self.default_response(response)
            return response

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
