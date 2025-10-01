from java.awt import Robot, event
from java.lang import Thread


def press_enter():
    r = Robot()
    Thread.sleep(500)  # wait 0.5 s for dialog to appear
    r.keyPress(event.KeyEvent.VK_ENTER)
    r.keyRelease(event.KeyEvent.VK_ENTER)

from threading import Thread as PyThread
t = PyThread(target=press_enter)
t.start()