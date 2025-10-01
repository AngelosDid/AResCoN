
# Used to add further measurements to the main_dictionary of the main code such as FindEdges StdDev

import pandas as pd
import Checks
import re
import operator
from os import listdir
from os.path import isfile,join,isdir,normpath,basename,splitext,dirname,exists
from collections import defaultdict

def PassMeasurementsToMainCsv(new_and_main_paths,metric='StdDev',metric_prefix='FindEdges',extra_calc_col=False,extra_col_name=False) :
    """Takes a metric from newly generated results file (like the StdDev of FindEdges) and passes it to the main result files
       of each respective file. If extra_calc_col argument is passed, one more column is created in the main result files which
       is the result of a mathematical operation betweem the metric from newly generated results file and pre-existing columns.
       Important note : any NaN values will be converted to 0.000001 to maintain filtering based on numeric values only in another function and 
       prevent division errors at the same time in case a value is used inside a condition as denominator.
       
       Input new_and_main_paths : zip format that contains coupled str paths of subdirectories. All paths to all subdirectories 
       should be included here. A second zip is done later, to match paths of particular files and not just directories.
       For consistency, the new measurement path should be first element in each couple and the main measurement path the second.
       Input metric        : str indicating the measurement that will be written to the corresponding main csv file.
       Input metric_prfix  : str that provides further characterization of the measurement. Used for FindEdges and Mean Background.
                             For instance, if metric_prefix='FindEdges' and metric = 'StdDev', column gets the name 'FindEdgesStdDev'.
       Input extra_calc_col: False by default. If str, one combinatory column based on main roi measurements and metric will be created.
                             If string, it has to be an operation like 'Mean'-'MeanBackground'. Only two columns are allowd and only
                             + - * / can be used as operators.
       Input extra_col_name: False by default. If string, it will be the name of the column for the math operation. It is important that
                             the extra col name is not existent in the main roi measurements.
                             
       Output : No output, but every main csv file is now updated with the new metric as a new last column. 
    """


    def Extra_Calculation_Column():
        """ Constructs the mathematical operation based on the extra_calc_col and checks whether the column from main roi measurement exists.
            Returns a pd series with the results of the operation for each row"""
        
        if Checks.ColumnOfRoiMeasurementsExists == 'column_not_found_in_csv' : return 'failed_to_find'
        else : 

            # define variables in case extra_calc_col will not be false
            ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
                    }                           
            pattern    = r'\b(\w+)\s*([+\-*/])\s*(\w+)\b'
            matches    = re.match(pattern, extra_calc_col)
            minuend    = matches[1]                                                                           # not using index 0 since 0 gives the whole match
            op         = matches[2]                                                                           # second position is the operator
            subtrahend = matches[3]

            all_results = []
            for index in range(len(main_df)):                                                                 # iterate through the number of dataframe rows
                first_col_val = main_df[minuend].iloc[index]                                                  # get the value of the particular row minuend 
                sec_col_val   = main_df[subtrahend].iloc[index]                                               # get the value of the particular row subtrahend
                res = ops[op](first_col_val,sec_col_val)                                                      # get the result of the operation
                all_results.append(res)  
            seriesults = pd.Series(all_results)                                                               #convert the list to series
            return seriesults

    
    new_metric_name = metric_prefix + metric                                                                   # a FindEdges is added first to the name because there is already an StdDev measurement for the normal measurements (without find edges)
    temporary_storage:dict = {}                                                                                # to prevent unwanted changes in the main measurement files, the latter will only be overwritten after ensuring no errors occure
    for new_csv_subdir_path, main_csv_subdir_path in new_and_main_paths :
        all_new_csv_files_paths = sorted ([join(new_csv_subdir_path,one_path) for one_path in listdir(new_csv_subdir_path) if isfile(join(new_csv_subdir_path,one_path))])
        all_main_files_paths    = sorted ([join(main_csv_subdir_path,one_path) for one_path in listdir(main_csv_subdir_path) if isfile(join(main_csv_subdir_path,one_path))])
        for new_csv_path, main_csv_path in list(zip(all_new_csv_files_paths,all_main_files_paths)):             # a second zip takes place here, to match files per se and not just subdirectories
            new_df  = pd.read_csv(new_csv_path)  
            main_df = pd.read_csv(main_csv_path) 
            if new_df.shape[0] != main_df.shape[0] :                                                            # ensure the number of rows is the same
                message = (f"A mismatch of regions of interest was detected between "
                        f"{new_csv_path} and {main_csv_path}. This is unexpected and"
                        " the function will stop.")
                Checks.ShowError('Unequal number of Rois', message)
                return 
            new_df[metric] = new_df[metric].fillna(0.000001)                                                    # THIS IS IMPORTANT. NaN values are converted to 0.000001 to maintain filtering based on numeric values and prevent division errors
            main_df[new_metric_name] = new_df[metric].values                                                    # pass the new metric to the main measurement dataframe. This runs always, regardles the existence of extra calc col or not
            if (extra_calc_col != False) and (extra_col_name != False) : 
                additional_col = Extra_Calculation_Column()
                if isinstance(additional_col, str) and additional_col == 'failed_to_find' : return 'failed'     # first we check if it is string, because if function does not return the string failed, it returns a series, and using the second statement directly would yield error   #if there was an error, a 'failed' message passes to main code, which stops everything
                additional_col = additional_col.fillna(0.000001)                                                # THIS IS IMPORTANT. NaN values are converted to 0.000001 to maintain filtering based on numeric values and prevent division errors
                main_df[extra_col_name] = additional_col.values  
            temporary_storage[main_csv_path] = main_df                                                          # This runs always, regardles the existence of extra calc col or not

    for Main_Path, dframe in temporary_storage.items() :
        dframe.to_csv(Main_Path,index=False)                                                                    # index = False to avoid registering new indices
    complete_msg = (f'The metric {metric} has been passed as a new column to the initial measurement files '
                    f'under the name {new_metric_name}')

    Checks.ShowInfoMessage('Step completed', complete_msg )





