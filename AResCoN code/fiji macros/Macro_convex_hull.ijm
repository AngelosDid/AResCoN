path = "C:/Users/angdid/Desktop/4um_2x2_correct_44_percent.ome_plane4.tif.zip"

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
run("Make Inverse");
//add the reverse selection of the largest object (hemishpere) again as last (all others including its original non-reversed duplicate will be deleted)
roiManager("Add");
particles_N = particles_N+1

for (i = 0; i < particles_N-1; i++) {
    roiManager('select', 0);
    roiManager("delete");
}

close("Results");
close("dupforbg.tif");
selectImage("duplicate.tif");
roiManager("Open", path);
roiManager('select', 0);
run("Clear", "slice"); //make the background (which is the reverse selection of hemisphere) white
roiManager('select', 0);
roiManager("delete");

roiManager("show all");
roiManager("Measure");


roiCount = roiManager("count");

//backwards iteration to avoid changing indices
for (i = roiCount - 1; i >= 0; i--) {
    roiManager("Select", i);
    getStatistics(area, mean, min, max, std);
	if (std == 0) {
		print("Roi index " + i + "will be removed from convex hull (0 std)");
	    roiManager("delete");
				  }
}


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
roiManager("Open", path);
roiManager('select', 0);
run("8-bit");


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
roiManager("Open", path);
roiManager("Show All without labels");
original_n = roiManager('count');
// loop through ROIs, create a bounding box to normalize them and enlarge safely
// and lastly, add the enlarged region to Roimanager and give the same roi name
for (i = 0; i < original_n; i++) {
    roiManager('select', i);
    selectedRoiname = Roi.getName;
    run("To Bounding Box");
    run("Enlarge...", "enlarge=10");
    roiManager("Add");
    roiManager('select', roiManager('count')-1);
    roiManager("rename", selectedRoiname);
}

//after creating the new rois, deleting the original ones 
for (i = 0; i < original_n; i++) {
    roiManager('select', 0);
    roiManager("delete");
}

// save the new csv measurements (it is a bit tricky to save only mean value in a similar csv format
// so we save all checked measurements in Fiji Set Measurements although the rest are not needed)
// show all to ensure that we will not count a single roi

roiManager("Measure");
roiManager("Show All");
selectWindow("Results"); // Select the results otherwise potential log exceptions will be saved instead
//saveAs("Results", {save_path} + title + ".csv");
saveAs("Tiff", "C:/Users/angdid/Desktop/masks/" + title);