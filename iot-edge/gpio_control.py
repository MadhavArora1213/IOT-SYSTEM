import logging

class GPIOControl:
    def __init__(self):
        # Simulation: Green LED on PIN 18, Red LED on PIN 23
        self.green_led = 18
        self.red_led = 23
        logging.info("GPIO Initialized (Simulated)")

    def access_granted(self):
        """Simulate green LED for success"""
        print("💡 [LED] GREEN ON (Access Granted)")
        # In real Pi: GPIO.output(self.green_led, True)

    def access_denied(self):
        """Simulate red LED for failure"""
        print("💡 [LED] RED ON (Access Denied)")
        # In real Pi: GPIO.output(self.red_led, True)

    def reset(self):
        """Turn off all LEDs"""
        print("💡 [LED] ALL OFF")
