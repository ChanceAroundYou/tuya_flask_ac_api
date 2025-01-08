import configparser

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from air_conditioner import air_conditioner_factory

# 读取配置文件
config = configparser.ConfigParser()
config.read("config.ini")

ACCESS_ID = config["tuya"]["ACCESS_ID"]
ACCESS_KEY = config["tuya"]["ACCESS_KEY"]
DEVICE_ID = config["tuya"]["DEVICE_ID"]

HOST = config["server"]["HOST"]
PORT = int(config["server"]["PORT"])


class Control(BaseModel):
    power: int | None = None
    mode: int | None = None
    fan_speed: int | None = None
    temperature: int | None = None


ac = air_conditioner_factory(DEVICE_ID, ACCESS_ID, ACCESS_KEY)
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
    uvicorn.run(app, host=HOST, port=PORT, workers=1)
