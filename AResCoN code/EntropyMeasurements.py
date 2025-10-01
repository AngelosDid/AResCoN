import subprocess
import pyautogui
import pyperclip
import time
import psutil
import pygetwindow
import re
import os
from os import listdir



def GetShannonEntropy (**kwargs) :  

    user_system = kwargs.get("winlin")  

    def CodeStorage ():
        """Converts the fiji maro code based on user input and applies a few additional changes. 
           Importantly, detects the name of the last image in the folder so that when macro finishes Fiji shuts down completely"""
        rois_path  = kwargs.get("Rroiresults").replace('\\', '/')                    # paths here will be backslashes for windows but wont work with INSIDE fiji macro in windows unless they become forward
        rois_path  = '"' + rois_path + '/"'                                          # adding quotes to the path to make it string INSIDE the fiji macro. Add a frontslash in the end
        entropy_sub_path  = kwargs.get("subdir_metric_path").replace('\\', '/')      # takes the subdirectory path of a particular planeN from EntropyResults
        entropy_sub_path  = '"' + entropy_sub_path + '/"' 
        print(f' Entropy path is {entropy_sub_path}')
        last_image_name = listdir(kwargs.get("Ffoldpath_img"))[-1]                   # gets the name of the last image inside the folder with the images. If the title of the image running in the macro is the same to this, fiji shuts down
        bits = kwargs.get("bdepth")                                                  # gets the bitdepth


