// This code totally ignores the rois from the image (shadows them)
// so that other measurements can be taken without being affected by the rois.
// For instance, Mean measurement of a larger region, skipping entirely the rois.


// To avoid opening filedialog everytime during Process->Batch->Macro, try to call the paths from here. 
RoisFolder = call("java.lang.System.getProperty", "macro.roisfolder") + "";
SaveFolder = call("java.lang.System.getProperty", "macro.savefolder") + "";

// Check if the variable is empty or still "null". This means the path has not been defined yet, that is, it's 1st iteration
if (RoisFolder == "null" || RoisFolder == "") {
    RoisFolder = getDirectory("Choose directory containing zipped ROIs");
    if (RoisFolder == "") exit("User canceled.");
    if (!endsWith(RoisFolder, File.separator)) RoisFolder += File.separator;
    call("java.lang.System.setProperty", "macro.roisfolder", RoisFolder);
}


// Check if the variable is empty or still "null". This means the path has not been defined yet, that is, it's 1st iteration
if (SaveFolder == "null" || SaveFolder == "") {
    SaveFolder = getDirectory("Choose directory to save measurements");
    if (SaveFolder == "") exit("User canceled.");
    if (!endsWith(SaveFolder, File.separator)) SaveFolder += File.separator;
    call("java.lang.System.setProperty", "macro.savefolder", SaveFolder);
}

// true might work too. This is to visualize whats happening
setBatchMode(false);

title = getTitle();
run("Duplicate...", "title=dummy.tif");
getStatistics(area, mean, min, max, std, histogram);
changeValues(max,max,min); 
getStatistics(area, mean, min, max, std, histogram);
rightail=max;
print(rightail);
close();


selectImage(title);
run("Duplicate...", "title=duplicate.tif");
selectImage("duplicate.tif");
// to achieve uniformal convertion, reduce the image bit size
setOption("ScaleConversions", true);
run("8-bit");
roiManager("Open", RoisFolder + title + ".zip");
// smooth the background and capture it better
run("Gaussian Blur...", "sigma=1");
// and set a tolerance (range) that flood can continue between pixels
run("Wand Tool...", "tolerance=25 mode=Legacy");
// use magic wand to click on the top left (which should always be background)
// and select all background
doWand(0, 0, 25.0, "Legacy");
// then start the floodfill for values that do not surpass 25
floodFill(0, 0);
// add the background surrounding the brain to the roi manager too
roiManager("Add");

//in case the user wants to enlarge the rois to compare roi intensity with surrounding
//background (bg) intensity, it would be catastrophic to enlarge the bg too. 
//So we save the roi as background to remove it later
//renaming is for troubleshooting. We cannot select rois based on their name directly
//but if the bg roi is still there at the end of execution, sth went wrong
//bg was added last, so :
roiManager("Select", roiManager("count") - 1); 
roiManager("Rename", "background");

//fill every roi with white too (like deleting that regions)

run("ROI Manager...");
n = roiManager('count');
for (i = 0; i < n; i++) {
    roiManager('select', i);
    roiManager("fill");
}
// select only the whited parts (where rois were)
setThreshold(255, 255);
run("Create Mask");
run("Create Selection");
// safer way to transfer the selection is via adding it to roi manager first
roiManager("Add");
// select the last-added ROI, which is the set of all rois from the mask
roiManager("Select", roiManager("count") - 1); 
roiManager("Rename", "all_rois_mask");
selectImage(title);
roiManager("Select", roiManager("count") - 1);
roiManager("fill");
// include all values from 0 to the penultimate maximum value
// only the background value and the filled white roi regions will be there
// and of course the one (or more than one) pixels that had the highest value
// we can live with ignoring that one
setThreshold(0, rightail);
// remove all_rois_mask roi which should be last
roiManager("Select", roiManager("count") - 1);
roiManager("delete");
// remove background roi, which should become last now
roiManager("Select", roiManager("count") - 1);
roiManager("delete");

// now start enlarging the rois (and adding them as new ones) so that you measure them
// IMPORTANT : If Show labels is ticked, new rois with same names will be created below
// the original ones. If it is not ticked, then the new ones will directly replace the old ones!
// Because it is preferable that the user sees the enlargment range, here it will be ticked.

roiManager("show all")
original_n = roiManager('count');
for (i = 0; i < original_n; i++) {
    roiManager('select', i);
    run("Enlarge...", "enlarge=10");
    roiManager("Add");
}

//print('fininished adding') ;
//alln=roiManager('count');
//print('overal n now is : ');
//print(alln);

//after creating the new rois, deleting the original ones 
for (i = 0; i < original_n; i++) {
    roiManager('select', 0);
    roiManager("delete");
    print('deleted ', i);
}


waitForUser('wait');
run("Fresh Start");