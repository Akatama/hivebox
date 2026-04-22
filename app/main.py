from fastapi import FastAPI, HTTPException
from .sensebox import get_temperatures, SENSEBOX_IDS
from .exceptions import OpenSenseMapAPIError
import toml

app = FastAPI()
pyproject = toml.load("pyproject.toml")


@app.get("/version")
async def version():
    return {"version": f"{pyproject['project']['version']}"}


@app.get("/temperature")
async def get_temperature():
    try:
        temps = get_temperatures(SENSEBOX_IDS)
    except OpenSenseMapAPIError as opensense_map_api_error:
        raise HTTPException(
            status_code=502, detail="Error communicating with openSenseMap API"
        ) from opensense_map_api_error

    if not temps:
        raise HTTPException(
            status_code=404, detail="No recent temperature data available"
        )

    average_temp = round(sum(temps) / len(temps), 2)
    return {
        "temperature": average_temp,
    }
