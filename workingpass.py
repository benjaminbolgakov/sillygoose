shock_mock_path = "rigs:dhu3s:pi6:backend:track_1:network_1:shock_mock_process"
tcs_mock_path="rigs:dhu3s:pi6:backend:track_1:network_1:tcs_mock_process"
keypad_mock_path = "rigs:dhu3s:pi6:backend:track_1:network_1:keypad_mock_process"
connection = PytteConnection("10.151.112.69:6388", "benjamin")
import threading
from gyppe_core import *
def main():
    logon(11111)
    lift(duration=2)
    lower(duration=2)
    lift(repeat=2)
    lower(repeat=2)
    lift(duration=2, repeat=2, interval=2)
    lower(duration=2, repeat=2)
    drive_and_lift(duration=2)
    reverse_and_lift(duration=4)
    drive_and_lower(duration=2)
    reverse_and_lower(duration=2)
    wait(10)
    drive(duration=5, repeat=2)
    logoff(2)


main()
