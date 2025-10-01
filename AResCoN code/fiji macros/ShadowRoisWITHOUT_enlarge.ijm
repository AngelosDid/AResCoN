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
// get penultimate maximum value to create the range 
// it is problematic to get max because the float decimals depend on the image max
// thereby, a duplicate image is made, where the maximum value is changed to minimum
// this, way, a new max can be calculated
getStatistics(area, mean, min, max, std, histogram);
changeValues(max,max,min); 
getStatistics(area, mean, min, max, std, histogram);
rightail=max;
close();

// make the background white
// this is useful to get rid of background contrast for rois close to contours later (not in this macro)
selectImage(title);
run("Duplicate...", "title=duplicate.tif");
selectImage("duplicate.tif");
// to achieve uniformal convertion, reduce the image bit size
setOption("ScaleConversions", true);
run("8-bit");
// smooth the background and capture it better
run("Gaussian Blur...", "sigma=1");
// and set a tolerance (range) that flood can continue between pixels
run("Wand Tool...", "tolerance=25 mode=Legacy");
// use magic wand to click on the top left (which should always be background)
// and select all background
doWand(0, 0, 25.0, "Legacy");
// then start the floodfill for values that do not surpass 25
floodFill(0, 0);
//fill every roi with white too (like deleting that regions)
roiManager("Open", RoisFolder + title + ".zip");
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
run("Fresh Start");




