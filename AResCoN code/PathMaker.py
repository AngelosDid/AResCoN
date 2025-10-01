import os 
import Checks
from os.path import join, normpath, exists
from os import listdir
from datetime import datetime
import pathlib

def CreateMeasurementSubdirs (planes_number, savepath):
    """Creates a subdir planeN folder (where measurements will be saved in the future) for every planeN image folder using os.mkdir
       Input planes_number : int corresponding to the number of planes, that is, subdirectories
       Input savepath : this is the self.user_selections["Measurements_Folder"] from the main code, which is the main path where more save subdirs will be 
                     created for the measurements
       Output: Besides the os.mkdir, a list with all paths (str format) of all save sudirs is returned  """
    all_of_save_paths = []
    for n in range(1,planes_number+1): 
        new_save_subdir = f'plane{n}_Measurements'
        plane_path      = os.path.join(savepath,new_save_subdir)
        os.mkdir(plane_path)
        all_of_save_paths.append(plane_path)
    return all_of_save_paths


def CreateFindEdgesSubdirs (planes_number, savepath):
    """Creates a subdir planeN folder (where find edges measurements will be saved in the future) for every planeN image folder using os.mkdir
       Input planes_number : int corresponding to the number of planes, that is, subdirectories
       Input savepath : this is the parent directory of the self.user_selections["Measurements_Folder"] from the main code.
       Output: Besides the os.mkdir, a list with all paths (str format) of all save sudirs is returned  """
    all_of_save_paths = []
    for n in range(1,planes_number+1): 
        new_save_subdir = f'plane{n}_FindEdges'
        plane_path      = os.path.join(savepath,new_save_subdir)
        os.mkdir(plane_path)
        all_of_save_paths.append(plane_path)
    return all_of_save_paths


def CreateEntropySubdirs (planes_number, savepath):
    """Creates a subdir planeN folder (where entropy measurements will be saved in the future) for every planeN image folder using os.mkdir
       Input planes_number : int corresponding to the number of planes, that is, subdirectories
       Input savepath : this is the parent directory of the self.user_selections["Measurements_Folder"] from the main code.
       Output: Besides the os.mkdir, a list with all paths (str format) of all save sudirs is returned  """
    all_of_save_paths = []
    for n in range(1,planes_number+1): 
        new_save_subdir = f'plane{n}_Entropy'
        plane_path      = os.path.join(savepath,new_save_subdir)
        os.mkdir(plane_path)
        all_of_save_paths.append(plane_path)
    return all_of_save_paths

def CreateReducedRoisMainDir(parent_dir_of_main_roi_measurements_dir):
    """ Creates the main directory where the subdirectories of each selected reducedroi percentage will be generated.
        parent_dir_of_main_roi_measurements_dir : str indicating the path to the parent directory of the initial roi measurements """

    if "ReducedRois" not in os.listdir (parent_dir_of_main_roi_measurements_dir):
        os.mkdir (os.path.join(parent_dir_of_main_roi_measurements_dir,"ReducedRois"))
        message = (f"A ReducedRois folder for all your ReducedRoi subdirectories was created " 
                   f"in your parent directory {join(parent_dir_of_main_roi_measurements_dir,'ReducedRois')}")
        Checks.ShowInfoMessage ("ReducedRois folder created", message)
    else :
        elsemessage = (f"There is already a ReducedRois folder in {parent_dir_of_main_roi_measurements_dir} ."
                       "That's not problematic per se. You probably want to make reduced rois with different percentages now. " 
                       "Just make sure you are not mixing rois from previous datasets :) ")
        Checks.ShowInfoMessage ("ReducedRois folder already exists", elsemessage)
    
    return normpath(join(parent_dir_of_main_roi_measurements_dir,"ReducedRois"))                                                               # in both cases, return the path
        
def CreateReducedRoisSubirs (new_rr_paths):
    """Creates one or more subdirectories where the reduced in size rois will be saved. These directories are saved 
       inside the ReducedRois directory, which in turn was previously saved in the parent dir of the main roi measurements
       new_rr_paths : list with strings comprising the new paths to be created
       Output : a list with strings, each one indicating a new created path for a subdirectory """
    
    all_rr_paths = []
    for new_reducedroi_path in new_rr_paths:
        os.mkdir (new_reducedroi_path+'%_reduction')
        all_rr_paths.append(normpath(new_reducedroi_path+'%_reduction'))
    
    Checks.ShowInfoMessage('Folders succesfully created', "New subdirectories were created inside the ReducedRois folder")

    return all_rr_paths

def CreateReducedRoiPlaneSubdirs (planes_number_rr, savepath_rr):
    """Creates a subdir planeN folder (where reduced rois will later be saved) for every planeN image folder using os.mkdir
       Input planes_number : int corresponding to the number of planes, that is, subdirectories
       Input savepath : this is the ReducedRois directory that contains all N%_reduction subdirs.
       Output : dictionary with percentage folder path as key and a sorted list with strings indicating each new created planeN folder path as value                                                                                            """
    
    perc_and_planes:dict = {}                                                 # dictionary with percentage folder path as key and sorted list with strings indicating each new created planeN folder path as value
    all_percentage_paths = sorted(os.listdir(savepath_rr))

    for percentage_folder in all_percentage_paths :
        plane_paths_for_this_folder:list = []
        for n in range(1,planes_number_rr+1): 
            new_save_subdir_rr = f'plane{n}_ReducedRois'
            plane_path      = normpath(join(savepath_rr,percentage_folder,new_save_subdir_rr))
            os.mkdir(plane_path)
            plane_paths_for_this_folder.append(plane_path)
        percentage_folder_whole_path = join(savepath_rr,percentage_folder)
        perc_and_planes [percentage_folder_whole_path] = plane_paths_for_this_folder
    return perc_and_planes

