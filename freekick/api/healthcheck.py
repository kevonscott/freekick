from flask_restful import Resource


class HealthCheckApi(Resource):
    def get(self):
        return "ok", 200
