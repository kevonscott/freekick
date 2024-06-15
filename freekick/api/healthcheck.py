from flask_restx import Resource


class HealthCheckApi(Resource):
    def get(self):
        return "ok", 200
