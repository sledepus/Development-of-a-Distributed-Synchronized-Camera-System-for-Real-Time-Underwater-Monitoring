# Overview of dependencies needed
## Sensors:
smbus2 (Python package to interface with I2C via Python)
flask (Python package to run a lightweight HTTP server)
flask_cors (Extension package to flask)

Line 5 in start_monitoring.sh needs to point to correct Python virtual environment

## Sync:
### On Nvidia Jetson:
Jetson.GPIO (Python package to interface with GPIO on Jetson via Python)
Chrony (Lightweight NTP client / server)

Line 5 in start_sync.sh needs to point to correct Python virtual environment

### On Host PC:
aiohttp (Asynchronus HTTP client / server for Python)
Chrony (Lightweight NTP client / server)