def CreatePlaneNSubirdsForLabels (initial_paths):
    """Creates planeN subdirectories inside the RoisFromLabels directory where converted rois from labels will be saved """

    for path in initial_paths:
        parent= os.path.dirname (path)
        planeName = os.path.basename(path)
        new_path = join(parent,"RoisFromLabels",planeName)
        os.mkdir(new_path)



def CreateMeanBackgroundSubdirs (planes_number_mg, savepath_mg):
    """Creates a subdir planeN folder (where mean background measurements will be saved in the future) for every planeN image folder using os.mkdir
       Input planes_number : int corresponding to the number of planes, that is, subdirectories
       Input savepath : this is the parent directory of the self.user_selections["Measurements_Folder"] from the main code.
       Output: Besides the os.mkdir, a list with all paths (str format) of all save sudirs is returned  """
    all_of_save_paths_mg = []
    for n in range(1,planes_number_mg+1): 
        new_save_subdir_mg = f'plane{n}_MeanBackground'
        plane_path_mg      = os.path.join(savepath_mg,new_save_subdir_mg)
        os.mkdir(plane_path_mg)
        all_of_save_paths_mg.append(plane_path_mg)
    return all_of_save_paths_mg

def Create2DFilterDirAndSubdirs (conditions,filter_path,basdir):
    """Creates a FilteredRoisXY + timestamp directory based on user selection.
       Then creates an Accepted and Rejected directory inside the timestamp folder
       Then creates planeN subdirectories for each planeN that exists in the main_dictionary
       Then creates a subdirectory for each filter condition the user has used, inside every planeN.
       Input conditions  : List with strings comprising filtering conditions like '300>Area>30 and Mean>20'
       Input filter_path : str indicating the path to the main filter folder (folder must be empty)
       Input basdir      : dictionary, corresponding to the main_dictionary in main code 
       Output            : str indicating the path where the template subdirectories for filtering are made"""

    symbol_converter = str.maketrans ({
        '<': '_less_than_',
        '>': '_more_than_',
        '=': '_equals_',
        '*': '_times_'
    })
    converted_conditions = []
    for cndtn in conditions :
        converted_conditions.append(cndtn.translate(symbol_converter))                 # append a converted version to avoid windows error while creating file

    
    plane_range = len(basdir.keys())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = join(filter_path,f"FilteredRoisXY_{timestamp}")
    os.mkdir(base_path)                                                                # will keep that as base for next path generations
    os.mkdir(join(base_path,'Accepted'))
    os.mkdir(join(base_path,'Rejected'))

    # good to remind the user that the condition names can be confusing for the rejected rois
    # for instance, openning a folder called (Max_more_than_1000) means that the rejected rois
    # did NOT have a max more than 1000
    accept_reject_names = listdir(base_path)
    for index in range(len(accept_reject_names)):
        accept_or_reject_name = accept_reject_names[index]
        accept_or_reject_path = join(base_path,accept_or_reject_name)
        for planeN in range(1,plane_range+1):
            foldername = f"plane{planeN}_Rois"
            planeN_subdir = join(accept_or_reject_path,foldername)
            os.mkdir(planeN_subdir)
            for condition in converted_conditions:
                if accept_or_reject_name == 'Rejected':                                # There is no reason to create condition folders for the accepted ones
                    cond_path = join(planeN_subdir,condition)
                    os.mkdir(cond_path)
                    for imagename in basdir[planeN][0].keys() :                        # Finally, create a subdirectory for every image (in this stage we dont know of course whether all of them will be filled with something. This depends on the filtering)
                        image_path = join(cond_path,imagename)
                        if not exists(image_path):
                            os.mkdir (image_path)                                          
                elif accept_or_reject_name== 'Accepted' :                              # In this scenario, we can save directly inside the planeN_subdir
                    for imagename in basdir[planeN][0].keys() :                        
                        image_path = join(planeN_subdir,imagename)                     # Mind that here, we join a previous path, because we never created the cond_path for the accepted ones
                        if not exists(image_path):
                            os.mkdir (image_path) 
    return base_path

def CreateZfilteredMainFolder(acceptedROIs_path):
    """Creates the main folder where all final zfiltered zip files with rois from all planes will be saved for each brainID.
       Input acceptedROIs_path : dict from the accepted_ROIs.pkl file after XY filtering. The main z folder will be created inside
       its parent directory.
       
       Output : the z_folder_path as long as it didnt exist before, or, it existed but it was empty"""
    
    parent = os.path.dirname(acceptedROIs_path)
    z_folder_path = join(parent,"ZfilteredROIs")
    if not exists (z_folder_path) :                    # The folder will be created if it doesnt exist 
        os.mkdir(z_folder_path)
        return z_folder_path
    elif len(os.listdir(z_folder_path)) == 0:          # if it exists but has no files inside, then we just return
        return z_folder_path
    else :                                             # if it exists and has files, then show error message
        msg = f"A ZfilteredROIs path already exists inside {parent}. Delete or move it first before generating new filtered results"
        Checks.ShowError("Directory already exists",msg)
        return 'z folder already exists and not empty'


    


