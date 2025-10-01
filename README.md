# A Researcher is Counting Neurons (AResCoN)
AResCoN is a pipeline developed to perform accurate filtering of cells or nuclei following initial inferences. It uses the output of Cellpose or Stardist and utilizes Fiji to obtain measurements that can be used either for X and Y axis cell filtering or Z-axis cell filtering within a small range of planes.

AResCoN is particularly useful in setups where complete imaging of a slice (hemishpere or brain) is required but it can also be used for isolated regions within a 2D slice. 

## 📋 Prerequisites
* AResCoN works optimally with **16-bit** images and has been tested so far only with 20x magnified captures. 8-bit images and lower or higher magnifications are likely to work too.
  
* AResCoN has only be tested with .tif images. Different channels must be tested separately. 
  
* For a complete utilization of its features, it requires images from small multi-stacks (usually comprising up to 10 planes). Due to the wiggly nature of a mounted tissue -as well as the slightly different depth of cells and nuclei populating it- the acquisition of several planes can guarantee at least one crisp capture of each cell-nucleus across many planes. AReScON can filter out Cellpose predictions that are detected over separate planes and correspond to the same observation.

* Please use the Fiji/ImageJ version provided in this repository.
  
* An installation of AutoHotKeysUX is necessary.

## Step 1 

Run Cellpose inferences and paste the .tif mask output to a ROIs_folder with plane subdirectories

