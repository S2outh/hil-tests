import os
import subprocess
import pytest
from labgrid import Environment
import drivers.http_led_driver  # registers driver
import drivers.probe_rs_driver  # registers driver

COORD = os.environ["LG_COORDINATOR"]
PLACE = "flatsat"

MATCH_LED   = "*/test-indicator-led/NetworkService/led"
MATCH_LOWER_SENSOR = "*/lower-sensor-probers/NetworkService/probe-lower-sensor"
MATCH_UPPER_SENSOR_1 = "*/upper-sensor-1-probers/NetworkService/probe-upper-sensor-1"
MATCH_OPEN_LST_1 = "*/open-lst-1-probers/NetworkService/probe-open-lst-1"
MATCH_EPS = "*/eps-probers/NetworkService/probe-eps"
MATCH_UMBILICAL = "*/umbilical-probers/NetworkService/probe-umbilical"

def lg(*args, check=True):
    return subprocess.run(
        ["labgrid-client", "--coordinator", COORD, *args],
        text=True,
        capture_output=True,
        check=check,
    )

@pytest.fixture(scope="session", autouse=True)
def labgrid_session():
    lg("-p", PLACE, "delete", check=False)
    lg("-p", PLACE, "create", check=False)
    lg("-p", PLACE, "add-match", MATCH_LED, check=False)
    lg("-p", PLACE, "add-match", MATCH_LOWER_SENSOR, check=False)
    lg("-p", PLACE, "add-match", MATCH_UPPER_SENSOR_1, check=False)
    lg("-p", PLACE, "add-match", MATCH_OPEN_LST_1, check=False)
    lg("-p", PLACE, "add-match", MATCH_EPS, check=False)
    lg("-p", PLACE, "add-match", MATCH_UMBILICAL, check=False)
    print(lg("-p", PLACE, "show").stdout)

    # IMPORTANT: acquire before Environment() so RemotePlace can list resources
    lg("-p", PLACE, "acquire")

    try:
        env = Environment("env.yaml")
        t = env.get_target("main")
        t.get_driver("HttpLedDriver")  # LED ON via driver activation
        t.get_driver("ProbeRsDriver", name="probe-lower-sensor")
        t.get_driver("ProbeRsDriver", name="probe-upper-sensor-1")
        t.get_driver("ProbeRsDriver", name="probe-open-lst-1")
        t.get_driver("ProbeRsDriver", name="probe-eps")
        t.get_driver("ProbeRsDriver", name="probe-umbilical")

        yield t
    finally:
        # Optional: ensure driver hooks run before releasing place
        try:
            t.get_driver("ProbeRsDriver", name="probe-lower-sensor").deactivate()
            t.get_driver("ProbeRsDriver", name="probe-upper-sensor-1").deactivate()
            t.get_driver("ProbeRsDriver", name="probe-open-lst-1").deactivate()
            t.get_driver("ProbeRsDriver", name="probe-eps").deactivate()
            t.get_driver("ProbeRsDriver", name="probe-umbilical").deactivate()
        except Exception:
            pass
        try:
            t.get_driver("HttpLedDriver").deactivate()
        except Exception:
            pass
        # release place (will also make LED OFF if your driver runs on deactivate;
        # otherwise call driver.deactivate() explicitly before releasing)
        lg("-p", PLACE, "release", check=False)
