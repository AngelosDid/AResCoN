// This macro code was found in https://forum.image.sc/t/imagej-how-to-shrink-roi-by-percentage/99357/14

// iterate through ROIs
for(i=0; i<RoiManager.size; i++) {
  close("Mask");
  roiManager("Select", i);
  run("Create Mask");
  run("Create Selection");
  originalArea = getValue("Area");
  while(getValue("Area") > (0.5 * originalArea) ) {
    run("Erode");
    run("Create Selection");
    roiManager("Update");
  }
  print(i, RoiManager.getName(i), originalArea, getValue("Area"));
}
close("Mask");
roiManager("Show All");