def GatherCsvsToOne(new_metric_subdirs, main_saves_path, new_metric = 'ShannonEntropy'):
    """Gets the value from every single roinumber.csv file and assignes it to a new csv file
       that contains the Shannon Entropy measurement from all the roinumber.csv files of that image.
       The latter csv file will be stored in the same directory where the folders with image names are stored.
       Also checks for same Entropy values across adjacent rois (which is indicative of wrong measurement), 
       to ensure that histograms where closed properly in Fiji when the Entropy values were first obtained. This
       additional check is useful since the speed that fiji operates sometimes affects processing.
       
       Input new_metric_subdirs : list that contains all subdir paths (e.g. [path../plane1_Entropy, path../plane_2_Entropy]).
       These subdirectories contain subfolders, each one corresponding to a filename. Inside those folders, there are
       roinumber.csv files.
       Input main_saves_path : str indicating the path to the main measurements. Used only for a contingent ShowInfo message"""

    # For future reference, check if the fact that it is nested affects the way it works. Should be ok since we are not referencing arguments from GatherCsvsToOne.
    def recursive_defaultdict():
        return defaultdict(recursive_defaultdict)
    
    # Example of accessing a csv after grouped has been completely defined
    # grouped['C:\\Users\\angdid\\Desktop\\testit\\EntropyResults\\plane1_Entropy']['C:\\Users\\angdid\\Desktop\\testit\\EntropyResults\\plane1_Entropy\\plane1.tif']['001_454.csv']
    grouped=recursive_defaultdict()                                                                                     # dictionary of this type {path../plane1_Entropy:{image_filename} : {roinumber.csv} : EntropyValue}
    same_value_warnings = recursive_defaultdict()

    for metr_subdir in new_metric_subdirs:
        metr_subdir = normpath(metr_subdir)
        images_subdir_names = sorted ([folder for folder in listdir(metr_subdir) if isdir(join(metr_subdir,folder))]) # create list with foldernames (e.g. imageID) per subdir (planeN). Only names here, not paths.
        images_subdirs = [join(metr_subdir,folder) for folder in images_subdir_names]                                   # creates list with a path to each foldername. Done this way to sort based on the sole names first and only then add the preceding path.
        for filename_folder in images_subdirs :                                                          
            filename_folder = normpath(filename_folder)
            each_roi_name = sorted ([csv for csv in listdir(filename_folder) if isfile(join(filename_folder,csv))])      # create list with names to all csv files per folder. Done this way to sort based on the sole names first and only then add the preceding path.
            for roinumber_csv in each_roi_name:
                path_to_csv = join(filename_folder,roinumber_csv)                                                       # creates the path to each single csv
                df = pd.read_csv(path_to_csv, nrows=1)
                metr_value  = df[new_metric].loc[0]
                grouped[metr_subdir][filename_folder][roinumber_csv] = metr_value
                
                try :                                                                                                   # to ensure that fiji hasnt used same histogram for different rois when measuring rois, the previous ShannonEntropy is compared to the current
                    previous_value                                                                                      # first iteration would yield keyerror, hence the try
                except : previous_value = df[new_metric].loc[0]                                                         # if keyerror, it means this inner loop is running for the first time
                else :                                                                                                  # if it is not running for the first time, then check if current value is equal to previous
                    if previous_value == metr_value :
                        same_value_warnings[filename_folder][roinumber_csv] = metr_value                                # if so, add to the warning recursive default dictionary
                finally : previous_value = metr_value                                                                   # in any case, create a previous_value from the current value, to be used for next iteration
    
    # only creates the csv files after ensuring that the code above runs without errors. Safer to make a complete set of files.
    for metr__Sub in grouped.keys():                                                                                   # an example would be 'C:\\Users\\angdid\\Desktop\\testit\\EntropyResults\\plane1_Entropy'
        for image__Sub in grouped[metr__Sub].keys():                                                                   # an example would be 'C:\\Users\\angdid\\Desktop\\testit\\EntropyResults\\plane1_Entropy\\plane1.tif'
            entropy:dict = {}
            imagename,extension= splitext(basename(image__Sub))                                                        # get the image name only, and not the file extension from the end of the path
            for single_roi, value in grouped[metr__Sub][image__Sub].items():                                           # create dictionary with roiname as keyu and entropy value as number
                single_roi,_ = splitext(single_roi)                                                                    # we don't want the .csv extension of the roinumber.csv names          
                single_roi = f'{imagename}{extension}:{single_roi}'                                                    # the other csv measurement have roinumbers like this -> imagename.tif:roinumber. So we want the same
                entropy[single_roi] = value
            # after the inner loop is finished, create a csv file including all roi new metric measurements
            writepath = join(metr__Sub,imagename) + '.csv'                                                             # create a path ending to .csv instead of .tif or whichever extension. We use the metr__Sub on purpose to create the file out of the rest roinumber csvs
            df = pd.DataFrame.from_dict(entropy, orient='index', columns=[new_metric])
            df = df.reset_index()                                                                                      # add the indices to match the measurements file
            df.index = df.index + 1                                                                                    # start index number from 1 to match the previous measurements
            df.columns = ['Label', new_metric]                                                                         # add the Label to match the measurement file
            df.to_csv (writepath,index=True)                                                                           # add the indices to match the measurements file
    

    if bool(same_value_warnings) == True :                                                                             # if there have been observed same adjacent (in terms of roinumber) Entropy values, store in log file
        random_subdir_case = new_metric_subdirs [0]                                                                    # a path is needed to find the parent directory
        parent_dir = dirname(random_subdir_case)
        logpath = join(parent_dir,'entropy_log.txt')
                                                                                
        try: exists(join(parent_dir,'entropy_log.txt'))                                                                # check if the log file has been previously created
        except : 
            open (logpath, 'w').close()                                                                                # if not, then create it
        with open (logpath,'a') as f :                                                                                 # in all cases, start writing the instances of same values
            message = (f' Adjacent values observed in at least one of the planeN foldernames\n')
            f.write(message)
            for Folder__Name, Roi__Nums_and_values in same_value_warnings.items():
                for a_roi, a_value in Roi__Nums_and_values.items():
                    f.write(f"{Folder__Name}, roilabel : {a_roi} and its preceding one, {new_metric} value : {a_value}\n")
            f.write('\n\n\n\n\n')
        
        msg = (f'Same entropy values were observed for adjacent roi labels. Check the entropy_log.txt file in '
                   f'this directory {parent_dir}. Fiji/ImageJ might have measured Entropy wrong. AResCoN will now start '
                   f'passing the entropy values of each roi to the respective measurement csv file under the {main_saves_path} main directory')
        Checks.ShowInfoMessage('Suspicious same Entropy values', msg)

    else : print('No suspected duplicate entropy values were found')

      
                

            


   

    