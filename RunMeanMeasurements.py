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
    fiji_delay  = kwargs.get('fijiseconds')
 

    def CodeStorage ():
        """Converts the fiji maro code based on user input and applies a few additional changes. 
           Importantly, detects the name of the last image in the folder so that when macro finishes Fiji shuts down completely"""
        rois_path                 = kwargs.get("roiresults_mg").replace('\\', '/')         # paths here will be backslashes for windows but wont work with INSIDE fiji macro in windows unless they become forward
        rois_path                 = '"' + rois_path + '/"'                                 # adding quotes to the path to make it string INSIDE the fiji macro. Add a frontslash in the end
        save_path                 = kwargs.get("measure_sub_path_mg").replace('\\', '/')   # take the subdirectory path of the measurement that corresponds to a planeN
        save_path                 = '"' + save_path + '/"' 
        img_subdir_path           = kwargs.get ("foldpath_img_mg").replace('\\', '/')      # take the subdirectory path of the images
        img_subdir_path           = '"' + img_subdir_path + '/"'
        last_image_name           = listdir(kwargs.get("foldpath_img_mg"))[-1]             # gets the name of the last image inside the folder with the images. If the title of the image running in the macro is the same to this, fiji shuts down
        ahk_path                  = kwargs.get("ahk_script").replace('\\', '/')
        ahkexe_path               = kwargs.get("ahk_exec").replace('\\', '/')
        setbatch_addition_to_fiji = 'setBatchMode(true);'                                  # by default, this variable is a string corresponding to a command that hides fiji display
        enlargement_factor        = kwargs.get('enlarge_factor_mg')
        container                 = kwargs.get('transmitter_path').replace('\\', '/')      # container is the path where transmitter from fiji and files returned from python to be used from fiji will be saved
        container                 = '"' + container + '/"'
        sanity                    = kwargs.get('sanity')                                   # if 'Yes', then for every plane image a new image will be produced showing the thresholding and the NaN values
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
// Stage 7:  Make a zip file with a single ROI of the convex hull and save it in a container folder
// Stage 8:  Create a text file inside the container folder that includes information about
//           1) image path, 2)rois path, 3)enlargement factor, and 4)image title
//           
// Stage 9:  Wait until TurnRoisToNaNandFindBboxes reads the convex hull zip file and the text file and returns an image with NaN ROIs and surrounding bounding boxes
// Stage10:  Open the python image and the ROIs and apply measurements in Fiji.
// Stage11:  Save measurements
// Stage12:  Burn the bounding boxes ROIs to the image with NaNs and save it as a montage for sanity checks of the convex hull
//           You should not see many ROIs in the background. If you do, then the threshold method might havent worked properly
// Stage last : Refresh start if there are more images loaded in the process-batch-macro. Otherwise quit. In both cases, delete these files 
//              (1) zip file that was created and contained the convex hull 
//              (2) transmitterR text file that contained path and factor information for python
//              (3) Image file that python provided with NaN ROIs
//              (4) zip file that python provided with enlarged bounding boxes

// S T A G E  1
title = getTitle();
decision_sanity = "{sanity}";

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

// S T A G E  2
run("Analyze Particles...", "size=0-Infinity display clear add");
areas = Table.getColumn("Area");
particles_N = Table.size;
ranked = Array.rankPositions(areas);

// S T A G E  3
// Select the largest object and center the view on it
roiManager("Select", ranked[particles_N-1]);
RoiManager.useNamesAsLabels(true);

// S T A G E  4
run("To Selection");
//waitForUser("to selection");
run("Make Inverse");
//waitForUser("made inverse");
//add the reverse selection of the largest object (hemishpere) again as last (all others including its original non-reversed duplicate will be deleted)
// if selectiontype is -1, an error pops up that can only be skipped with keystroke
// an ahk file with a delay of 7 seconds will be executed and simulate a keystroke
// fiji macro only runs asynchronously with exec, and calling a python file for autogui would mess the existent running
// thats why an ahk file is selected instead. Alternatives could be java files executed with fiji exec using cmd

// S T A G E  4a
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
// we add the inverse selection of the largest ROI based on analyse particles to the Roi Manager so that we know its position (last added)
roiManager("Add");
particles_N = particles_N+1;
}} else {{
roiManager("Add");
particles_N = particles_N+1; }}

