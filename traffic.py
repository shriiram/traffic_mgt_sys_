import RPi.GPIO as GPIO
import time
from collections import deque

# GPIO Mode
GPIO.setmode(GPIO.BCM)

# Traffic light and PIR sensor pins
lanes = {
    "A": {"green": 16, "yellow": 20, "red": 21, "pir": 5},
    "B": {"green": 6, "yellow": 13, "red": 19, "pir": 12},
    "C": {"green": 26, "yellow": 22, "red": 27, "pir": 17},
    "D": {"green": 23, "yellow": 24, "red": 25, "pir": 18}
}

# Initialize GPIO pins
for lane, pins in lanes.items():
    GPIO.setup(pins["green"], GPIO.OUT)
    GPIO.setup(pins["yellow"], GPIO.OUT)
    GPIO.setup(pins["red"], GPIO.OUT)
    GPIO.setup(pins["pir"], GPIO.IN)

# Helper functions to control lights
def turn_light(lane, color):
    """Turn a specific color light on for a lane and others off."""
    for c in ["green", "yellow", "red"]:
        GPIO.output(lanes[lane][c], GPIO.HIGH if c == color else GPIO.LOW)
    print(f"Lane {lane} traffic light: {color.upper()}")

def all_red():
    """Set all traffic lights to red."""
    for lane in lanes.keys():
        turn_light(lane, "red")
    print("All traffic lights set to RED")

# Traffic management logic
def traffic_management():
    motion_queue = deque() # Priority queue for lanes with motion
    last_motion_time = time.time()
    round_robin_lanes = deque(lanes.keys()) # Round-robin sequence
    round_robin_index = 0
    round_robin_delay = 10 # Seconds per light in round-robin mode
    motion_check_interval = 1 # Interval to check PIR sensors
    active_lane = None # Currently active lane
    interrupt_round_robin = False # Flag to break round-robin on motion detection

    print("Starting traffic management system...")
    all_red() # Initial state

    try:
        while True:
            # Check motion for all lanes
            for lane in lanes.keys():
                if GPIO.input(lanes[lane]["pir"]):
                    print(f"Motion detected at Lane {lane}")
                    if lane not in motion_queue:
                        motion_queue.append(lane)
                    last_motion_time = time.time()
                    interrupt_round_robin = True # Trigger round-robin interrupt

            # Determine lane to activate
            if interrupt_round_robin and active_lane in round_robin_lanes:
                # Finish the current round-robin lane before breaking
                print(f"Finishing round-robin for Lane {active_lane} before switching")
                interrupt_round_robin = False # Reset interrupt after the current cycle
            elif motion_queue:
                # Process motion-detected lane
                active_lane = motion_queue.popleft()
                print(f"Processing Lane {active_lane} from motion queue")
            elif time.time() - last_motion_time > round_robin_delay:
                # Fall back to round-robin if no motion
                active_lane = round_robin_lanes[round_robin_index]
                round_robin_index = (round_robin_index + 1) % len(round_robin_lanes)
                print(f"Switching to round-robin: Lane {active_lane}")

            # Activate the selected lane's traffic light
            if active_lane:
                turn_light(active_lane, "green")
                time.sleep(5) # Keep green light ON for 5 seconds
                turn_light(active_lane, "yellow")
                time.sleep(2) # Yellow light ON for 2 seconds
                turn_light(active_lane, "red")

            # Small delay for PIR motion check
            time.sleep(motion_check_interval)

    except KeyboardInterrupt:
        print("Stopping traffic management system...")
        GPIO.cleanup()

# Run the traffic management system
traffic_management()