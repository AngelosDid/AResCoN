//press d to show all, a to show none and s to remove selection

macro "Macro 1 [d]" {
        roiManager("show all with labels");
    }

macro "Macro 2 [a]" {
        roiManager("show none");
    }

macro "Macro 2 [s]" {
	if (RoiManager.selected == 1) {
        roiManager("delete");
    }
    }