// delete all the other ROIs of analyzed particles
for (i = 0; i < particles_N-1; i++) {{
    roiManager('select', 0);
    roiManager("delete");
                                     }}
close("Results");
close("dupforbg.tif");
selectImage("duplicate.tif");
roiManager("Open", {rois_path} + title + ".zip");
roiManager('select', 0);
//make the background (which is the reverse selection of hemisphere) white
run("Clear", "slice"); 
roiManager('select', 0);
roiManager("delete");


// S T A G E  5
roiManager("show all");
roiManager("Measure");

roiCount = roiManager("count");
print("roicount is" + roiCount);

// I am not entirely how in some cases roiCount is 0 but it happens and the this code fixes the error occuring after clearing the reverse selection (background outside slice)
// Possible Interperation : sometimes roicount is 0, probably because there is no selection of largest particle for some reason in step 4 
// (or merely the reverse selection gets unselected afterwards since I am initially able to see the largest particle numbered as 1 after thresholding),
// which leads to deleting the first cell/nucleus roi observation (instead of the large particle roi which by default is first and waits to be deleted). 
// This first roi observation may be the only one existing in cases where there are no other cell/nuclei rois in the image.
// Mind that the cellpose inference notebook adds an artificial roi on purpose to avoid errors when there are noi inferences, so there must be always at least one cell/nucleus roi. 
// In this case, we want to re-add an artificial ROI (top left) to ensure that stage 5 will run.
// If the interpretation is correct, this means that in some cases where this problem of selection of largest particle (or selecting it reverse area) after thresholding occurs, one roi out of the many is deleted.
// This is hardly a problem in sets of hundreds or thousands of rois, but it is noted here.

if (roiCount == 0) {{

    // probably unecessary to reset the manager but better safe
    print("Something went wrong and all rois were deleted so I am adding back the zip file with rois");
    roiManager("Reset");           
    roiManager("Open", {rois_path} + title + ".zip");

    // below a previous way of resolving the problem. 
    //print("All rois were deleted so I am adding an artificial one to avoid errors");
    //// creating the necessary arrays to create the polygon. This is a reasonably low number of pixels. If the image has less will fail.
    //x = newArray(10, 40, 40, 10);  
    //y = newArray(20, 20, 35, 35);  
    //// Create the polygon ROI
    //makeSelection("polygon", x, y);
    //run("ROI Manager...");
    //roiManager("Add");   
    //roiManager('select', 0);
    //roiManager("Rename", "001_001");

                    }}

//Continuing with step 5...
//backwards iteration to avoid changing indices
// rois that belong to the background based on threshold will be ignored during convex hull formation
for (i = roiCount - 1; i >= 0; i--) {{
    roiManager("Select", i);
    getStatistics(area, mean, min, max, std);
    // we are inserting the roiManager("count") > 1 condition in cases where all ROIs are outside the thresholded slice to prevent error.
	if (std == 0 && roiManager("count") > 1) {{
		print("Roi index " + i + "will be removed from convex hull (0 std)");
        roiManager("delete");
				                             }}
    // as commented above, we will not delete the ROI even it if has 0std if there is no other ROI                         
	if (std == 0 && roiManager("count") < 2)      {{
		print("Roi index " + i + "will be kept although it has 0 std to avoid error");
                                                  }}

                                    }}

// S T A G E  6
roiManager("select", "all");
roiManager("combine");
// Get the convex hull using a groovy script saved inside a subfolder in plugins, named Convex_Rois.groovy. 
run("Convex Rois");
// The script has added the convex to the roi manager already
run("Make Inverse");

// S T A G E  7
// save the convex hull so that it can be used by python
// the name includes _ConvexHullforAResCoN to eliminate any chance of an image file having it itself 
roiManager("save selected", {container} + title + "_ConvexHullforAResCoN.zip");


