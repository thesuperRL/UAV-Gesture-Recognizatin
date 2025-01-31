import asyncio
from pynput import keyboard
from mavsdk import System

velocity = None

roll = ""
pitch = ""
throttle = ""
yaw = ""

def on_press(key):
    global roll, pitch, throttle, yaw
    try:
        if key.char == 'w':
            print("w press")
            roll = 0.0
            pitch = 0.5
            throttle = 0.5
            yaw = 0.0
        elif key.char == 'a':
            print("a press")
            roll = -0.5
            pitch = 0.0
            throttle = 0.5
            yaw = 0.0
        elif key.char == 's':
            print("s press")
            roll = 0.0
            pitch = -0.5
            throttle = 0.5
            yaw = 0.0
        elif key.char == 'd':
            print("d press")
            roll = 0.5
            pitch = 0.0
            throttle = 0.5
            yaw = 0.0
        elif key.char == 'q':
            print("q press")
            roll = 0.0
            pitch = 0.0
            throttle = 0.7
            yaw = 0.0
        elif key.char == 'e':
            print("e press")
            roll = 0.0
            pitch = 0.0
            throttle = 0.2
            yaw = 0.0
        else:
            print(str(key) + " pressed, reset speed")
            roll = 0.0
            pitch = 0.0
            throttle = 0.5
            yaw = 0.0
    except:
        print("failed to rec")
        print(key)


async def main():
    """Main function to connect to the drone and input manual controls"""
    global roll, pitch, yaw, throttle
    # Connect to the Simulation
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    # Checking if Global Position Estimate is ok
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position state is good enough for flying.")
            break

    # Arming the drone
    print("-- Arming")
    await drone.action.arm()

    # Take off
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(10)

    print("-- Set manual control")
    roll = 0.0
    pitch = 0.0
    throttle = 0.5
    yaw = 0.0
    # set the manual control input after arming
    manual = asyncio.create_task(manual_controls(drone))
    print("-- wait")
    await asyncio.sleep(1)

    # start manual control
    print("-- Starting manual control")
    await drone.manual_control.start_position_control()
    print("-- wait")
    await asyncio.sleep(1)
    print("-- Activating manual control")

    listener = keyboard.Listener(
        on_press=on_press)
    listener.start()

    await asyncio.sleep(30)

    await drone.action.land()
    print("-- end")

async def manual_controls(drone):
    global roll, pitch, yaw, throttle
    while True:
        await drone.manual_control.set_manual_control_input(pitch, roll, throttle, yaw)


asyncio.run(main())
