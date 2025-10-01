import subprocess
import pyautogui
import pyperclip
import time
import psutil
import pygetwindow
import re
from os import listdir


def TransformLabels (**kwargs) :  

    user_system = kwargs.get("winlin")  

    def CodeStorage ():
        """Converts the fiji maro code based on user input and applies a few additional changes. 
          Importantly, detects the name of the last image in the folder so that when macro finishes Fiji shuts down completely"""
        planeN_with_masked_tif = kwargs.get("planeN_masks").replace('\\', '/')     # path to labels planeN subdirectory
        planeN_with_masked_tif  = '"' + planeN_with_masked_tif + '/"' 
        save_path = kwargs.get("savepath").replace('\\', '/')                      # path to RoisFromLabels planeN subdirectory
        save_path  = '"' + save_path + '/"'
        last_mask_name = listdir(kwargs.get("planeN_masks"))[-1]                   # gets the name of the last image inside the folder with the images. If the title of the image running in the macro is the same to this, fiji shuts down

        FijicodeMeasurements = f"""title = getTitle();
run("Label Map to ROIs", "connectivity=C4 vertex_location=Corners name_pattern=001_%03d");
roiManager("Show All");
roiManager("Save", {save_path} + title + ".zip");
if (title=="{last_mask_name}")
    run("Quit");
roiManager ("Reset");
run("Fresh Start");"""
        return FijicodeMeasurements

    def RunFiji (code_fiji):
            fiji_path = kwargs.get("fiji_path")                                       # paths here will be backslashes for windows
            images_folder_path = kwargs.get("planeN_masks").replace('/', '\\')        # paths here will be frontslashes for windows and must change to backslashes to fit for fiji batch-process-macro input for windows

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
    TransformLabels()

    
    





