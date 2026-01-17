## Mercury Robotics — Operator (gamepad) control

This repository contains a small operator script used for hands-on control of Mercury Robotics hardware using a game controller (Xbox, Nintendo Pro Controller, DualSense, etc.). The main operator program is `operator.py`.

### What it does
- Reads a connected game controller using `pygame`.
- Uses a mapping table to translate physical buttons/axes into logical inputs (e.g., left stick -> forward/strafe, right stick -> rotation).
- Converts joystick inputs into four mecanum wheel outputs via `calculateMecanumWheel`.
- Converts the wheel floats into bytes and—optionally—sends 4 bytes over a TCP socket to a robot server (default port 9999). The send order is (rb, rf, lb, lf).
- Provides a `MotorControlWatcher` hook that observers can use to monitor motor value changes.

Supported controller mappings are defined in `operator.py` (examples: "Pro Controller", "Xbox One S Controller", "Xbox 360 Controller", "DualSense Wireless Controller"). If your controller name isn't listed you may need to add or adapt a mapping.

### Configuration notes
- Toggle network sending by setting `connect = True` or `connect = False` in `operator.py`.
- The script defaults to connecting to `127.0.0.1:9999`. You can change the `ip_address` in `operator.py` or use the `get_ip_from_mac(mac_address)` helper to look up an IP from the ARP table.
- If connection fails the script will attempt to reconnect in a loop.

### Quick start (zsh)
1. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the required package(s):

```bash
pip install pygame
# If you have a requirements.txt later, you can use:
# pip install -r requirements.txt
```

3. Run the operator script:

```bash
python operator.py
```

Notes:
- To quit the script, close the pygame window or use Ctrl+C in the terminal.
- For headless testing (no robot server), set `connect = False` to disable network sending while you test input/visualizer output.

### Troubleshooting
- If your controller isn't recognized, run a small Python snippet to print `pygame.joystick.Joystick(i).get_name()` for each attached device and compare names to the mapping keys in `operator.py`.
- If `pygame` fails to initialize the joystick subsystem, ensure you have SDL dependencies installed for your platform and that joystick support is available.

If you'd like, I can also add a minimal `requirements.txt`, an example config, or a short test harness to validate joystick mapping on startup.

---------------------------------------------------------

### About `testcontrol.py`

`testcontrol.py` is a small test server meant to validate the operator script's networking and data flow. It:

- Listens for a TCP connection on port 9999 (binds to all interfaces by default).
- Accepts one client (the `operator.py` script) and repeatedly receives 4-byte frames.
- Each received frame is intended to represent four unsigned bytes: rb, rf, lb, lf (the same order `operator.py` sends).
- The file contains commented-out example code showing how those bytes might be forwarded to serial motor controllers (Roboclaw) — useful if you want to connect the test harness to actual motor hardware.

How to use it for local testing:

1. Start the test server in one terminal (it will block waiting for a connection):

```bash
source venv/bin/activate
python testcontrol.py
```

2. In another terminal start the operator client (it will connect to `127.0.0.1:9999` by default):

```bash
source venv/bin/activate
python operator.py
```

Notes and troubleshooting:
- If `operator.py` cannot connect, ensure `testcontrol.py` is running and that the `ip_address` in `operator.py` points to the machine running the server (use `127.0.0.1` for the same machine).
- `testcontrol.py` currently times out if no data arrives within ~1 second while reading a 4-byte frame; on timeout it will return and the top-level loop will restart the accept cycle.
- The serial/robot-control calls are commented out; uncomment and adapt them if you want the server to forward received bytes to hardware.

Run these steps to test locally: start `testcontrol.py` first, then `operator.py`. I can also add a small logger to `testcontrol.py` to print the unpacked byte values as they arrive if you'd like to see live values.
