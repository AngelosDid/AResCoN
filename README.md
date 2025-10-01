# A Researcher is Counting Neurons (AResCoN)
AResCoN is a pipeline developed to perform accurate filtering of cells or nuclei following initial inferences. It uses the output of Cellpose or Stardist and utilizes Fiji to obtain measurements that can be used either for X and Y axis cell filtering or Z-axis cell filtering within a small range of planes.

AResCoN is particularly useful in setups where complete imaging of a slice (hemishpere or brain) is required but it can also be used for isolated regions within a 2D slice. 

## 📋 Prerequisites
* AResCoN works optimally with **16-bit** images and has been tested so far only with 20x magnified captures. 8-bit images and lower or higher magnifications are likely to work too.
  
* AResCoN has only be tested with .tif images. Different channels must be tested separately. 
  
* For a complete utilization of its features, it requires images from small multi-stacks (usually comprising up to 10 planes). Due to the wiggly nature of a mounted tissue -as well as the slightly different depth of cells and nuclei populating it- the acquisition of several planes can guarantee at least one crisp capture of each cell-nucleus across many planes. AReScON can filter out Cellpose predictions that are detected over separate planes and correspond to the same observation.

* Please use the Fiji/ImageJ version provided in this repository.
  
* An installation of AutoHotKeysUX is necessary.

## Step 1 (Get independent planes)

Use the 'Stack to Images' ImageJ function and save separately each plane. Images **must end** to _plane1.tif, _plane2.tif and so on. Make sure that each plane includes only a single channel.



## Step 2 (Paste images to corresponding planeN folder)

Create a main Rois_Folder and then create as many planeN_Images subdirectories as the maximum plane that you have. For instance, if brain a consists of 4 planes and brain b of 5, then create 5 planeN subdirectories, where N corresponds to a number from 1 to 5. plane1_images must contain a_plane1.tif and b_plane1.tif , plane2_images must contain a_plane2.tif and b_plane2.tif and so on.

<p align="center">
  <img src="https://github.com/user-attachments/assets/0dcfdb38-6ed3-4316-ae5a-735196c7b6da" width="700">
</p>




## Step 3 (Convert masks to ROIs)

Run Cellpose inferences and paste each .tif mask output to the respective planeN subdirectory of a main ROIs folder. For instance, if there are 2 multistacks of brain a and brain b, both comprising 5 planes, plane1_ROIs must contain a_plane1.tif and b_plane1.tif, plane2_ROIs must contain a_plane2.tif and b_plane2.tif and so on.

The names of the .tif masks must be **identical** to the names of the initial _planeN.tif images. The provided Cellpose notebook adds an additional _predicted_mask to each mask output name. Remove this additional part from all images. 

If you aren't using planes from small multistacks and are only interested in filtering single shots, place all your .tif output masks inside the plane1_Rois subdirectory of the main ROIs folder.

<p align="center">
  <img src="https://github.com/user-attachments/assets/aa93acc5-e427-456e-981d-6b21afbce24c" width="700">
</p>

After you ensure that the architecture is correct, open the AResCoN code folder with VS code and run the Multiplane_cell_detection17.py. A GUI window will open. 

Click at the Microscopy tab and make sure that the number of zplanes corresponds to your maximum z-plane. 

⚠️ Disclaimer:  It is not guaranteed that Cellpose can run successfuly if you have images consisted of a different number of planes. This is something that will be tested soon. Therefore, it is strongly recommended to ensure that all your test files have an equal number of planeN images at this point. 

You can also adjust now the bit depth (recommended to use 16-bit images) and the system, which **must** be Windows.

Click at the Measure Rois tab, then click at the Find fiji.exe button and locate the ImageJ.exe file (**NOT the fiji.exe**) that is provided in the first release of this repository.

<p align="center">
  <img src="https://github.com/user-attachments/assets/b154d915-9711-4233-a2c0-6dcb52e31935" width="700">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/731184a3-5ea2-48ac-a8ea-ff12b7d14cd7" height="350" width="400">
</p>



Then navigate to the ChangeROIs tab and click the 'Convert Labels to ROIs' button. You will be prompted to select the main ROI folder that contains all subdirectories comprising the mask .tif outputs at this stage. 

<p align="center">
  <img src="https://github.com/user-attachments/assets/e389f919-0fa4-4466-b6c2-ce3e63fc65da" height="350" width="400">
</p>

Let Fiji run completely uninterrupted. It will open and close as many times as your maximum plane number.

At present, there is no messagebox appearing to inform you that the process is complete. Wait a few seconds and a new folder named RoisFromLabels will be created inside your main ROI folder, along with your subdirectories.



## Step 4 (Create Main Folder with Images and Rois)

Create a main folder (e.g. Input) and paste your main Images Folder that contains all planeN subdirectories inside it. Locate the main ROIsFromLabels folder that includes all the newly created subdirectories that now contain .zip files instead of .tif masks. 

You can find the RoisFromLabels folder inside the subdirectories of the main ROIs folder. Paste the RoisFromLabels folder inside your main Input folder. Preferably, rename the RoisFromLabels folder to Rois_folder.



## Step 5 (Set the right Fiji measurements)

In Fiji Menu bar type 'set measurements' and make sure those measurements are selected : 

<p align="center">
  <img src="https://github.com/user-attachments/assets/afe4b992-15e6-4836-b3a6-81cb9ae01a51" height="350">
</p>



## Step 6 (Get Measurements)

In AResCoN, navigate to Main Inputs and press the 'Images Folder' Button. Select your main Image Folder which contains all planeN_images subdirectories. Then press 'Rois Folder' button and select the main ROIs folder which contains all planeN_Rois subdirectories. Both of these main folders must be inside the Input directory. 

<p align="center">
  <img src="https://github.com/user-attachments/assets/7804088f-244f-4d6a-8258-d804a325e98a" height="500" width="500">
</p>

Then, navigate to Measure Rois tab. Click at the 'Save Folder' tab and locate the Input directory (that is, the parent directory of ROIs and Images folder). Create a third folder inside Input called 'save' or whatever else and select it.

Fiji.exe is already selected unless you have closed AReScoN before, in which case you have to select the ImageJ executable file again.

Read the instructions on the screen first and let Fiji run uninterrupted until it obtains all measurements. You will be notified once the procedure is completed. New csv measurements will have been created inside your planeN subdirectories in the save folder.



## Step 7 (Insert data from save directory into AResCoN)

Go to the 'Add Metrics' Tab and click on Add measurements. You can also click on Save measurements after the procedure is finished. In both cases, you will be notified with a messagebox.





