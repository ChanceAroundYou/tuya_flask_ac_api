# air_conditioner.py

from tuya_connector import TuyaOpenAPI

API_ENDPOINT = "https://openapi.tuyacn.com"

class AirConditioner:
    modes = ["cool", "heat", "auto", "fan_only", "dry"]
    fan_speeds = ["auto", "low", "medium", "high"]
    min_temperature = 16
    max_temperature = 30

    def __init__(self, device_id, openapi: TuyaOpenAPI):
        self.device_id = device_id
        self.temperature = 26
        self.power = 0
        self.mode = 0
        self.fan_speed = 0
        self.openapi = openapi
        self.get_status()

    def _command(self, code, value):
        commands = {"commands": [{"code": code, "value": value}]}
        self.openapi.post(f"/v1.0/devices/{self.device_id}/commands", commands)

    def get_status(self):
        self.openapi.get("/v1.0/statistics-datas-survey")
        results = self.openapi.get(f"/v1.0/devices/{self.device_id}/status")["result"]
        status = {
            item["code"]: int(item["value"]) 
            for item in results
        }

        self.power = status["power"]
        self.mode = status["mode"]
        self.temperature = status["temp"]
        self.fan_speed = status["wind"]

        return {
            'power': self.power,
            'mode': self.mode,
            'fan_speed': self.fan_speed,
            'temperature': self.temperature,
        }

    def set_power(self, power):
        self._command("power", power)

    def set_mode(self, mode):
        self._command("mode", mode)

    def set_fan_speed(self, fan_speed):
        self._command("wind", fan_speed)

    def set_temperature(self, temperature):
        self._command("temp", temperature)
        
def air_conditioner_factory(device_id: str, access_id: str, access_key: str):
    openapi = TuyaOpenAPI(API_ENDPOINT, access_id, access_key)
    ac = AirConditioner(device_id, openapi)
    return ac
