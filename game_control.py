import cv2
from pynput.keyboard import Controller, Key  # Importing necessary keys
from pynput.mouse import Controller as MouseController, Button  # Mouse controller
import handtracking as htm  # Your hand tracking module
import time

##############################################

cap = cv2.VideoCapture(0)  # Open webcam
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

#############################################

detector = htm.handDetector(maxHands=1, detectionCon=0.75, trackCon=0.75)  # Hand detection with better confidence

keyboard = Controller()  # Keyboard controller to send keypresses
mouse = MouseController()  # Mouse controller to handle mouse events

# Control states
control_mode = "keyboard"  # Start with keyboard mode by default
switch_time = time.time()  # Timer to debounce switching between modes
switch_delay = 5.0  # Delay of 1 second to prevent accidental switching

mouse_pressed = False  # To track mouse clicks

def debounce_switch():
    """Returns True if the time delay for switching is satisfied."""
    global switch_time
    current_time = time.time()
    if current_time - switch_time > switch_delay:
        switch_time = current_time
        return True
    return False

while True:
    success, img = cap.read()  # Read frame from camera
    img = detector.findHands(img)  # Detect hands in the frame
    lmList, bbox = detector.findPosition(img)  # Get landmark positions of the hand

    if len(lmList) != 0:  # If a hand is detected
        fingers = detector.fingersUp()  # Get which fingers are up

        # Gesture to switch to mouse mode (Thumb and Pinky up)
        if fingers[0] == 1 and fingers[4] == 1 and all(f == 0 for f in fingers[1:4]) and control_mode != "mouse":
            if debounce_switch():  # Prevent accidental switching
                control_mode = "mouse"
                print("Switched to Mouse Mode")

        # Gesture to switch to keyboard mode (Index and Middle finger up)
        elif fingers[0] == 1 and fingers[4] == 1 and all(f == 0 for f in fingers[1:4]) and control_mode != "keyboard":
            if debounce_switch():
                control_mode = "keyboard"
                print("Switched to Keyboard Mode")

        if control_mode == "keyboard":
            # Keyboard controls
            if all(fingers):  # Jump (Space)
                keyboard.press(Key.space)
            else:
                keyboard.release(Key.space)

            # Esc gesture: Thumb and Ring finger up
            if fingers[0] == 1 and fingers[3] == 1 and all(f == 0 for f in [1, 2, 4]):
                keyboard.press(Key.esc)
            else:
                keyboard.release(Key.esc)

            # Move Forward (W): Index finger up
            if fingers[1] == 1 and all(f == 0 for f in fingers[:1] + fingers[2:]):  # Only index finger up
                keyboard.press("w")
                keyboard.release("s")
            else:
                keyboard.release("w")

            # Turn Left (A): Thumb up
            if fingers[0] == 1 and all(f == 0 for f in fingers[1:]):  # Only thumb up
                keyboard.press("a")
            else:
                keyboard.release("a")

            # Turn Right (D): Middle finger up
            if fingers[2] == 1 and all(f == 0 for f in fingers[:2] + fingers[3:]):  # Only middle finger up
                keyboard.press("d")
            else:
                keyboard.release("d")

            # Brake/Reverse (S): Index finger down
            if fingers[1] == 0:
                keyboard.press("s")
            else:
                keyboard.release("s")

            # Honk (H): Thumb and Pinky up
            if fingers[0] == 1 and fingers[4] == 1:
                keyboard.press("h")
            else:
                keyboard.release("h")

        elif control_mode == "mouse":
            # Mouse controls
            if fingers[0] == 1 and fingers[1] == 0:  # Pinch gesture: Thumb up, index down
                if not mouse_pressed:
                    mouse.click(Button.left, 1)  # Perform a left-click
                    mouse_pressed = True
            else:
                mouse_pressed = False  # Release mouse click state

            # Scroll gesture: All fingers up
            if all(fingers):
                mouse.scroll(0, 1)  # Scroll up

            # Fist gesture: Scroll down
            if fingers == [0, 0, 0, 0, 0]:
                mouse.scroll(0, -1)  # Scroll down

            # Index finger up to move the mouse pointer
            if fingers[1] == 1 and all(f == 0 for f in fingers[:1] + fingers[2:]):  # Only index finger up
                x, y = lmList[8][1:3]  # Get position of index finger tip
                screen_x, screen_y = mouse.position  # Current mouse position
                mouse.move(x - screen_x, y - screen_y)  # Move the mouse pointer accordingly

    cv2.imshow("image", img)  # Display camera feed
    cv2.waitKey(1)  # Wait for 1 ms to process next frame