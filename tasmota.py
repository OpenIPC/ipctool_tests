from contextlib import contextmanager
import time
import os
import requests


def check_ping(hostname):
    """Run ping and return 1 if success"""

    attempts = 1
    response = os.system("ping -c {} {} >/dev/null".format(attempts, hostname))
    # and then check the response...
    if response == 0:
        # Network is active
        return attempts
    return 0


def turn(host, req):
    """Send request to Tasmota device to turn it on/off"""

    response = requests.get("http://{}/cm?cmnd=Power%20{}".format(host, req))
    if response.status_code != 200:
        raise ValueError
    print(response.json())


@contextmanager
def updown(swname, controlip, **kwds):
    """Context manager for power on/off switch with `swname` and check its
    availability via pinging `controlip`"""

    warmup = kwds["warmup"]
    print("Turn on switch")
    turn(swname, "On")
    print("Waiting for {} seconds".format(warmup))
    try:
        time.sleep(kwds["warmup"])
        pings = 0
        total = 5
        for _ in range(total):
            pings += check_ping(controlip)
        print("{}/{} pings are successful".format(pings, total))
        if pings < 3:
            print("Pings are lower threshold")
            raise ConnectionError
        print("Start tests")
        yield None
    finally:
        print("Turn off switch")
        turn(swname, "Off")
