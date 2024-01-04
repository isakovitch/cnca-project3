from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Usage out of https://pypi.org/project/prometheus-flask-exporter
metrics = PrometheusMetrics(app)
by_path_counter = metrics.counter(
    'by_path_counter', 'Request count by request paths',
    labels={'path': lambda: request.path}
)
by_method_counter = metrics.counter(
    'by_method_counter', 'Request count by verb', 
    labels={'method': lambda: request.method})
# static information as metric
metrics.info('app_info', 'Frontend', version='0.0.1')

@app.route("/")
@by_path_counter
@by_method_counter
def homepage():
    return render_template("main.html")

# https://knowledge.udacity.com/questions/735508
class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
@app.route("/403")
@by_path_counter
@by_method_counter
def status_code_403():
    status_code = 403
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
@app.route("/404")
@by_path_counter
@by_method_counter
def status_code_404():
    status_code = 404
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
@app.route("/500")
@by_path_counter
@by_method_counter
def status_code_500():
    status_code = 500
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
@app.route("/503")
@by_path_counter
@by_method_counter
def status_code_503():
    status_code = 503
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

if __name__ == "__main__":
    app.run()
