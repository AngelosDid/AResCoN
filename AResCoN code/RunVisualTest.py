import subprocess
import pyautogui
import pyperclip
import time
import psutil
import pygetwindow
import re
from os.path import basename


def VisualizeReducedRois (**kwargs) :  

    user_system = kwargs.get("winlin")  

    def CodeStorage ():
        """Converts the fiji maro code based on user input and applies a few additional changes"""
        rois_path  = kwargs.get("roipath").replace('\\', '/')                    # paths here will be backslashes for windows but wont work with INSIDE fiji macro in windows unless they become forward
        rois_path  = '"' + rois_path +'"'                                        # adding quotes to the path to make it string INSIDE the fiji macro. Add a frontslash in the end
        image_path = kwargs.get("impath").replace('\\', '/')                     # gets the name of the image. 
        image_path = '"' + image_path +'"'
        image_name = basename(image_path)
        reduceprcn = kwargs.get("prcntg")
        final_prc  = (100 - reduceprcn) /100                                     # If the user has selected 20%, this will be a final 80% of the initial. Which is 0.8 out of 1
        
        # The macro code below was found in https://forum.image.sc/t/imagej-how-to-shrink-roi-by-percentage/99357/14
        Fijicode = f"""open({image_path});
selectImage("{image_name});
open({rois_path});
roiManager("Open", {rois_path});
for(i=0; i<RoiManager.size; i++) {{
close("Mask");
roiManager("Select", i);
run("Create Mask");
run("Create Selection");
originalArea = getValue("Area");
while(getValue("Area") > ({final_prc} * originalArea) ) {{
run("Erode");
run("Create Selection");
roiManager("Update");                                              }}
print(i, RoiManager.getName(i), originalArea, getValue("Area"));
                                  }}
close("Mask");
roiManager("Show All");
showMessage("Your rois have been reduced to {final_prc} of their original size. Dont forget to close imagej before you continue with AResCoN");"""
        return Fijicode

    def RunFiji (code_FIJI):
        fiji_path = kwargs.get("FFiji_path")                                       # paths here will be backslashes for windows
        while is_fiji_running("imageJ-win64.exe") == True :                        # as long as previous iteration fiji is open, wait till it closes. 
            time.sleep(3)  

        if user_system == 'Windows' :
            subprocess.Popen([fiji_path])
            time.sleep(8)
            EnsureFijisActive()
            time.sleep(2)
            pyautogui.hotkey('ctrl', 'l') 
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'l') 
            time.sleep(0.2)
            pyautogui.write("new macro")
            time.sleep(1.5)
            pyautogui.press('enter')                                             # Simulates pressing the "Escape" key
            time.sleep(2)

            pyperclip.copy("")  # Clear clipboard
            time.sleep(0.1)
            pyperclip.copy(code_FIJI)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v', interval=0.2)
            pyautogui.press('f5')
                
    def is_fiji_running(process_name):
        """Checks whether fiji is still runinng
           Input process_name : str corresponding to the name of the fiji process we test
           Output : True or False, depending on whether fiji is open or not, respectively"""
        
        for proc in psutil.process_iter(attrs=['name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    print('still runing')
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False
    
    def EnsureFijisActive ():
        """Searches if for fiji in the open windows and makes it the active window so that pyautogui can work on top of it"""
        find_fiji_pattern   = re.compile (r'fiji', re.IGNORECASE)
        find_imagej_pattern = re.compile (r'imagej', re.IGNORECASE) 
        for window in pygetwindow.getAllWindows():
            if (find_fiji_pattern.search(window.title) != None) or (find_imagej_pattern.search(window.title) != None)  :
                for activate_attempt in range(50):
                    try: 
                        window.activate()
                        time.sleep(0.2)
                    except : 
                        # pygetwindow is sometimes problematic and cannot activate the window. Workaround is to minimize it, maximize and then restore to normal size
                        window.minimize()
                        window.maximize()
                        window.restore()

                    if window.isActive:
                        return

    macro_FIJI = CodeStorage()
    RunFiji(macro_FIJI)             

if __name__ == "__main__" : 
    VisualizeReducedRois()

    
    





