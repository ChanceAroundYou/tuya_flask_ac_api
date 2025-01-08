from tuya_connector import TuyaOpenAPI
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

# ACCESS_ID = "sk3jdv43nrvq8txt73ce"
# ACCESS_KEY = "377b9fcef2c745fc94b8b0501929ae05"
# DEVICE_ID = "6c0acdc7f465cbd5c63p6b"
ACCESS_ID = "7u3fhafa9vnkga4q74dy"
ACCESS_KEY = "cfd2ea809657436db043114165fd9156"
DEVICE_ID = "6c1b72b269c836ed16yuur"

API_ENDPOINT = "https://openapi.tuyacn.com"
MQ_ENDPOINT = "wss://mqe.tuyacn.com:8285/"

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
        status = self.openapi.get(f"/v1.0/devices/{self.device_id}/status")
        print(status)
        status = {each["code"]: int(each["value"]) for each in status["result"]}

        self.power = status["power"]
        self.mode = status["mode"]
        self.temperature = status["temp"]
        self.fan_speed = status["wind"]

        status = {
            'power': self.power,
            'mode': self.mode,
            'fan_speed': self.fan_speed,
            'temperature': self.temperature,
        }
        return status

    def set_power(self, power):
        assert isinstance(power, int)
        assert power in [0, 1]

        self.power = power
        
        if power:
            self._command("PowerOn", 'PowerOn')
        else:
            self._command("PowerOff", 'PowerOff')

    def set_mode(self, mode):
        if not self.power:
            self.power = 1

        assert isinstance(mode, int)
        assert mode in range(5)

        self.mode = mode
        if mode == 4:
            self.fan_speed = 1

        self._command("M", mode)

    def set_fan_speed(self, fan_speed):
        if not self.power:
            return

        assert isinstance(fan_speed, int)
        assert fan_speed in range(4)

        self.fan_speed = fan_speed
        self._command("F", fan_speed)

    def set_temperature(self, temperature):
        if not self.power:
            return

        assert isinstance(temperature, int)
        assert temperature in range(self.min_temperature, self.max_temperature+1)

        self.temperature = temperature
        self._command("T", self.temperature)
        

class Control(BaseModel):
    power: Optional[int] = None
    mode: Optional[int] = None
    fan_speed: Optional[int] = None
    temperature: Optional[int] = None


openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()
ac = AirConditioner(DEVICE_ID, openapi)
# 使用fastapi建立一个web服务，接收请求控制空调
app = FastAPI()

@app.post("/control")
def control(control: Control):
    if control.power is not None:
        ac.set_power(control.power)
    if control.mode is not None:
        ac.set_mode(control.mode)
    if control.fan_speed is not None:
        ac.set_fan_speed(control.fan_speed)
    if control.temperature is not None:
        ac.set_temperature(control.temperature)
    status = ac.get_status()
    return status

@app.get("/status")
def status():
    return ac.get_status()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10223, workers=1)
