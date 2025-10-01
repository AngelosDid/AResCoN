#from java.awt import Robot, event
#from javax.swing import JOptionPane
#import time
#
## Display a dialog box
#JOptionPane.showMessageDialog(None, "Click OK to continue")
#print("User clicked OK, continuing execution...")
#
#time.sleep(2)
#r = Robot()
#r.keyPress(event.KeyEvent.VK_ENTER)
#r.keyRelease(event.KeyEvent.VK_ENTER)



from javax.swing import JOptionPane, JDialog
from java.awt import Robot, event
from java.lang import Thread

# Create a non-modal dialog
dialog = JOptionPane("Click OK to continue").createDialog(None, "Message")
dialog.setModal(False)  # make it non-blocking
dialog.setVisible(True)

# Wait a bit, then press Enter automatically
Thread.sleep(2000)  # 2 seconds delay
r = Robot()
r.keyPress(event.KeyEvent.VK_ENTER)
r.keyRelease(event.KeyEvent.VK_ENTER)