#!/usr/bin/env python3
import time, math, threading
from smbus2 import SMBus, i2c_msg
from flask import Flask, jsonify
from flask_cors import CORS

# Flask setup
server = Flask(__name__)
CORS(server)

@server.route("/sensor_values")
def get_sensor_values():
    with sensor_lock:
        return jsonify(sensor_data)

# Sensor dictionary for publishing
sensor_data = {
    "temperature": 0.0,
    "humidity":    0.0,     
    "x_accel":     0.0,
    "y_accel":     0.0,
    "z_accel":     0.0,
    "roll":        0.0,
    "pitch":       0.0,
}
sensor_lock = threading.Lock()

# I2C addresses
I2C_BUS          = 7
SHTC3_ADDR = 0x70
IMU_ADDR         = 0x53 

# ADXL345 registers
IMU_POWERCTL_REG   = 0x2D
IMU_DATAFORMAT_REG = 0x31

# SHTC3 commands
SHTC3_SLEEP   = (0xB0, 0x98)
SHTC3_WAKEUP  = (0x35, 0x17)
SHTC3_MEASURE = (0x78, 0x66)  

# Function for sending commands to IMU
def send_to_imu(bus, reg, value):
    try:
        bus.write_byte_data(IMU_ADDR, reg, value)
    except OSError as e:
        print("IMU write failed:", e)

# Function for reading from IMU
def read_from_imu(bus):
    try:
        buf = bus.read_i2c_block_data(IMU_ADDR, 0x32, 6)
        x, y, z = (int.from_bytes(buf[i:i+2], "little", signed=True) for i in (0, 2, 4))
        g_scale = 0.0078          # g/LSB for ±4 g
        return True, (x * g_scale, y * g_scale, z * g_scale)
    except OSError as e:
        print("IMU read failed:", e)
        return False, (0.0, 0.0, 0.0)
# Calculation orientation based on acceleration values
def calculate_orientation(x, y, z):
    try:
        roll  = math.degrees(math.atan2(y, z))
        pitch = math.degrees(math.atan2(-x, math.hypot(y, z)))
        return roll, pitch
    except ZeroDivisionError:
        return 0.0, 0.0
# Function for setting SHTC3 into measure mode and then reading values
def read_shtc3(bus):
    try:
        bus.write_byte_data(SHTC3_ADDR, *SHTC3_WAKEUP)
        time.sleep(0.001)

        bus.write_byte_data(SHTC3_ADDR, *SHTC3_MEASURE)
        time.sleep(0.020)

        read = i2c_msg.read(SHTC3_ADDR, 6)
        bus.i2c_rdwr(read)
        t_msb, t_lsb, _, h_msb, h_lsb, _ = read

        raw_t = (t_msb << 8) | t_lsb
        raw_h = (h_msb << 8) | h_lsb

        temperature = -45 + 175 * (raw_t / 65536.0)
        humidity    =      100 * (raw_h / 65536.0)

        bus.write_byte_data(SHTC3_ADDR, *SHTC3_SLEEP)

        return True, temperature, humidity
    except OSError as e:
        print("SHTC3 read failed:", e)
        return False, 0.0, 0.0

# Updating sensor value dictionary 
def publish(temp, hum, x, y, z, roll, pitch):
    with sensor_lock:
        sensor_data.update(
            temperature=temp,
            humidity=hum,          
            x_accel=x,
            y_accel=y,
            z_accel=z,
            roll=roll,
            pitch=pitch,
        )


def main():
    with SMBus(I2C_BUS) as bus:
        send_to_imu(bus, IMU_DATAFORMAT_REG, 0x01)   # +-4 g
        send_to_imu(bus, IMU_POWERCTL_REG,   0x08)   # measure mode

        while True:
            ok_t, temperature, humidity = read_shtc3(bus)
            ok_i, (x, y, z)             = read_from_imu(bus)

            if ok_t:
                print(f"T: {temperature:5.2f} °C  RH: {humidity:5.1f} %")
            if ok_i:
                roll, pitch = calculate_orientation(x, y, z)
                print(f"Accel g  X:{x:+.3f} Y:{y:+.3f} Z:{z:+.3f}  "
                      f"Roll:{roll:+.1f}° Pitch:{pitch:+.1f}°")

            publish(temperature, humidity, x, y, z, roll, pitch)
            time.sleep(1)

# Starting HTTP server for publishing sensor values
if __name__ == "__main__":
    threading.Thread(
        target=lambda: server.run(host="0.0.0.0", port=8080,
                                  debug=False, use_reloader=False),
        daemon=True
    ).start()

    main()
