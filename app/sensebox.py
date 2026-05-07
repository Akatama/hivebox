import os
from datetime import datetime, timezone, timedelta
from .exceptions import OpenSenseMapAPIError
import requests

DEFAULT_SENSEBOX_IDS = (
    "5eba5fbad46fb8001b799786,5c21ff8f919bf8001adf2488,5ade1acf223bd80019a1011c"
)

SENSEBOX_IDS = os.getenv("SENSEBOX_IDS", DEFAULT_SENSEBOX_IDS).split(",")

API_URL = "https://api.opensensemap.org/boxes/"


def get_temperatures(sensebox_ids: list[str]):
    temps = []
    for sensebox_id in sensebox_ids:
        try:
            response = requests.get(f"{API_URL}/{sensebox_id}", timeout=10)

            response.raise_for_status()

            sensebox_data = response.json()

            sensors = sensebox_data.get("sensors")

            if sensors is None:
                print(
                    f"Warning: No 'sensors' list found for box ID {sensebox_id}. Skipping."
                )
                continue

            temp_sensor = None

            for sensor in sensors:
                if isinstance(sensor, dict) and sensor.get("title") == "Temperatur":
                    temp_sensor = sensor
                    break

            if not temp_sensor:
                print(
                    f"Warning: No Temperatur sensor found for box id {sensebox_id}. Skipping."
                )
                continue

            last_measurement = temp_sensor.get("lastMeasurement")

            if (
                last_measurement
                and last_measurement.get("value") is not None
                and last_measurement.get("createdAt")
            ):
                created_at = datetime.strptime(
                    last_measurement["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ).replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if now - created_at <= timedelta(hours=1):
                    temps.append(float(last_measurement["value"]))

        except requests.exceptions.HTTPError as http_error:
            print(
                f"Warning: HTTP error for sensebox_id '{sensebox_id}': {http_error}. Skipping."
            )
            continue
        except requests.exceptions.RequestException as request_error:
            raise OpenSenseMapAPIError(
                f"Warning: Network error for sensebox_id: '{sensebox_id}': {request_error}"
            ) from request_error
        except (ValueError, KeyError, TypeError) as e:
            print(
                f"Warning: Data processing error for sensebox_id: {sensebox_id}: {e}. Skipping"
            )
            continue

    return temps
