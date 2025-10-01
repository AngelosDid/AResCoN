# Save as: AutoEnter.py
from java.awt import Robot, event
from java.lang import Thread
from java.lang import Runnable
from ij import WindowManager
import time

class EnterPresser(Runnable):
    def run(self):
        # Wait for the dialog to appear
        Thread.sleep(8000)
        
        # Get the active window (should be the error dialog)
        active_window = WindowManager.getActiveWindow()
        if active_window is not None:
            # Bring the window to front to ensure it has focus
            active_window.toFront()
            
            # Create robot and press Enter
            r = Robot()
            r.keyPress(event.KeyEvent.VK_ENTER)
            r.keyRelease(event.KeyEvent.VK_ENTER)
            
            # Print to log for debugging
            print("Auto-pressed Enter to dismiss dialog: " + active_window.getTitle())
        else:
            print("No active window found to dismiss")

# Create and start the thread
presser = EnterPresser()
thread = Thread(presser)