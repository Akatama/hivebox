from fastapi import FastAPI
import toml

app = FastAPI()
pyproject = toml.load("pyproject.toml")


@app.get("/version")
async def root():
    return {"version": f"{pyproject['project']['version']}"}
