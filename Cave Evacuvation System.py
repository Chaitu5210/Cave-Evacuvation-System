import time
import smtplib
from grove.grove_led import GroveLed
from grove.grove_button import GroveButton
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from grove.grove_rotary_angle import GroveRotaryAngle
from grove.grove_buzzer import GroveBuzzer
from grove.grove_rgb_lcd import GroveRgbLcd
from grove.grove_sound_sensor import GroveSoundSensor
from grove.grove_temperature_humidity_sensor import GroveTemperatureHumiditySensor
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from grove.grove_air_quality import GroveAirQuality
from grove.grove_relay import GroveRelay  # Import the Grove Relay module

# Initialize sensors and actuators
red_led = GroveLed(5)
blue_led = GroveLed(6)
green_led = GroveLed(7)
button = GroveButton(8)
ultrasonic = GroveUltrasonicRanger(3)
rotary = GroveRotaryAngle(0)
buzzer = GroveBuzzer(4)
lcd = GroveRgbLcd(0x04, 2, 3)
sound_sensor = GroveSoundSensor(1)
temp_humidity_sensor = GroveTemperatureHumiditySensor(2)
light_sensor = GroveLightSensor(0)
air_quality_sensor = GroveAirQuality(1)
automatic_light_relay = GroveRelay(2)  # Relay for automatic lighting

# Define constants
TEMPERATURE_THRESHOLD = 30
SOUND_THRESHOLD = 80
DISTANCE_THRESHOLD = 30
AIR_QUALITY_THRESHOLD = 200

# Email configuration (replace with your own details)
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_password"
RECIPIENT_EMAIL = "recipient@example.com"

# Define emergency kits location
EMERGENCY_KITS_LOCATION = "Near Exit B"

def display_message(message, color=(255, 255, 255)):
    lcd.set_text_n_color(message, *color)

def log_event(event):
    with open("event_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event}\n")

def send_email(subject, message):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, f"Subject: {subject}\n\n{message}")

def main():
    try:
        lcd.set_text("Coal Mine Evacuation System")
        time.sleep(2)
        lcd.set_text("Press the button to start")
        
        # Wait for button press to activate
        while not button.is_pressed():
            pass
        lcd.set_text("System Activated")
        
        while True:
            # Read sensor data
            temperature, humidity = temp_humidity_sensor.read()
            light_intensity = light_sensor.read()
            sound_level = sound_sensor.read()
            distance = ultrasonic.get_distance()
            rotation_angle = rotary.angle()
            air_quality = air_quality_sensor.read()
            
            # Display sensor data on the LCD
            lcd_text = f"Temp: {temperature:.2f}C  Humidity: {humidity:.2f}%\n"
            lcd_text += f"Light: {light_intensity}  Sound: {sound_level}\n"
            lcd_text += f"Distance: {distance}cm  Angle: {rotation_angle}°\n"
            lcd_text += f"Air Quality: {air_quality}\n"
            lcd_text += f"Emergency Kits: {EMERGENCY_KITS_LOCATION}\n"  # Display emergency kits location
            
            # Control automatic lighting based on ambient light intensity
            if light_intensity < 100:  # Adjust threshold as needed
                automatic_light_relay.on()
                lcd_text += "Automatic Lighting: ON\n"
            else:
                automatic_light_relay.off()
                lcd_text += "Automatic Lighting: OFF\n"
            
            display_message(lcd_text, (0, 128, 0))  # Display in green
            
            # Check for emergency conditions and activate indicators
            emergency_triggered = False
            
            if (
                temperature > TEMPERATURE_THRESHOLD or
                sound_level > SOUND_THRESHOLD or
                distance < DISTANCE_THRESHOLD or
                air_quality > AIR_QUALITY_THRESHOLD
            ):
                red_led.on()
                blue_led.off()
                green_led.off()
                buzzer.on()
                lcd.set_text("Emergency! Evacuate!")
                emergency_triggered = True
                log_event("Emergency Triggered")
                send_email("Coal Mine Emergency", "An emergency has been triggered in the coal mine.")
            else:
                red_led.off()
                blue_led.off()
                green_led.on()
                buzzer.off()
            
            # Display specific emergency messages
            if emergency_triggered:
                if temperature > TEMPERATURE_THRESHOLD:
                    lcd.set_text("High Temperature Detected")
                elif sound_level > SOUND_THRESHOLD:
                    lcd.set_text("Loud Noise Detected")
                elif distance < DISTANCE_THRESHOLD:
                    lcd.set_text("Obstacle Detected")
                elif air_quality > AIR_QUALITY_THRESHOLD:
                    lcd.set_text("Low Air Quality")
            
            # Wait before next iteration
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Cleanup and exit gracefully
        lcd.set_text("System Stopped")
        red_led.off()
        blue_led.off()
        green_led.off()
        buzzer.off()
        automatic_light_relay.off()  # Turn off the automatic lighting relay
        lcd.set_rgb(0, 0, 0)  # Turn off LCD backlight

if __name__ == "__main__":
    main()
