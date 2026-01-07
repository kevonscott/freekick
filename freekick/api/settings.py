from flask_restx import Namespace, Resource, fields

from freekick.service import get_setting, update_setting, SettingDTO

setting_ns = Namespace("settings", description="App Settings")
setting_model = setting_ns.model(
    "Setting",
    {
        "league": fields.String,
        "estimator": fields.String,
        "is_default": fields.Boolean,
        "models": fields.List(fields.String)

    }
)

@setting_ns.route("/setting")
class SettingApi(Resource):
    @setting_ns.doc("get_settings")
    @setting_ns.marshal_with(setting_model)
    def get(self):
        """Query the app runtime settings."""
        setting_dto = get_setting()
        print("==================")
        print(setting_dto)
        return setting_dto, 200

    @setting_ns.doc("update_settings")
    @setting_ns.expect(setting_model)
    def put(self, data):
        setting_dto: SettingDTO = SettingDTO(**data)
        # update_setting(setting_dto)
        return "ok", 200
