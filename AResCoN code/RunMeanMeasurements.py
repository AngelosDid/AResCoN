import subprocess
import pyautogui
import pyperclip
import time
import psutil
import pygetwindow
import re
from os import listdir


# This script should run after AutoHotKey is installed in the system
# There is an error occuring in some images (active image does not have a selection) which is not problematic per se
# but a keystroke must be applied to bypass the error message.
# The script is included in the data of Areson (autoenter.ahk)
# Pay attention to the AutoHotKey version used. AutoHotKey syntax changes across different versions.

def GetSurroundingMean (**kwargs) :  

    user_system = kwargs.get("winlin_mg")  

    def CodeStorage ():
        """Converts the fiji maro code based on user input and applies a few additional changes. 
           Importantly, detects the name of the last image in the folder so that when macro finishes Fiji shuts down completely"""
        rois_path                 = kwargs.get("roiresults_mg").replace('\\', '/')         # paths here will be backslashes for windows but wont work with INSIDE fiji macro in windows unless they become forward
        rois_path                 = '"' + rois_path + '/"'                                 # adding quotes to the path to make it string INSIDE the fiji macro. Add a frontslash in the end
        save_path                 = kwargs.get("measure_sub_path_mg").replace('\\', '/')   # take the subdirectory path of the measurement that corresponds to a planeN
        save_path                 = '"' + save_path + '/"' 
        last_image_name           = listdir(kwargs.get("foldpath_img_mg"))[-1]             # gets the name of the last image inside the folder with the images. If the title of the image running in the macro is the same to this, fiji shuts down
        ahk_path                  = kwargs.get("ahk_script").replace('\\', '/')
        ahkexe_path               = kwargs.get("ahk_exec").replace('\\', '/')
        setbatch_addition_to_fiji = 'setBatchMode(true);'                                  # by default, this variable is a string corresponding to a command that hides fiji display
        enlargement_factor        = kwargs.get('enlarge_factor_mg')
        masks_path                = kwargs.get('maskpath').replace('\\', '/')
        masks_path                = '"' + masks_path + '/"'
        if kwargs.get("visuals")==True: setbatch_addition_to_fiji = 'setBatchMode(false);' # but if the user has selected to visualize, then it turns to a fiji command 


        FijicodeMeasurements = f"""{setbatch_addition_to_fiji}
// Stage 1 : Apply threshold to separate bright objects from background. Fill holes to protect ventricles from background
// Stage 2:  Detect largest background object, which must be the hemisphere itself and unROI the rest
//        :  By unROIng the rest, we can later create a convex hull based on rois inside the hemishpere object only
//        :  convex hull is a polygon shaped using the very exterior rois (thats why we unROI objects outside the hemisphere)
// Stage 3:  Open the ROIs again. Now you have the selected background at index 0 and all the rest rois.
// Stage 4:  Whiten (clear) the reverse selection of the hemishpere object, which is everything else lying in the background.
//           Then delete the selection from the rois.
// Stage4a:  In case there is an error with reverse selection, call autohotkey to initiate a delayed enter press
// Stage 5:  Run measurements and get standard deviation of all rois. Rois with 0 stdev are either part of the whitened (cleared) background
//           or faulty detections -artifacts- inside the hemisphere (might be like 5 out of a thousand real rois with cellpose)
// Stage 6:  Now that the outliers are deleted, create the convex hull, which is a polygon based on exterior rois, hopefully all inside the 
//           hemishpere. If a roi survived the autothreshold and was an artifact roi which is in fact outside the hemisphere, the convex hull 
//           will be imperfect in that region. This should rarely play any significant role though.
// Stage 7:  Get the inverse selection of the convex hull and make everything outside the latter white (255)
// Stage 8:  Make all ROIs white too. Then create a mask that contains all whitened parts (that is, the ROIs and the space outside convex hull).
//           Get the selection of the area of the mask and add the selection as ROI.
// Stage 9:  Swap to the real image (not the duplicate images anymore), chose the ROI with all parts whitened in one of the duplicates and whiten 
//           the same regions (ROIs and bacground outside convex hull) too.
//Stage10:   Create a duplicate of the origin image (bot duplicate and image now containing the whitened parts) and change its maximum pixel value
//           in the image to minimum. Then get the maximum value again, which is in fact the original penultimate value. This way you avoid looping 
//           through all pixel to find the penultimate. 
//Stage 11:  Go back to the original (whitened now) image and set threshold between 0 and penultimate value. Now everything in the image apart from
//           the original max pixel value(s), the region outside the convex hull and the rois is taken into account. The rest is ignored during 
//           measurements. This allows to measure surrounding regions without the impact of the background. Thats the whole point! 
//Stage 12:  Enlarge the region of each roi and get the measurements again, after having cleared the previous measurements. 
//           First create a bounding box to normalize the roi shape and avoid exceptions that are raised by bad rois. 
//           We want all ROIs to be measured to be able to paste them later (another function) to the csv measurements without order mismatches
//           For future reference : consider implementing the straighten command if there are mere lines as rois for whatever reason
//           if (selectionType() == 5)  ...

title = getTitle();

selectImage(title);
run("Duplicate...", "title=duplicate.tif");
run("Duplicate...", "title=dupforbg.tif");
selectImage("dupforbg.tif");
run("8-bit");
// to achieve uniformal convertion, reduce the image bit size
setOption("ScaleConversions", true);
run("Gaussian Blur...", "sigma=10");
run("Auto Threshold", "method=MinError(I) white");
run("Fill Holes");

run("Convert to Mask");
run("Invert"); // Makes the object white if it was black

run("Analyze Particles...", "size=0-Infinity display clear add");
areas = Table.getColumn("Area");
particles_N = Table.size;
ranked = Array.rankPositions(areas);

// Select the largest object and center the view on it
roiManager("Select", ranked[particles_N-1]);
RoiManager.useNamesAsLabels(true);

run("To Selection");
//waitForUser("to selection");
run("Make Inverse");
//waitForUser("made inverse");
//add the reverse selection of the largest object (hemishpere) again as last (all others including its original non-reversed duplicate will be deleted)
// if selectiontype is -1, an error pops up that can only be skipped with keystroke
// an ahk file with a delay of 7 seconds will be executed and simulate a keystroke
// fiji macro only runs asynchronously with exec, and calling a python file for autogui would mess the existent running
// thats why an ahk file is selected instead. Alternatives could be java files executed with fiji exec using cmd
if (selectionType() == -1) {{

//ahkExe = 'C:/Program Files/AutoHotkey/UX/AutoHotkeyUX.exe';
//ahkScript = 'C:/Users/angdid/Desktop/autoenter.ahk';
ahkexe_pathi = "{ahkexe_path}";
ahk_pathi    = "{ahk_path}" ;
cmd = '"' + ahkexe_pathi + '" "' + ahk_pathi + '"';




//to make it asynchronous, we set waitforcompletion to false
setOption("WaitForCompletion", false);
exec(cmd);
// this is the command that yields active image does not have a selection error
//the former execution of ahk file is already running and will eventually simulate press of enter
roiManager("Add");
particles_N = particles_N+1;
}} else {{
roiManager("Add");
particles_N = particles_N+1; }}


for (i = 0; i < particles_N-1; i++) {{
    roiManager('select', 0);
    roiManager("delete");
                                     }}
close("Results");
close("dupforbg.tif");
selectImage("duplicate.tif");
roiManager("Open", {rois_path} + title + ".zip");
roiManager('select', 0);
run("Clear", "slice"); //make the background (which is the reverse selection of hemisphere) white
roiManager('select', 0);
roiManager("delete");

roiManager("show all");
roiManager("Measure");


roiCount = roiManager("count");

//backwards iteration to avoid changing indices
// rois that belong to the background based on threshold will be ignored during convex hull formation
for (i = roiCount - 1; i >= 0; i--) {{
    roiManager("Select", i);
    getStatistics(area, mean, min, max, std);
	if (std == 0) {{
		print("Roi index " + i + "will be removed from convex hull (0 std)");
	    roiManager("delete");
				  }}
}}


roiManager("select", "all");
roiManager("combine");
// Get the convex hull using a groovy script saved inside a subfolder in plugins, named Convex_Rois.groovy. 
run("Convex Rois");
// The script has added the convex to the roi manager already
run("Make Inverse");
setForegroundColor(255, 255, 255); 
// Fill the inverse selection of the convex hull with white
run("Fill", "slice");   
roiManager("reset");
// We re-open all ROIs, now to include those who were excluded for convex hull selection. We need them to avoid indexing mismatch 
// since these values will be eventually pasted in the saved metrics of each image in another function
roiManager("Open", {rois_path} + title + ".zip");
roiManager('select', 0);
run("8-bit");


//fill every roi with white too (like deleting that regions)

run("ROI Manager...");
n = roiManager('count');
for (i = 0; i < n; i++) {{
    roiManager('select', i);
    roiManager("fill");
}}
// select only the whited parts (where rois were)
setThreshold(255, 255);
run("Create Mask");
run("Create Selection");
// safer way to transfer the selection is via adding it to roi manager first
roiManager("Add");
// select the last-added ROI, which is the set of all rois from the mask
roiManager("Select", roiManager("count") - 1); 
roiManager("Rename", "all_rois_mask");
close("duplicate.tif");
selectImage(title);
RoiManager.selectByName("all_rois_mask");
roiManager("fill");
// we need to set a threshold to separate all image values from background and rois
// threshold also helps visualizing what is excluded and what not
// We include all values from 0 to the penultimate maximum value
// only the background value and the filled white roi regions will not be there
// and of course the one (or more than one) pixels that had the highest value in the image
// we can live with ignoring that one. Should not affect measurements.
run("Duplicate...", "title=dummy.tif");
selectImage("dummy.tif");
getStatistics(area, mean, min, max, std, histogram);
changeValues(max,max,min); 
getStatistics(area, mean, min, max, std, histogram);
rightail=max;
print(rightail);
close("dummy.tif");
selectImage(title);
setThreshold(0, rightail);
// remove all_rois_mask roi, which should be last
roiManager("Select", roiManager("count") - 1);
roiManager("delete");
// remove background roi, which should become last now
roiManager("Select", roiManager("count") - 1);
roiManager("delete");


// now start enlarging the rois (and adding them as new ones) so that you measure them
// IMPORTANT : If Show labels is ticked, new rois with same names will be created below
// the original ones. If it is not ticked, then the new ones will directly replace the old ones!
// Because it is preferable that the user sees the enlargment range, here it will be ticked.

run("Clear Results");
roiManager("reset");
roiManager("Open", {rois_path} + title + ".zip");
roiManager("Show All without labels");
original_n = roiManager('count');
// loop through ROIs, create a bounding box to normalize them and enlarge safely
// and lastly, add the enlarged region to Roimanager and give the same roi name
for (i = 0; i < original_n; i++) {{
    roiManager('select', i);
    selectedRoiname = Roi.getName;
    run("To Bounding Box");
    run("Enlarge...", "enlarge={enlargement_factor}");
    roiManager("Add");
    roiManager('select', roiManager('count')-1);
    roiManager("rename", selectedRoiname);
}}

//after creating the new rois, deleting the original ones 
for (i = 0; i < original_n; i++) {{
    roiManager('select', 0);
    roiManager("delete");
}}

// save the new csv measurements (it is a bit tricky to save only mean value in a similar csv format
// so we save all checked measurements in Fiji Set Measurements although the rest are not needed)
// show all to ensure that we will not count a single roi

print("Total ROI number is " + roiManager("count"));
roiManager("Measure");
roiManager("Show All");
selectWindow("Results"); // Select the results otherwise potential log exceptions will be saved instead
saveAs("Results", {save_path} + title + ".csv");
saveAs("Tiff", {masks_path} + title);


if (title=="{last_image_name}") {{
    while (nImages > 0) {{
    selectImage(nImages);
    close();
                        }}
    run("Quit");
                                }}

run("Fresh Start");"""
        return FijicodeMeasurements

    def RunFiji (code_fiji):
            fiji_path = kwargs.get("fiji_path")                                       # paths here will be backslashes for windows
            images_folder_path = kwargs.get("foldpath_img_mg").replace('/', '\\')     # paths here will be frontslashes for windows and must change to backslashes to fit for fiji batch-process-macro input for windows
            initial_fiji_sleep = 13                                                   # time it takes for fiji to open (or reopen). If low, the autogui wont run properly
            print('printing below')
            print(f"{fiji_path} {images_folder_path}")    

            while is_fiji_running("imageJ-win64.exe") == True :                       # as long as previous iteration fiji is open, wait till it closes. 
                time.sleep(3)  

            if user_system == 'Windows' :
                print('system is windows')
                print(f'images folder is {images_folder_path}')
                subprocess.Popen([fiji_path])
                time.sleep(initial_fiji_sleep)
                EnsureFijisActive()
                time.sleep(2)
                EnsureFijisActive()                                                  #sometimes it doesnt work if its only tried once
                time.sleep(2)
                EnsureFijisActive()                                                  #sometimes it doesnt work if its only tried once
                # time.sleep(2)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'l') 
                time.sleep(0.2)
                # time.sleep(1.5)
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
        """Searches if for fiji in the open windows and makes it the active window so that pyautogui can work on top of it.
           It is crucial to have any other windows-tabs with the name fiji or imagej closed!"""

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
    GetSurroundingMean()
