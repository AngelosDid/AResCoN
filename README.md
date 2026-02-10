# A Researcher is Counting Neurons (AResCoN)
AResCoN is a pipeline developed to perform accurate filtering of cells or nuclei following initial inferences. It uses the output of Cellpose or Stardist and utilizes Fiji to obtain measurements that can be used either for X and Y axis cell filtering or Z-axis cell filtering within a small range of planes.

AResCoN is particularly useful in setups where complete imaging of a 2D slice (one hemishpere or both) is required but it can also be used for isolated regions within a 2D slice. 

## 📋 Prerequisites

* A primary output of Cellpose (recommended) or Stardist (only for no z-axis filtering) is required. You can find notebooks for training/predictions on Cellpose github page. A notebook for predictions is also attached here.

* The naming of the obtained ROIs must be similar to the ROIs provided in the repository, namely 001_001, 001_002, 001_003 and so on. Your ROIs will obtain by default these names if you run the label (mask) to ROI conversion option in AResCoN.

* At present, AResCoN only works on Windows. Kindly ignore the Linux option.

* AResCoN works optimally with **16-bit** images and has been tested so far only with 20x magnified captures. 8-bit images and lower or higher magnifications are likely to work too, as long as your dataset is homogenous.
  
* AResCoN has only be tested with .tif (and .tiff) images.
  
* AResCon receives only one channel input at at time. If you have more than one channels, you should run each separately.
  
* For a complete utilization of its features, it requires images from small multi-stacks (usually comprising up to 10 planes). Due to the (1) wiggly nature of a mounted tissue (2) the slightly different depth of cells and nuclei populating it (3) inconsistencies in slice thickness- the acquisition of several planes can secure at least one crisp capture of each cell-nucleus across many planes. AReScON can filter out Cellpose predictions that are detected over separate planes and correspond to the same observation. 

* AResCoN has recently been fixed to accomodate multistack images comprising more than 9 planes. It is now also able to process multistack images comprising a different number of planes (e.g. a multistack of 6 planes and a multistack of 12 planes).
  
* The steps that include openning of Fiji require that you do not press your keyboard or move your mouse. Therefore, it is recommended that you don't run AResCoN in your main desktop.

* Please use the Fiji/ImageJ version provided in this repository. Do not update Fiji. Other versions will probably not work unless you adjust the number of tab presses in the pyautogui in all modules where fiji is called.
  