// S T A G E  8
// Create a text file as a signal for python to start
// this file tells python which image and rois to use for bounding boxes of ROIs, how much to enlarge bounding boxes, as well as image title
// Hence, python searching for the inverse.zip and the transmitter.txt which include the info above
tfile = File.open({container} + title + "_transmitterR.txt");
print(tfile, {img_subdir_path} + title);
print(tfile, {rois_path} + title + ".zip");
print(tfile, {enlargement_factor}); 
print(tfile, title); 
File.close(tfile);
showStatus("Waiting for Arescon to provide bounding boxes of ROIs");


// S T A G E  9
// wait until Arescon has pasted there the file with enlarged bounding boxes ROIs
while (!File.exists({container} + title + "_BBoxRois.zip")) {{
    wait(1000);
}}

// wait until Arescon has pasted there the image with NaN pixels for ROIs and background (inverse of convex hull) 
showStatus("Waiting for Arescon to respond and provide image with NaN ROIs");
while (!File.exists({container} + title)) {{
    wait(1000);
}}
close("*");
// some more waiting to ensure that the image will be read when it is fully created
wait(5000);
// try to clear results to avoid getting the name of duplicate in the results instead of the image name


run("Clear Results");

print("passed stage 9");


// S T A G E  10
open({container} + title);
wait(2000);
// reseting roi manager to load all bounding boxes of all rois, including the ones in the background

roiManager("reset");
roiManager("Open", {container} + title + "_BBoxRois.zip");


roiManager("Measure");
roiManager("Show All");

// S T A G E  11

// Select the results otherwise potential log exceptions will be saved instead
selectWindow("Results"); 
saveAs("Results", {save_path} + title + ".csv");

// S T A G E  12

//selectImage(title);
roiManager("Select All");
// Create one active selection of all ROIs to burn them better in the image
roiManager("Combine");  
setLineWidth(4);
run("Draw");
selectImage(title);
if (decision_sanity == "Yes") {{
saveAs("Tiff", {container} + title + "_SanityCheck.tif");
close("*");            }}

// L A S T   S T A G E
// if it is the last image in the batch, then a stop file will be created to 
if (title=="{last_image_name}") {{
    while (nImages > 0) {{
    selectImage(nImages);
    close();
                        }}
    File.delete ({container} + title + "_ConvexHullforAResCoN.zip");
    wait(20);
    File.delete ({container} + title + "_transmitterR.txt");
    wait(20);
    File.delete ({container} + title);
    wait(20);
    File.delete ({container} + title + "_BBoxRois.zip");
    run("Quit");
                                }}

// delete the files in the container to prevent confusion while being read by AResCoN. This is crucial
File.delete ({container} + title + "_ConvexHullforAResCoN.zip");
wait(20);
File.delete ({container} + title + "_transmitterR.txt");
wait(20);
File.delete ({container} + title);
wait(20);
File.delete ({container} + title + "_BBoxRois.zip");


run("Fresh Start");"""
        return FijicodeMeasurements

    def RunFiji (code_fiji):
            fiji_path = kwargs.get("fiji_path")                                       # paths here will be backslashes for windows
            images_folder_path = kwargs.get("foldpath_img_mg").replace('/', '\\')     # paths here will be frontslashes for windows and must change to backslashes to fit for fiji batch-process-macro input for windows
            print('printing below')
            print(f"{fiji_path} {images_folder_path}")    

            while is_fiji_running("imageJ-win64.exe") == True :                       # as long as previous iteration fiji is open, wait till it closes. 
                time.sleep(3)  

            if user_system == 'Windows' :
                print('system is windows')
                print(f'images folder is {images_folder_path}')
                subprocess.Popen([fiji_path])
                time.sleep(fiji_delay)
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
                
                # move to output field in order to clear it
                for tabpresses in range (2):
                    pyautogui.press('tab')
                # should have reached output field now
                pyautogui.hotkey('ctrl', 'a', interval=0.2)     
                time.sleep(0.1)
                pyautogui.press('backspace')
                time.sleep(0.2)

                
                for delpresses in range (5):
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
                        time.sleep(0.2)
                    
                    if window.isActive:
                        return
                    else :
                        window.minimize()
                        window.maximize()
                        window.restore()
                        time.sleep(0.2)
                        return


                        
    macro_fiji = CodeStorage()
    RunFiji(macro_fiji)             

    
if __name__ == "__main__" : 
    GetSurroundingMean()
