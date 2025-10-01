from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox
from os.path import isfile, isdir, join, exists
from os import listdir
from pathlib import Path
import pandas as pd
import re
import os
import shutil
import psutil


def ShowError(message,boxtitle):
    """Displays error messages"""
    box = QMessageBox()
    box.setIcon(QMessageBox.Critical)
    box.setText(boxtitle)
    box.setWindowTitle(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()

def ShowInfoMessage(message,boxtitle):
    """Displays information messages"""
    box = QMessageBox()
    box.setIcon(QMessageBox.Information)
    box.setText(boxtitle)
    box.setWindowTitle(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()

def AskConfirmation(asktitle,askmessage):
    reply = QMessageBox.question(None,asktitle, askmessage, 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes :
        return True
    else :
        return False
    
def VerifySameplaneNstart(couples_of_foldimages_with_foldroi_paths,strng_ptrn):
    """Checks if the subdirectories (planeN folders) of images and rois have the same planeN start and the same order.
       Input couples_of_foldimages_with_foldroi_paths : zip of two lists, one containing strings with all subdir paths for all planeN image folders
       and one containing strings with all subdir paths for all planeN roi folders
       Input strng_ptrn : a  r-string pattern for recognition of planeN patter
       Output : str indicating a mismatch in case two folders (one image subdir and one roi subdir) do not have the same planeN start"""
    
    for couple in couples_of_foldimages_with_foldroi_paths :
        if re.findall(strng_ptrn, couple[0]) == re.findall(strng_ptrn, couple[1]) :
            pass
        else :
            ShowError('Folders not matching','Could not identify a couple of planeN subdirectories between main images folder and main rois folder.')      # looks for a planeN match in the names 
            return 'Unmatched'
    
def VerifyEmptySaveFolder (savepath):
    """ Verifies that there are no subdirectories in the measurements save folder
        Input savepath : this is the self.user_selections["Measurements_Folder"] from the main code, which is the main path where more save subdirs will be 
        created for the measurements
        Output : string NotEmpty in case a subdir is found"""
    if len(os.listdir(savepath))>0 :
        ShowError('Save Folders Already Created','It seems that you have selected the same save folder previously. Please remove the planeN subdirectories from the save folder. Then, for every planeN image subdirectory that you have, a new save subdirectory will be created')     
        return 'NotEmpty'
    
def VerifyEmptyMaskFolder (emptymaskFolder):
    """ Verifies that there are no files inside the selected mask folder
        Input savepath : this is the self.user_selections["EmptyMaskDirectory"] from the InitializeMeanBackground() of the main code.
        Output : string NotEmpty in case a file"""
    if len(os.listdir(emptymaskFolder))>0 :
        ShowError('Mask folder not empty','It seems that you have selected the same save folder previously. Please try selecting an empty one.')     
        return 'NotEmpty'

def OnlyOnePlaneSelected (user_planes_n):
    """The first gui tab has asks the user to define how many planeN subdirectories they have. This is 1 be default but the user may want to change it."""
    if user_planes_n == 1 :
        plane_decision = AskConfirmation('1 plane selected', 'You have set your number of planes to 1 in the microscopy tab. This will affect this step. Do you wish to continue?')
        if plane_decision == False :
            return 'One_plane_only_by_accident'
        
def NotSelectedSaveFolder(selections_dic): 
    """Checks whether a save folder has already been selected, so that the user can proceed to adding measurements
       Input selections_dic : dictionary corresponding to self.user_selections. If a save folder exists, then Measurements_Folder should exist as key.
       Output               : str  indicating that there is no defined folder"""
    try :
        selections_dic["Measurements_Folder"]
    except KeyError:
        save_message = ("It appears that you have not selected a main save folder. "
                        "This can happen if you start running AResCoN directly from a later stage tab. "
                        "Please go to Measure Rois tab and select the folder that contains all subfolders with planeN measurements")
        ShowError('Undefined main Save folder',save_message)   
        return 'save_folder_not_defined'  

def NotSelectedRoiFolder(selection_dic):
     """Checks whether a main roi save folder has already been selected, so that the user can proceed to adding measurements
       Input selections_dic : dictionary corresponding to self.user_selections. If a save roi folder exists, then Rois_Folder should exist as key.
       Output               : str  indicating that there is no defined roi save folder"""
     try:
        selection_dic["Rois_Folder"]
     except KeyError:
        save_message = ("It appears that you have not selected main roi folder."
                        "This can happen if you start running AResCoN directly from a later stage tab. "
                        "Please go to Main Inputs tab and select the folder that contains all subfolders with planeN rois")
        ShowError('Undefined main roi folder',save_message)   
        return 'roi_save_folder_not_defined'  
     
def NotSelectedImagesFolder(selection_dic):
     """Checks whether a main image folder has already been selected, so that the user can proceed to adding/getting measurements
       Input selections_dic : dictionary corresponding to self.user_selections. If a main image folder exists, then Images_Folder should exist as key.
       Output               : str  indicating that there is no defined main image folder"""
     try:
        selection_dic["Images_Folder"]
     except KeyError:
        save_message = ("It appears that you have not selected main image folder."
                        "This can happen if you start running AResCoN directly from a later stage tab."
                        " Please go to Main Inputs tab and select the folder that contains all subfolders with planeN images")
        ShowError('Undefined main image folder',save_message)   
        return 'image_folder_not_defined'
     
def NotSelectedFijiFile(selection_dic):
     """Checks whether a a fiji/imagej.exe file has already been selected, so that the user can proceed to getting measurements
       Input selections_dic : dictionary corresponding to self.user_selections. If fiji.exe has been selected, then FijiexePath should exist as key.
       Output               : str  indicating that there is no defined path for fiji exe"""
     try:
        selection_dic["FijiexePath"]
     except KeyError:
        save_message = ("You have not defined the path for your fiji.exe file yet."
                        " Please go to Measure Rois tab and select your fiji.exe file")
        ShowError('Undefined fiji.exe path',save_message)   
        return 'image.exe_not_defined'
     
def NotSelectedExamplePercentage(prcntg):
    try :
        prcntg = int(prcntg.strip('%'))                                                                                # remove the % in case user has inserted
    except ValueError :
        ShowError ('Wrong input','You have typed something wrong. Only integer values are allowed. Please try again.')
        return 'percentage_not_defined'
    else :
        return prcntg

def NotSelectedReducePercentages (string_list_with_percentages):
    try : 
        perc_list = string_list_with_percentages.split(',')                                                                              # in case user has inserted more than one value, split them. This turns a string like '10,20' to ['10','20']
        transformed_list = [int(percentage_val.strip('%').strip(' ')) for percentage_val in perc_list]                                   # remove the % in case user has inserted and convert '10' to 10 and '20' to 20
        if transformed_list == []:
            ShowError ('Wrong input',"You haven't typed any percentage values. Please type the values and separate them by comma.")
            return 'wrong_user_input'
    except : 
        ShowError ('Wrong input','You have typed something wrong. Only integer values are allowed, separated by comma. Please try again.')
        return 'wrong_user_input'
    else :
        return transformed_list


def MetricsNotAdded(needed_for_find_edges=False):
    if needed_for_find_edges == False :
        save_message = ("It appears that you have not added any Measurements Yet. "
                        "After you Get Measurements, make sure you Add Measurements before you create a save file. "
                        " You can then load this save file every time you open AResCon")
        ShowError('Measurements not added yet',save_message)
    else :
        save_message = ("It appears that you have not added any Measurements Yet. "
                        "You can only add the find edges results to already added measurements. "
                        "Make sure that you add measurements first or load an existing save file. "
                        "You can then add the additional measurements of find edges ")
        ShowError('Measurements not added yet',save_message)

def FindEdgesFolderExists(parentdir):
    if 'FindEdgesResults' in os.listdir(parentdir):                                                                                                  # No FindEdgesResults directory should exist at this stage.
        message = ('A FindEdgesResults folder already exists. Please navigate to the parent directory'
                    ' of your main measurements save folder and remove it')
        ShowError ('Remove FindEdgesResults first', message)
        return 'Exists_Already'

def FindEdgesFolderDoesNotExist(parentdir):
    if 'FindEdgesResults' not in os.listdir(parentdir):                                                                                                 # No FindEdgesResults directory should exist at this stage.
        message = (f' Could not find FindEdgesResults in {parentdir}. You need to click on find edges StdDev and create the csv files first ')
        ShowError ('Find Edges StdDev first', message)
        return 'Does_not_exist'  

def EntropyFolderDoesNotExist(parentdir):
    if 'EntropyResults' not in os.listdir(parentdir):                                                                                                 # No EntropyResults directory should exist at this stage.
        message = (f' Could not find EntropyResults in {parentdir}. You need to click on Get Entropy and create the csv files first ')
        ShowError ('Get Entropy first', message)
        return 'Does_not_exist' 
          
    
def FindEdgesPythonVariableExists (selections_of_user):
    try :
        selections_of_user['FindEdges_Folder']
    except KeyError :
        return 'missing_user_selection_variable'
    
def MeanBackgroundFolderExists(parentdir):
    if 'MeanBackgroundResults' in os.listdir(parentdir):                                                                                                  # No MeanBackgroundResults directory should exist at this stage.
        message = ('A MeanBackgroundResults folder already exists. Please navigate to the parent directory'
                    ' of your main measurements save folder and remove it')
        ShowError ('Remove MeanBackgroundResults first', message)
        return 'Exists_Already'
    

    
def EntropyPythonVariableExists (selections_of_user):
    try :
        selections_of_user['Entropy_Folder']
    except KeyError :
        return 'missing_user_selection_variable'
    

def VerifySameNamesInsideSubdir (zip_subdirs, add_csv=False):
    """Verifies that all names inside two subdirectories are name. This is useful for adding new measurements to the existing csv ones. 
       For instance, find edges StdDevn can be added to the main csv measurements. But the filenames must match.
       Input zip_subdirs : zip format that contains coupled str paths of subdirectories. All paths to all subdirectories should be included here.
       Input remove_csv  : By default False, if true, then the .csv end will be virtually added to the filenames of the subdirectory to achieve a perfect match. 
       For consistency, the new measurement path should be first element in each couple and the main measurement path the second"""
    
    for extra_metric_subdir_path, metric_subdir_path in zip_subdirs :
        if add_csv == False:
            all_csv_names_extra = sorted ([file for file in listdir(extra_metric_subdir_path) if isfile (join(extra_metric_subdir_path, file))])
        else : 
            all_csv_names_extra = sorted ([file+'.csv' for file in listdir(extra_metric_subdir_path) if isdir (join(extra_metric_subdir_path, file))])    # Mind that in the scenario we have to add the .csv to the name, the file is a directory, not a csv file. Hence the isdir
        
        all_csv_names_main  = sorted ([file for file in listdir(metric_subdir_path) if isfile (join(metric_subdir_path, file))])
        if all_csv_names_extra != all_csv_names_main :
            ShowError("Could not match all names", "A mismatch between your main measurement filenames and new metric filenames stopped the procedure")
            return "names_dont_match"
   

def CreateCopies (new_metric_main_path, main_save_folder):
    """Creates a copy of the main folder of a new metric as well as of the main measurements (if not created already).
       This can help the user retrieve the file in case a mistake is made"""
    copies_made = 1                                                                                                                  # Normally, there should be no backup of the new metric since this function is called when the user wants to add this metric
    shutil.make_archive(new_metric_main_path+'_backup', 'zip', new_metric_main_path)
    if not exists(main_save_folder+'_backup.zip'):                                                                                   # However, user might have previousle added a metric to the main csv measurements, hence there might be a backup for main measurements
        shutil.make_archive(main_save_folder+'_backup', 'zip', main_save_folder)
        copies_made += 1
    if copies_made == 2 :
        message = f'Two backups were created: \n 1) {new_metric_main_path+"_backup.zip"} and \n 2){main_save_folder+"_backup.zip"}'
        ShowInfoMessage('Copies made successfully', message)
    if copies_made == 1 :                                                                                                             # =1 means that there was no backup of the main save roi measurements
        message = (f'A former backup of the main roi measurement folder {main_save_folder+"_backup.zip"} already exists. '
        f'Hence, a new backup is created solely for your single metric below \n {new_metric_main_path+"_backup.zip" }'
        '\n'
        f'If you also want a new backup of the main roi measurement folder click Yes. Yes will overwrite the current '
        f'{main_save_folder+"_backup.zip"} . To continue only with single metric backup click No .')
        if AskConfirmation('Backup exists', message) == True : shutil.make_archive(main_save_folder+'_backup', 'zip', main_save_folder) 


def EntropyFolderExists(parentdir):
    if 'EntropyResults' in os.listdir(parentdir):                                                                                     # No Entropy Results directory should exist at this stage.
        message = ('An EntropyResults folder already exists. Please navigate to the parent directory'
                    ' of your main measurements save folder and remove it')
        ShowError ('Remove EntropyResults first', message)
        return 'Exists_Already'
    
def CheckBitDepth (depth):
    if depth == '8bit': pass 
    else :
        message = ('It is recommended to measure entropy after an 8bit convertion first. Do you agree? '
                   'This will not affect you original files. ')
        decision = AskConfirmation('Unsuitable bit depth', message)
        if decision == True :
            return '8bit'
        else : 
            return '16bit'
        
def ReduceRoiPercentagesExist (new_reduced_roi_foldernames):
    """Ensures that there are no name conflicts between the newly created subdirectories with reduced size rois
       and potentially older ones created by the user at a previous stage.
       new_reduced_roi_foldernames : list with str indicating paths to subdirectories of the ReducedRois. These are to be created subdirs
                                     not yet existent."""
    for foldername in new_reduced_roi_foldernames :
        if os.path.exists(foldername+'%_reduction') :
            message = (f'There is already a {foldername+'%_reduction'} folder in your ReducedRois directory. '
                       'Please remove it first and try again. No changes were made anywhere while executing this command. '
                       'Lucky you, careless researcher !')
            ShowError('Folder name conflict', message)
            return 'name_conflict_detected'
        
def ShowMismatchError(error_number):
    message = (f"{error_number} mismatches were detected. Your roinames must be like 001_001, 001_002 and so on..." 
            "And roimeasurement labels must be like image.tif:001_001, image.tif:001_002 and so on..."
            "ImageJ adds the image.tif: part before he 001_001 and so on. The mismatches won't be included in the data")
    box2 = QMessageBox()
    box2.setIcon(QMessageBox.Critical)
    box2.setText(message)
    box2.setWindowTitle('Roiname and measurement mismatch')
    box2.setStandardButtons(QMessageBox.Ok)
    box2.exec_()

def MeanBackgroundInputsExist(enlargement_factor):
    """Checks whether all 3 inputs have been filled properly for the filtering based on surrounding mean gray value
       Inputs : all 3 inputs are strings with numerical values (no decimals) """
    
    if "." in enlargement_factor :
        message = "You have typed a float number. Only decimal numbers are allowed. Please try again"
        ShowError('Decimals not allowed', message)
        return 'Not_exists_or_wrong'

    if  "" in [enlargement_factor] :
        empty_message = "You have not filled all entry fields. Please try again"
        ShowError('Empty input detected', empty_message)
        return 'Not_exists_or_wrong'
    
    if enlargement_factor.isnumeric() : pass
    else : 
        non_numessage = ("You have inserted a non-numeric character in one of your inputs. Please try again")
        ShowError("Non-numeric value", non_numessage)
        return 'Not_exists_or_wrong'
    
def AutoHotKeyInputsMeanMeasurementsExist(mean_msrmnts_slctions):
    """Checks whether the user has selected both the .ahk and autohotkey.exe file.
       This is important because runmeanmeasurements fiji macro yields an error that needs to be skipped by simulating keystroke"""
    if  len (mean_msrmnts_slctions.keys()) == 2 :
        pass
    else :
        non_numessage = ("You have not selected .ahk or .exe file for AutoHotKey. Please try again")
        ShowError("Files missing", non_numessage)
        return "incomplete_inputs"


def UserWantsToVisualizeEnlargedRois ():
    message = ("Would you like to get visuals of surrounding background during the analysis? "
                "This will slow down the procedure from miliseconds to several seconds for every image. "
                "It will allow you though to see the surrounding background of each ROI as well as the "
                "excluded parts of the image.")
    return AskConfirmation("Visualize enlarged ROIs", message)

def ColumnOfRoiMeasurementsExists (dataframe,column_name_to_check):
    """Checks if a dataframe has a column with a particular name
    Input dataframe            : a dataframe created from a csv file that contains roi measurements of an image
    Input column_name_to_check : a str indicating the column that must be found
    """

    if column_name_to_check not in dataframe.columns : 
        message = (f"Could not find a column named precisely {column_name_to_check} in a csv file. "
                   "This column is needed for a mathematical operation that you have initiated. "
                   "You will have to erase the folder with the newly created metric first."
                   "Your main roi measurement csv files have remained intact. ")
        ShowError ("Column not found", message )
        return 'column_not_found_in_csv'
    

def is_fiji_still_open(process_name):
    """Checks whether fiji is still runinng
        Input process_name : str corresponding to the name of the fiji process we test
        Output : True or False, depending on whether fiji is open or not, respectively"""
    
    for proc in psutil.process_iter(attrs=['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                print('still runing')
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def MetricNotInData(filters_text,basedic):
    """Checks all user inputs for potential mistakes in metric names. If not, it returns the conditions inside
       the parentheses.
       Input filters_text  : the whole text of user input for filtering using min and max values
       Input basedir       : the main_directory of the main code that includes attributes for measurements.
       Output              : list with conditions in parenthesis like ['(300>Area>30)','(StdDev>30 and Min<50)']"""
    if filters_text.strip(" ")== "" :
        ShowError('No input', "You haven't applied any filters")
        return

    # Detect the (anything inside parenthesis) format to capture all statements
    conditions = re.findall(r'\((.*?)\)', filters_text)
 
    first_planename          = list(basedic.keys())[0]                                                                                        # for instance, 1
    first_imagename          = list(basedic[first_planename][0].keys())[0]                                                                    #first_planename[0] instead of first_plane name because the architecture has always a zero index -> main_dictionary[1][0]['plane1.tif']['001_002-1']  Mind that plane.tif is just the name of an image, not of a plane
    first_roiname            = list(basedic[first_planename][0][first_imagename].keys())[0]
    all_roi_objct_attr_names = dir(basedic[first_planename][0][first_imagename][first_roiname])
    user_attribs             = []                                                                                                             # attributes that dont have __sth__ are coming from the user
    
    for attrib in all_roi_objct_attr_names : 
        if "__" not in attrib : user_attribs.append(attrib)                                                                                   # for instance, __repr__ will be ignored
    
    words_to_validate =[] 
    single_whitespace_conditions = []
    for condition in conditions :                                                                                                             # filtered words of users input will be temporarily kept here to validate they exist as measurements in the main dictionary
        condition = re.sub(' +', ' ', condition)                                                                                              # if there are many whitespaces, make it a signle
        single_whitespace_conditions.append("("+condition+")")                                                                                # this is not for the particular loop but for the Askconfirmation message and the returned conditions.
        splitter = r'(and|[<>=+\-*])'                                                                                                           # splits if it finds the word 'and'  or the character < > =. This means that there should be no 'and' in any of the metric names
        splitlist = re.split(splitter,condition)                                                                                              # we split because we want to focus on the measurement names only here
        for element in splitlist :
            try : 
                float(element)                                                                                                                # if the element can be converted to a number, then it is just a number. Dont append
            except : 
                if element not in ["and"," and"," and", "<",">","=","+","-","*"]:                                                             # if the element is not any of the list characters, then it should be a measurement. Append
                    words_to_validate.append(element.strip(" "))                                                                              # get rid of whitespaces. This means that no metric should have white spaces
    words_to_validate = set(words_to_validate)

    notfound =""                                                                                                                              # if notfound remains "", it means all user inputs are validated
    for wtv in words_to_validate:
        if wtv not in user_attribs:                                                                                                           # if one of the words the user has written is not an attribute name
            notfound = notfound + " " + wtv 
    
    if notfound != "":
        message = (f"The following measurements could not be traced inside the metrics you added in Arescon: {notfound} \n"
                   "This could happen if:\n\n"
                   "1)You haven't passed this metric(s) to your main roi measurement csv files\n\n"
                   "2)You have added measurements from a previous saved_metrics.pkl file that didn't include all the metrics that you typed. " 
                   "You can fix this by adding measurements again .\n\n"
                   "3)You have just typed a metric name wrong. Click open metrics to open a csv file and see your measurement names.\n\n"
                   "4)You have typed a condition wrong. For instance : (SurroundingMean>0.1.000001) instead of (SurroundingMean>0.000001)")
        ShowError ('Incorrect input', message)
    
    else :
        # This check might have been obsolete but nevertheless good to keep
        for condition in single_whitespace_conditions : 
            if condition[0] != '(' or condition[-1] != ')':
                parenthmsg = f'The condition {condition} is not properly enclosed with parenthesis. Please try again.'
                ShowError ('Parenthesis matters',parenthmsg) 
                return 

        condmsg = '\n'.join(condition+" OR " for condition in single_whitespace_conditions)                                                    # create a string message with \n to seperate conditions and insert OR between them
        elsemsg =  (f"All metric names have been validated. The conditions that will be applied for ROI exclusion are:\n\n"
                    f"{condmsg[:-4]} \n\n"                                                                                                     # This is to remove the last OR from the last condition when printed
                    "Please read the conditions in this window carefully before you apply your filter. Make sure that all "
                    "conditions that you typed are present here. Missing conditions can be due to wrong parenthesis enclosure and "
                    "will affect your results unpredictably (we don't want that). \n\n"
                    "Press Yes to continue or No if you have spotted any syntax mistakes. ")
        if AskConfirmation("Verify Input", elsemsg) == False : return                                                                         # if the user presses no, then do nothing and return.                                                                      
        else : return single_whitespace_conditions


def EmptyPathSelections ():
    """Checks if the path that the user selected is an empty subfolder"""
    savemsg = (f"You will be now prompted to select an empty subfolder to save the accepted and rejected ROIs.")
    ShowInfoMessage("Filters Folder", savemsg)
    filtersave = QFileDialog.getExistingDirectory(None, savemsg)
    print(filtersave)
    if filtersave=='': 
        ShowError("No input", "You haven't selected any folder")
        return 
    elif listdir(filtersave) != []:
        ShowError ("Folder not empty", "Please select an empty folder!")
        EmptyPathSelections()
    else :
        return filtersave
    

def PrepareUserforMaskFolderSelection():
    message= "You will now be prompted to select an empty directory where the masks of image planes will be saved for contingent sanity checks"
    ShowInfoMessage('Selection of folder required', message)
    
    
def WarnIfFindEdgesIsMissing (self_from_main):
    """Checks whether there is a FindEdgesStdDev column in the first csv file of all save measurements.
        This would be indicative of its existence accross all csv files. The user can decide if (s)he wants to continue or not"""
    first_plane_path = list(Path(self_from_main.user_selections["Measurements_Folder"]).iterdir())[0]                                                         # gets the list with plane n subdirectories paths, selects the first,
    single_csvpath   = list(Path(first_plane_path).iterdir())[0]                                                                                              # then gets the list with the paths of the first planeN subdirectory and selects first image roi measurements csv path
    first_file_df    = pd.read_csv(single_csvpath)  
    if 'FindEdgesStdDev' not in first_file_df.columns :
        erro_message = 'FindEdgesStdDev is not added to your main measurements folder. You will not be able to proceed to Z-filtering.' \
        'Do you want to continue ? '
        title_error = "FindEdgesStdDev missing"
        user_decision = AskConfirmation(title_error,erro_message)
        if user_decision == False:
            return 'FindEdgesStdDev_not_in_the_main_save_folder_User_Decided_to_stop'
        else : return True
    


    pass
    