# code with comments can be found inside the entropy_macro.ijm. 
# mind that the makeDirectory commands have changed on purpose.
# channel_index is removed, since channels and planes are by separated by the user
# Importantly, a last command for image_name is inserted so that fiji closes
# after a subdirectory has been processed.
        
        if bits == '16bit':
            FijicodeEntropy = f"""setBatchMode("false");
    roiManager("reset");
    title = getTitle();
    File.makeDirectory({entropy_sub_path} + title + "/");
    channel_dir_path = {entropy_sub_path} + title + "/";
    selectWindow(title);
    roiManager("Open", {rois_path} + title + ".zip");
    n_of_ROIs = roiManager("count");
    RoiManager.useNamesAsLabels("true");
    roiManager("Show All with labels");
    for (roindex = 0; roindex < n_of_ROIs; roindex++) {{
        roiManager("Select", roindex);
        roiname = getInfo("roi.name");
        index_of_dot_in_file_extension = lastIndexOf(title, ".");
        title_without_file_extension = substring(title, 0, index_of_dot_in_file_extension);
        histo_name_before_rename = "Histogram of " + title_without_file_extension;
        histogram_title = "Histogram of " + roiname;
        binCount = 256;        // Number of bins (e.g., 512, 1024)
        selectWindow(title);
        run("Histogram", "bins=256 use pixel value range");
        while (!isOpen(histo_name_before_rename)) {{
    	wait(10);  
	                                               }}
	    rename(histogram_title);
	    while (!isOpen(histogram_title)) {{
    	wait(10);
	                                      }}
	    selectImage(histogram_title);
	    while (getTitle() != histogram_title) {{
    	wait(10);  
	                                           }}
	    Table.showHistogramTable;
	    wait(50);
        total_counts = 0;
        countarray = newArray();
        binarray = newArray();
        for (c = 0; c < binCount; c++) {{
            current_count = parseInt(Table.get("count", c));
            total_counts += current_count;
            countarray[c] = current_count;
            binarray[c] = parseInt(Table.get("bin start", c));
                                        }}
        probarray = newArray();
            entropy = 0;
        for (i = 0; i < binCount; i++) {{
            bin_prob = countarray[i] / total_counts;
            probarray[i] = bin_prob;
            if (bin_prob > 0) {{
                    entropy -= bin_prob * log(bin_prob) / log(2); 
                               }}  
                                        }}
        for (i = 0; i < binCount; i++) {{
            setResult("StartingBin", i , binarray[i]);
            setResult("Count", i, countarray[i]);
            setResult("Probability", i, probarray[i]);
                                        }}
        setResult("ShannonEntropy", 0, entropy);
        selectWindow("Results");
        saveAs("Results", channel_dir_path + roiname + ".csv");
        selectWindow("Results");
        run("Close");
        selectWindow(histogram_title);
        // Wait until the selected window is really active
	    while (getTitle() != histogram_title) {{
   	    wait(10);
	                                           }}
	    run("Close");

	    selectWindow(histogram_title);
	    while (getTitle() != histogram_title) {{
    	wait(10);
	                                           }}
        run ("Close");                                   

    }}
    while (nImages > 0) {{
    selectImage(nImages);
    wait(500);
    title = getTitle(); 
    if (title=="{last_image_name}") {{
        while (nImages > 0) {{
        selectImage(nImages);
        close();
                            }}
        run("Quit");  
                                     }}
    setOption("changes", false);
    close();
                        }}
    """

        if bits == '8bit':
            FijicodeEntropy = f"""setBatchMode("false");
    roiManager("reset");
    setOption("ScaleConversions", true);
    run("8-bit");
    title = getTitle();
    File.makeDirectory({entropy_sub_path} + title + "/");
    channel_dir_path = {entropy_sub_path} + title + "/";
    selectWindow(title);
    roiManager("Open", {rois_path} + title + ".zip");
    n_of_ROIs = roiManager("count");
    RoiManager.useNamesAsLabels("true");
    roiManager("Show All with labels");
    for (roindex = 0; roindex < n_of_ROIs; roindex++) {{
        roiManager("Select", roindex);
        roiname = getInfo("roi.name");
        index_of_dot_in_file_extension = lastIndexOf(title, ".");
        title_without_file_extension = substring(title, 0, index_of_dot_in_file_extension);
        histo_name_before_rename = "Histogram of " + title_without_file_extension;
        histogram_title = "Histogram of " + roiname;
        binCount = 256;        // Number of bins (e.g., 512, 1024)
        selectWindow(title);
        run("Histogram", "bins=256 use pixel value range");
        while (!isOpen(histo_name_before_rename)) {{
    	wait(10);  
	                                               }}
	    rename(histogram_title);
	    while (!isOpen(histogram_title)) {{
    	wait(10);
	                                      }}
	    selectImage(histogram_title);
	    while (getTitle() != histogram_title) {{
    	wait(10);  
	                                           }}
	    Table.showHistogramTable;
	    wait(50);
        total_counts = 0;
        countarray = newArray();
        binarray = newArray();
        for (c = 0; c < binCount; c++) {{
            current_count = parseInt(Table.get("count", c));
            total_counts += current_count;
            countarray[c] = current_count;
            binarray[c] = parseInt(Table.get("bin start", c));
                                        }}
        probarray = newArray();
            entropy = 0;
        for (i = 0; i < binCount; i++) {{
            bin_prob = countarray[i] / total_counts;
            probarray[i] = bin_prob;
            if (bin_prob > 0) {{
                    entropy -= bin_prob * log(bin_prob) / log(2); 
                               }}  
                                        }}
        for (i = 0; i < binCount; i++) {{
            setResult("StartingBin", i , binarray[i]);
            setResult("Count", i, countarray[i]);
            setResult("Probability", i, probarray[i]);
                                        }}
        setResult("ShannonEntropy", 0, entropy);
        selectWindow("Results");
        saveAs("Results", channel_dir_path + roiname + ".csv");
        selectWindow("Results");
        run("Close");
        selectWindow(histogram_title);
        // Wait until the selected window is really active
	    while (getTitle() != histogram_title) {{
   	    wait(10);
	                                           }}
	    run("Close");

	    selectWindow(histogram_title);
	    while (getTitle() != histogram_title) {{
    	wait(10);
	                                           }}
        run ("Close");                                        
                                               
    }}
    while (nImages > 0) {{
    selectImage(nImages);
    wait(500);
    titlos = getTitle(); 
    if (titlos=="{last_image_name}") {{
        while (nImages > 0) {{
        selectImage(nImages);
        close();
                            }}
        run("Quit");  
                                      }}
    setOption("changes", false);
    close();
                        }}
    """      

        return FijicodeEntropy

    def RunFiji (code_fiji):
            fiji_path = kwargs.get("Ffiji_path")                                      # paths here will be backslashes for windows
            images_folder_path = kwargs.get("Ffoldpath_img").replace('/', '\\')       # paths here will be frontslashes for windows and must change to backslashes to fit for fiji batch-process-macro input for windows

            print('printing below')
            print(f"{fiji_path} {images_folder_path}")    

            while is_fiji_running("imageJ-win64.exe") == True :                       # as long as previous iteration fiji is open, wait till it closes. 
                time.sleep(10)                                                        # waiting time is longer in this code because it takes longer to finalize


            if user_system == 'Windows' :
                print('system is windows')
                print(f'images folder is {images_folder_path}')
                # env = os.environ.copy()                                             # these might be useful for linux, have to see
                # env["DISPLAY"] = ":0"  
                subprocess.Popen([fiji_path])
                time.sleep(8)
                EnsureFijisActive()
                time.sleep(2)
                EnsureFijisActive()
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                pyautogui.write("Macro... ")
                time.sleep(1.5)
                pyautogui.press('enter')                                              # Simulates pressing the "Escape" key
                time.sleep(2)

                for tabpresses in range (1):
                    pyautogui.press('tab')
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'a', interval=0.2)
                time.sleep(1)
                #pyautogui.press('delete')
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
    GetShannonEntropy()

    
    





