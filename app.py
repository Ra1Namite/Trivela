from api import API

app = API()


def custom_exception_handler(req, res, exception_cls):
    res.text = str(exception_cls)


app.add_exception_handler(custom_exception_handler)


@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"


@app.route("/about")
def about(request, response):
    response.text = "Hello from the ABOUT page"


@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"


@app.route("/tell/{num_1:d}/{num_2:d}")
def sum(request, response, num_1, num_2):
    total = int(num_1) + int(num_2)
    response.text = f"{num_1} + {num_2} = {total}"


@app.route("/book")
class BookResource:
    def get(self, req, res):
        res.text = "Books Page"

    def post(self, req, res):
        res.text = "Endpoint to create a book"


def handler(req, res):
    res.text = "sample"


app.add_route("/sample", handler)


@app.route("/template")
def template_handler(req, res):
    res.body = app.template(
        "index.html", context={"name": "Rambo", "title": "Food"}
    ).encode()


@app.route("/exception")
def exception_throwing_handler(req, res):
    raise AssertionError("This handler should not be used.")
