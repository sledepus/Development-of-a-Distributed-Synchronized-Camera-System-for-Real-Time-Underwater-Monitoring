import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Setting up PWM pin
output_pins = {
    'JETSON_XAVIER': 18,
    'JETSON_NANO': 33,
    'JETSON_NX': 33,
    'CLARA_AGX_XAVIER': 18,
    'JETSON_TX2_NX': 32,
    'JETSON_ORIN': 18,
    'JETSON_ORIN_NX': 33,
    'JETSON_ORIN_NANO': 33
}
output_pin = output_pins.get(GPIO.model, None)
if output_pin is None:
    raise Exception('PWM not supported on this board')

# More accurate sleep
def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()

# Sleep until next whole second
def sleep_until_next_1sec():
    now = datetime.now()
    next_sec = (now + timedelta(seconds=1)).replace(microsecond=0)
    sleep_duration = (next_sec - now).total_seconds()
    sleep(sleep_duration)

# HTTP Server Setup
class StartRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/start':
            print("Received /start command via HTTP. Starting PWM.")
            self.send_response(200)
            self.end_headers()
            self.server.should_start_pwm = True
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server(server):
    print("HTTP server is running. Waiting for /start...")
    server.serve_forever()

def main():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)

    p = GPIO.PWM(output_pin, 60)  # 60 Hz

    # Start HTTP server in a thread
    httpd = HTTPServer(('', 8080), StartRequestHandler)
    httpd.should_start_pwm = False
    threading.Thread(target=run_http_server, args=(httpd,), daemon=True).start()

    # Wait for signal to start
    while not httpd.should_start_pwm:
        time.sleep(0.1)

    sleep_until_next_1sec()
    print("PWM synchronized every minute. Press CTRL+C to exit.")
    try:
        while True:
            sleep_until_next_1sec()
            p.start(10) # 10% duty cycle per Ser/Des datasheet
            print(f"PWM started at {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(60)
            p.stop()
            print(f"PWM stopped at {datetime.now().strftime('%H:%M:%S')}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
