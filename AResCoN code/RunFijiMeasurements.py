import subprocess
import pyautogui
import pyperclip
import time
import psutil
import pygetwindow
import re
from os import listdir


def GetMeasurementsOfRois (**kwargs) :  

    user_system = kwargs.get("winlin")  

    def CodeStorage ():
        """Converts the fiji maro code based on user input and applies a few additional changes. 
          Importantly, detects the name of the last image in the folder so that when macro finishes Fiji shuts down completely"""
        rois_path  = kwargs.get("Rroiresults").replace('\\', '/')                    # paths here will be backslashes for windows but wont work with INSIDE fiji macro in windows unless they become forward
        rois_path  = '"' + rois_path + '/"'                                          # adding quotes to the path to make it string INSIDE the fiji macro. Add a frontslash in the end
        save_path  = kwargs.get("measure_sub_path").replace('\\', '/')               # take the subdirectory path of the measurement that corresponds to a planeN
        save_path  = '"' + save_path + '/"' 
        last_image_name = listdir(kwargs.get("Ffoldpath_img"))[-1]                   # gets the name of the last image inside the folder with the images. If the title of the image running in the macro is the same to this, fiji shuts down

        FijicodeMeasurements = f"""title = getTitle();
run("ROI Manager...");
roiManager("Open", {rois_path} + title + ".zip");
roiManager("Show All");
roiManager("Measure");
saveAs("Results", {save_path} + title + ".csv");
if (title=="{last_image_name}") {{
    while (nImages > 0) {{
    selectImage(nImages);
    close();
                        }}
    run("Quit");                }}
roiManager ("Reset");
run("Fresh Start");"""
        return FijicodeMeasurements

    def RunFiji (code_fiji):
            fiji_path = kwargs.get("Ffiji_path")                                       # paths here will be backslashes for windows
            images_folder_path = kwargs.get("Ffoldpath_img").replace('/', '\\')        # paths here will be frontslashes for windows and must change to backslashes to fit for fiji batch-process-macro input for windows

            print('printing below')
            print(f"{fiji_path} {images_folder_path}")    

            while is_fiji_running("imageJ-win64.exe") == True :                       # as long as previous iteration fiji is open, wait till it closes. 
                time.sleep(3)  


            if user_system == 'Windows' :
                print('system is windows')
                print(f'images folder is {images_folder_path}')
                subprocess.Popen([fiji_path])
                time.sleep(8)
                EnsureFijisActive()
                time.sleep(2)
                EnsureFijisActive()                                                   # sometimes doesnt work if only tried once
                time.sleep(2)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                pyautogui.write("Macro... ")
                time.sleep(1.5)
                pyautogui.press('enter')                                             # Simulates pressing the "Escape" key
                time.sleep(2)

                for tabpresses in range (1):
                    pyautogui.press('tab')
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'a', interval=0.2)
                time.sleep(1)
                pyperclip.copy("")  # Clear clipboard
                time.sleep(0.1)
                pyperclip.copy(f'{images_folder_path}')
                time.sleep(0.6)
                #time.sleep(1)
                pyautogui.hotkey('ctrl', 'v', interval=0.2)
                time.sleep(1)
                for delpresses in range (6):
                    pyautogui.press('tab')
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'a', interval=0.2)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(1)
                pyperclip.copy("")  # Clear clipboard
                time.sleep(0.3)
                pyperclip.copy(code_fiji)
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'v', interval=0.2)
                pyautogui.hotkey('ctrl', 'tab')
                time.sleep(1)
                for tabpresses in range (3):
                    pyautogui.press('tab')
                time.sleep(1)
                pyautogui.press('space')
                time.sleep(1)



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

 
    macro_fiji = CodeStorage()
    RunFiji(macro_fiji)             

    
if __name__ == "__main__" : 
    GetMeasurementsOfRois()

    
    





