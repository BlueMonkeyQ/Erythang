import json
import os
from pathlib import Path

def getData(response):
    return response.json()

def toJson(data,filename):
    with open(Path(f"data/steam/example/{filename}.json"), "w") as f:
        json.dump(data, f, indent=4)

def fileExist(filename):
    return os.path.exists(Path(f"data/steam/example/{filename}.json"))

def getJson(filename):
    with open (Path(f"data/steam/example/{filename}.json"), "r") as f:
        data = json.load(f)
    return data