import time
from flask import Flask, render_template, request, Response, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from jaeger_client import Config

# import pymongo
# from flask_pymongo import PyMongo

app = Flask(__name__)

###################################################################
## Prmetheus
###################################################################
# Usage out of https://pypi.org/project/prometheus-flask-exporter
metrics = PrometheusMetrics(app)

# static information as metric
metrics.info('app_info', 'Backend', version='0.0.1')
by_path_counter = metrics.counter(
    'by_path_counter', 'Request count by request paths',
    labels={'path': lambda: request.path}
)
by_method_counter = metrics.counter(
    'by_method_counter', 'Request count by verb', 
    labels={'method': lambda: request.method})
by_status_counter = metrics.counter(
    'by_status_counter', 'Request count by http status', 
    labels={'status': lambda: Response.status_code})

###################################################################
## Jaeger
###################################################################
def init_tracer(service):    
    config = Config(
        config={"sampler": {"type": "const", "param": 1,}, "logging": True,},
        service_name=service,
    )
    # this call also sets opentracing.tracer
    return config.initialize_tracer()
tracer = init_tracer("backend")

# As stated in https://knowledge.udacity.com/questions/735508
# To keep things simple we will generate errors using dedicated endpoints and skip setup of a mongoDB
# app.config["MONGO_DBNAME"] = "example-mongodb"
# app.config[
#     "MONGO_URI"
# ] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

# mongo = PyMongo(app)


@app.route("/")
@by_path_counter
@by_method_counter
@by_status_counter
def homepage():
    with tracer.start_span("Root") as root_span:        
        return "Hello World"


@app.route("/api")
@by_path_counter
@by_method_counter
@by_status_counter
def my_api():
    with tracer.start_span("Api") as api_span:
        answer = "something"
        time.sleep(10)
        return jsonify(repsonse=answer)

# https://knowledge.udacity.com/questions/735508
# @app.route("/star", methods=["POST"])
# def add_star():
#     star = mongo.db.stars
#     name = request.json["name"]
#     distance = request.json["distance"]
#     star_id = star.insert({"name": name, "distance": distance})
#     new_star = star.find_one({"_id": star_id})
#     output = {"name": new_star["name"], "distance": new_star["distance"]}
#     return jsonify({"result": output})


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
@by_status_counter
def status_code_403():
    status_code = 403
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
@app.route("/404")
@by_path_counter
@by_method_counter
@by_status_counter
def status_code_404():
    status_code = 404
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
@app.route("/500")
@by_path_counter
@by_method_counter
@by_status_counter
def status_code_500():
    status_code = 500
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )
@app.route("/503")
@by_path_counter
@by_method_counter
@by_status_counter
def status_code_503():
    status_code = 503
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

if __name__ == "__main__":
    app.run()
