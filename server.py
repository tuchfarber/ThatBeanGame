from bottle import route, run

@route("/")
def hello():
    return "Hi"

run(host="localhost", port=8080, debug=True)