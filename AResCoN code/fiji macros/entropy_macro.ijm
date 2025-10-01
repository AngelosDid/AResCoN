// To avoid opening filedialog everytime during Process->Batch->Macro, try to call the paths from here. 
RoisFolder = call("java.lang.System.getProperty", "macro.roisfolder") + "";
SaveFolder = call("java.lang.System.getProperty", "macro.savefolder") + "";
channel_index = call("java.lang.System.getProperty", "macro.channel_index") + "";

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

// Check if the variable is empty or still "null". This means the path has not been defined yet, that is, it's 1st iteration
if (channel_index == "null" || channel_index == "") {
    channel_index = getNumber("Select channel stack from multistack image. If unsure, go to Plugins->New->Macro and run setSlice(a number here) to locate your preference.", 0);
    if (channel_index == "") exit("User canceled.");
    call("java.lang.System.setProperty", "macro.channel_index", channel_index);
}

//setting the batch mode to false helps to open the list from the histogram later on
setBatchMode("false");

// ensures roi manager is empty
roiManager("reset");
title = getTitle();

//SaveFolder has been modified with file separator, so no need for extra slash. Here we make a directory with the image's name
File.makeDirectory(SaveFolder + title);
image_dir_path = SaveFolder + title + "/" ;

// Here we make directory with the number that corresponds to a particular plane for a particular channel
File.makeDirectory(SaveFolder + title + "/Channel&PlaneIndex" + channel_index);
channel_dir_path = SaveFolder + title + "/Channel&PlaneIndex" + channel_index + "/" ;

//To ensure that the image is selected
selectWindow(title);

//Loads the ROIs that have been produced with stardist
roiManager("Open", RoisFolder + title + ".zip");
n_of_ROIs = roiManager("count");
RoiManager.useNamesAsLabels("true");
roiManager("Show All with labels");


for (roindex = 0; roindex < n_of_ROIs; roindex++) {
	roiManager("Select", roindex);
	roiname = getInfo("roi.name");

	// Set histogram title name to make it active every time so results can be get
	index_of_dot_in_file_extension = lastIndexOf(title, ".");
	title_without_file_extension = substring(title, 0, index_of_dot_in_file_extension);
	histo_name_before_rename = "Histogram of " + title_without_file_extension;
	
	histogram_title = "Histogram of " + roiname;
	print("title changed to " + histogram_title);

	// Creates min and max variable that correspond to lowest and highest pixel value. Bins will be created based on that
	//getRawStatistics(nPixels, mean, min, max, std, histogram);
	//getStatistics(nPixels, mean, min, max, std, histogram);
	// Define parameters for histogram.
	binCount = 256;        // Number of bins (e.g., 512, 1024)
	//min = 0;              // Minimum intensity (not recommended to uncomment) 
	//max = 65535;           // Maximum intensity (not recommended to uncomment)
	
	//Selects a particular stack in terms of z scale and channel based on user's input
	//Always reselect main window first, otherwise the setSlice will malfunction
	selectWindow(title);
	setSlice(channel_index);


	// Generate histogram with custom bins and ensure it has opened first
	run("Histogram", "bins=256 use pixel value range");
	while (!isOpen(histo_name_before_rename)) {
    	wait(10);  
	}

	// rename the histogram
	rename(histogram_title);

	while (!isOpen(histogram_title)) {
    	wait(10);
	}

	//opens the list option of the histogram to get counts per bin and ensures it has opened
	selectImage(histogram_title);
	while (getTitle() != histogram_title) {
    	wait(10);  
	}

	Table.showHistogramTable;
	wait(50);
	

	// Calculate total number of counts for the bins > 0
	// Also creates an array with the counts because using setResults() disrupts reselecting the histogram table with bins as active window
	total_counts = 0;
	countarray = newArray();
	binarray = newArray();
	for (c = 0; c < binCount; c++) {
		current_count = parseInt(Table.get("count", c));
		total_counts += current_count;
		countarray[c] = current_count;
		binarray[c] = parseInt(Table.get("bin start", c));
		
}
 

        // Calculate probability of each bin count that is > 0
        // and eventually calculate shannon entropy
	probarray = newArray();
        entropy = 0;
	for (i = 0; i < binCount; i++) {
		bin_prob = countarray[i] / total_counts;
		probarray[i] = bin_prob;
		if (bin_prob > 0) {
        		entropy -= bin_prob * log(bin_prob) / log(2); 
    	}
		
}

	// Use setResult only after all arrays have been created so that no return to a previous csv table is needed. Register the columns and their values
	for (i = 0; i < binCount; i++) {
    	setResult("StartingBin", i , binarray[i]);
    	setResult("Count", i, countarray[i]);
    	setResult("Probability", i, probarray[i]);
}
	setResult("ShannonEntropy", 0, entropy);
	selectWindow("Results");
	saveAs("Results", channel_dir_path + roiname + ".csv");
	selectWindow("Results");
	run("Close");

	selectWindow(histogram_title);
	// Wait until the selected window is really active
	while (getTitle() != histogram_title) {
   	 wait(10);
	}
	run("Close");

	selectWindow(histogram_title);
	while (getTitle() != histogram_title) {
    	wait(10);
	}
	run("Close","force");
;
	}