* An installation of AutoHotKeysUX is necessary (https://www.autohotkey.com/  v2 and not the depracated one)


## Step 0 (Getting ready)

Install Anaconda or Miniconda. Open the Anaconda prompt, locate the directory where the AResCoN_dependencies.yaml file is. Then type:  
```bash
conda env create -f AResCoN_dependencies.yaml
```


## Step 1 (Get independent planes)

Use the 'Stack to Images' ImageJ function and save separately each plane. Images **must end** to _plane1.tif, _plane2.tif and so on. Make sure that each plane includes only a single channel.

Alternatively, if your original images are multistack AND multichannel images, you can navigate the fiji macros folder inside AResCoN code and use the SeparateMultiplaneForBatchMacro.txt. You can copy its content, open Fiji and go to Process->Batch->Macro. Select as input the directory where all your multistack AND multichannel images are. When the first image opens, you will be requested to indicate a folder where each single-channel/single-plane image will be saved. Your directory has to be structured like this: directory/CN/planeN_image where N is the number of your channel (for CN) or plane (for planeN). Therefore, if you have 3 channels and 3 planes, you need to have a C1, C2 and C3 folder; inside of each a plane1_images, plane2_images, plane3_images folder. All CN and planeN directories must be empty (This macro will be incorporated to AResCoN in a new version). 


## Step 2 (Paste images to corresponding planeN folder)

Create a main Rois_Folder and then create as many planeN_Images subdirectories as the maximum plane that you have. For instance, if brain a consists of 4 planes and brain b of 5, then create 5 planeN subdirectories, where N corresponds to a number from 1 to 5. plane1_images must contain a_plane1.tif and b_plane1.tif , plane2_images must contain a_plane2.tif and b_plane2.tif and so on.

<p align="center">
  <img src="https://github.com/user-attachments/assets/0dcfdb38-6ed3-4316-ae5a-735196c7b6da" width="700">
</p>



## Step 3 (Convert masks to ROIs)

⚠️ Warning: Sometimes, hidden desktop.ini files might be included inside your directories. AResCoN is not accounting for these files yet. You can ensure that you directory has no hidden desktop files if you : open file explorer -> click the three dots next to view (Windows 11), -> options -> view -> hide protected operating system files -> delete all desktop.ini files that might be inside every plane folder. 

Alternatively you can : 

```bash
cd "C:\Users\YourAccount\Desktop\ROIs folder"
del /s /a desktop.ini"
```

Next: Run Cellpose inferences and paste each .tif mask output to the respective planeN subdirectory of a main ROIs folder. For instance, if there are 2 multistacks of brain a and brain b, both comprising 5 planes, plane1_ROIs must contain a_plane1.tif and b_plane1.tif, plane2_ROIs must contain a_plane2.tif and b_plane2.tif and so on.

The names of the .tif masks must be **identical** to the names of the initial _planeN.tif images. The provided Cellpose notebook will add an additional _predicted_mask to each mask output name (unless you remove it directly from the notebook). Remove this additional "_predicted_mask" part from all images. You can do this from cmd or much more easily with tools like PowerRename.

If you aren't using planes from small multistacks and are only interested in filtering single shots, place all your .tif output masks inside the plane1_Rois subdirectory of the main ROIs folder.

<p align="center">
  <img src="https://github.com/user-attachments/assets/aa93acc5-e427-456e-981d-6b21afbce24c" width="700">
</p>

After you ensure that the architecture is correct, open the AResCoN code folder with VS code and run the Multiplane_cell_detection17.py. A GUI window will open. 

Click at the Microscopy tab and make sure that the number of zplanes corresponds to your maximum z-plane. 

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

⚠️ Warning: Sometimes, hidden desktop.ini files might be included inside your Images or ROIs folders. This bug was discovered recently and hasn't been fixed yet. It is recommended to navigate to your main Images and ROIs folders from cmd and delete any possible hidden desktop.ini files.

```bash
cd "C:\Users\YourAccount\Desktop\Images OR ROIs folder"
del /s /a desktop.ini"
```



## Step 4 (Create Main Folder with Images and Rois)

Create a main folder (e.g. Input) and paste your main Images Folder that contains all planeN subdirectories inside it. Locate the main ROIsFromLabels folder that includes all the newly created subdirectories that now contain .zip files instead of .tif masks. 

You can find the RoisFromLabels folder inside the subdirectories of the main ROIs folder. Paste the RoisFromLabels folder inside your main Input folder. Preferably, rename the RoisFromLabels folder to Rois_folder.



## Step 5 (Set the right Fiji measurements)

In Fiji Menu bar type 'set measurements' and make sure the Area, Standard deviation, min and max grey value, Limit to threshold and Display Labels are selected (I personally have opted for more but you dont need them and it will cost time) : 

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

Go to the 'Add Metrics' Tab and click on Add measurements. You can also click on Save measurements after the procedure is finished. In both cases, you will be notified with a messagebox. Depending on the size of your files, this might take time. A (Not Responding) message on the title of the program does not indicate that AResCoN is not running properly, rather that it is still running.


## Step 8 (Get the standard deviation ROIs after FindEdges)

Click on 'Find edges StdDev' and let Fiji run, like you did in step 6. You will be notified by a messagebox in the end and a new folder containing the new measurements based on FindEdges will be created inside the Input folder.

## Step 9 (Add FindEdges stdev in main measurements)

Click on Add edges StdDev. This will lead to the addition of a column in each one of your csv files inside the main folder. Then click again on 'Add measurements' to insert the new information to AResCoN. 

Steps 7,8 and 9 in one image :

<p align="center">
  <img src="https://github.com/user-attachments/assets/ec2f6f2e-44cb-41a3-b124-5553b55215b2" height="500" width="500">
</p>



## Step 10 (Get Relative background of each ROI) :

⚠️ Warning : This step might differ from the youtube tutorial. Changes have been made to the way this function works in order to minimize processing time.

Find the 2D filter tab and type a ROI enlargement factor (I like a value of 2). For a value of 2, this factor means that you are taking as a background field the space of a double sized bounding box of each cell of yours. Press the 'Locate .ahk' button and select the autoenter.ahk inside the AResCoN code folder. After installing the AutoHotKeysUX, press the 'Locate' .exe button and select the executable file of AutoHotKeysUX.

<p align="center">
  <img src="https://github.com/user-attachments/assets/268a805b-a9fb-4686-b0fa-0ec25dbd250b" width = 550 height="350">
</p>

Click on 'Get Roi-Background mean gray differences'. You will be asked to select an empty folder where Fiji will communicate with AResCoN during the process. 
* Eventually, images of convex hulls will remain in this folder. You can use them later as sanity checks. Each convex hull is a region created based on the external boundaries of the more distant cells from all directions, yet still inside your slice (and not any contingent misdetected ROIs. in the background of the slice). ROIs are 'burned' into each sanity check image so that you can see whether the convex hull has been created appropriately. Ignore erroneous ROIs that might be outside the convex hull and are derived by erroneous detections of Cellpose but be suspicious if many ROIs are outside the convex hull (which would mean that your slice was not successfuly contrasted to the background of the image).
* If you convex hulls are not created properly, then you will have to tweak the code for threshold-based background detection that takes place inside the RunMeanMeasurements.py module. You can experiment with the different methods that Fiji offers, open macro recorder and see the underlying code so that you replace the default code below (Note that you don't have to reduce your particles to 1. As long as your slice is the largest particle after thresholding, the rest of the script will work fine).
  
  ```bash
   setOption("ScaleConversions", true);
  run("Gaussian Blur...", "sigma=10");
  run("Auto Threshold", "method=MinError(I) white");
  ```

Let Fiji run uninterruptedly like step 6. This step will take longer than step 6 and 8. How much longer? This really depends on the number of ROIs that each image has. It might take a couple of minutes -or more- per plane for images with many thousands of ROIs.

Eventually, two more columns will be added to each csv file inside the subdirectories of the save folder, where your main measurements are stored. The most important new column is the SurroundingMean, which is the relative background of each corresponding ROI. This background **DOES NOT** take into account pixel values of other ROIs falling under this enlarged region. It also does not take into account the real black background behind the tissue, which is adjacent to neurons that lay in the very outrer cortical parts. Hence, this is background is more reliable than other methods.



## Step 11(Filter ROIs in XY axis) 


You can make your own ROI filters by inserting conditions based on the metrics/measurements that are included in your csv files. For instance, you can exclude all ROIs that are less than 30% brighter than their background by typing (Mean>SurroundingMean*1.3). You can include any other condition (always inside parenthesis) that you want, as long as you don't repeat the name of a metric inside the same condition (you can still factorize if you want). If any of the conditions is violated, the ROI will be filtered out.

💡 IMPORTANT : The ROIs that displayed NaN value during the calculation of the relative background have artificially been given the value 0.000001 under the SurroundingMean column. These are mostly false ROIs detected outside the tissue, somewhere in the black background of the image. It is **highly** recommended to also add the (SurroundingMean>0.000001) condition in the filters, to ensure that no such ROIs will be included in your final set.

There is a catch here though: When we converted masks to ROIs (step3) any contingent spatial gap between overlapping ROIs is now lost. This means that if a neurons is **completely** surrounded by other neurons throughout the whole range of its enlarged form (see step 10), then there will be no unmasked pixel values to calculate the SurroundingMean (unless the enlargment factor had created a space that goes beyond the adjacent cells and included at least one free pixel). This will erroneously lead to a 0.000001 value. This is naturally almost impossible, however, Cellpose makes some really false predictions from time to time which occupy a very large space in the image. The indicated by the red arrow cell in the example below will be 'trapped' and might erroneously acquire a NaN -> 0.000001 value. 

Therefore, in future versions a pre-filtering step will be applied so that very large objects are excluded in the first place. The exclusion of large objects directly during inferences is tricky when using cellpose, because it is based on a percentage of the mask's size compared to the size of the image instead of a raw value of pixels. 


<p align="center">
  <img src="https://github.com/user-attachments/assets/c9c07a2b-1ced-4733-bac2-d0df6e50e271" height="350" width="350">
</p>

Click on 'Apply filters' and you will be prompted to select an empty folder where two directories will be saved, namely the accepted and the rejected. The rejected folder comprises as many directories as your filtering conditions, so that you can see which condition was violated by a particular ROI.

Make sure you agree to create a .pkl file. You will later need this for Zfiltering.



## Step 12 (Z-axis filtering)

Navigate to Zfilter tab and press 'Apply filters'. Then select your newly created Accepted_Rois.pkl file. The default values should work well for a precise detection of the crispest version of a neuron (the plane of origin is indicated in the end of the ROI name, e.g. 001_132-4. '-4' indicates that the selected crispest 'version' of the neuron originates from plane4. The vast majority of cells or nuclei should be detected correct. 

So far, I have detected a few negligible cases where some false positives survive the filtering, thereby leading to erroneous 'double' detection of a neuron. You can easily investigate yourself by overlaying the rois in the image. Notwithstanding that there will probably be no reason for tweaking the filtering values, you can refer to the decisiontree.pptx inside the AResCoN code and see which value corresponds to each step of the designed algorithm. I will provide a more descriptive explanation about this in the future.


# Final zip file

The final zip file contains ROIs that originate from all possible planes, maintaining only the crispest version of each neuron, thereby allowing you to capture all neurons that could possibly be visible throughout your whole tissue!

<img width="2253" height="656" alt="final" src="https://github.com/user-attachments/assets/79b63fce-4f52-4d91-924d-e78df82ccb08" />

# Final results on Youtube

https://youtu.be/fQPcCw8j4ls?t=5792

## 
AResCoN has been created solely by Angelos Didachos, a 4th-year PhD Candidate in Neuroscience. I am finishing my PhD in a few months and then actively looking for a job in Australia. Kindly cite my work if you are planning to use AResCoN by citing the github page. If you are interested in detection of animal freezing behaviors, check out my other repository, namely EasyFreezy, which utilizes Deeplabcut output to detect reliable freezing spans.

