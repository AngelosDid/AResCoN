import re
from collections import OrderedDict, defaultdict
import Checks
from os.path import join, normpath, basename, splitext
from roifile import ImagejRoi
from io import BytesIO
import numpy as np
import zipfile
import dill as pickle



def NonWordsToAtSymbol (string):
    """Converts the non alphabetical parts of a string to @. For instance, (Area>30) becomes @Area@@@@.
    This is useful for direct string detection and comparison. For example, condition based on user input
    is (Feret>20). When trying to find a Feret in the roi objects attributes, matching with FeretAngle
    will be prevented because after Feret in FeretAngle is found, the next character in FeretAngle is not @
    but a letter instead. Meaning that the match is not 1to1. 
    Mind that : the match itself is part of another function.
              : we insert an extra @ after the convertion has been made to prevent listIndex errors in other functions  """
    
    changed_word =""
    for char in string:
        if char.isdigit() or char in ['<','>','=','+','-','*','(',')']:
            changed_word += '@'
        # for metric filter conditions, skipping on purpose the 'and' assuming it is always preceded by whitespace, meaning it would not affect 1to1 string detection
        else : changed_word += char
    changed_word += '@'                                                                                                                      # insert one extra @ at the end, to prevent listIndex errors in a situation like @@@Feret (in the end of the string condition) where we want to check if after the n follows @ or a character (or whitespace). See the match.end in ApplyOnePlaneFilters
    return changed_word

def GetAttributeNamesFromSingleRoi (basedic):
    """Simply finds the attribute names from the first roi objects from the first image from the first planeN subdirectory.
       Input : dictionary, which is the main_dictionary of the main code
       Output: list with attribute names
    This is also used as snippet in Checks.MetricNotInCSV."""
    first_planename          = list(basedic.keys())[0]                                                                                        # for instance, 1
    first_imagename          = list(basedic[first_planename][0].keys())[0]                                                                    #first_planename[0] instead of first_plane name because the architecture has always a zero index -> main_dictionary[1][0]['plane1.tif']['001_002-1']  Mind that plane.tif is just the name of an image, not of a plane
    first_roiname            = list(basedic[first_planename][0][first_imagename].keys())[0]
    all_roi_attr_names       = dir(basedic[first_planename][0][first_imagename][first_roiname])
    
    final_attribute_names = []
    for attrib in all_roi_attr_names : 
        if ("__" not in attrib) and (attrib not in ['name','intersects_with','info','imagename','polygon','plane','roi_instances']) :                                           # exclude attributes with __ and those in the list because they are not real csv roi measurements
            # 'PassMeasurementsAsAttributes' is also an attribute name
            final_attribute_names.append(attrib)   
    return final_attribute_names


def GetAttributeAndConditioNameMatches (attrib_names,at_conditions,pure_conditions):
    """Finds the EXACT MATCHES ONLY between an attribute name and a metric and locates the start and end index of the matches
       For instance, Feret will not match exactly with FeretX or FeretAngle, even though the latter comprise Feret.
       Input attrib_names   : list with strings indicating names of measurements 
       Input at_conditions  : list with strings indicating conditions, yet with all numbers and operators converted to @ 
       Input pure conditions: list with strings indicating conditions
       Output : dictionary with filtering condition as keys (str). For instance '(300>Area>30 and Mean>20)'
       and as a value a dictionary tha has names of attributes as keys (i.e. 'Area') and a tuple(startindex,endindex) as a value.
       The start and stop index are the indices where the key name responds inside the condition. The order of key names is based on
       the tuple value, that is, the key name that has the lowest tuple value comes first, the second lowest comes second and so on"""
    
    name_matches = defaultdict(dict)                                                                                                                                                                                                                            
    for condindex, whole_condition in enumerate (at_conditions) :                                                                                # iterating over masked filtering conditions with @@ where there are not real letters. Like @@@@@Area@@@@@ instead of (300>Area>20). Mind the extra last @
         pure_condition = pure_conditions[condindex]                                                                                             # eventually, we will use as a condition key the key condition and not the masked one
         for name in attrib_names:
            matches = re.finditer(name,whole_condition)
            #create list with tuples containing start and stop index of the match. Mind that finditer gives as end index one index after the observation
            ss_ind = [(match.start(),match.end()) for match in matches ]                                                                                # this is the first and last index of an observed INITIAL name match between attribute names and a condition masked with @@@. Initial means not necessarily perfect (For instance, Feret matches with FeretAngle but its not the same)                                                          
            allow_sym = [" ","@"]                                                                                                                       # We will allow whitespaces and @ , i.e.  '@RoiAndBackgrounDifference @ SurroundingMean@@.@@@' the stop index of RoiAndBackgrounDifference is whitespace                                                                        
            appearances = [(pos,ti) for pos,ti in enumerate (ss_ind) if whole_condition[ti[0]-1] in allow_sym and whole_condition[ti[1]] in allow_sym]  # ti is the tuple. ti[0] is the start index and ti[1]the stop index +1 by default of finditer.  We look one back from start and one at the stop (which is plus one by default). If surrounded by @, it means perfect match. If not, then it is NOT a final match, because the match is only partial (meaning that the attribute name matched ONLY A PART of the condition metric name).pos is the position of this tuple in the matches list. 
            appearances_n = len(appearances)                                                                                                            # continuing for comment above. This is also the reason we add an extra @ while calling Mediator.NonWordsToAtSymbol. If we had @@@@Mean , looking for a character after n would yield an index error. Also notice that ti[0]-1 is allowed to be whitespace too. For instance Max<400 and Min>30. Min wouldnt be captured here because whitespaces do not become @
            if appearances_n > 1 :
                message = (f'The metric {name} was found {appearances_n} times instead of one '
                f'inside the same condition {pure_condition}. Unfortunately, the current AResCoN version cannot process this information. ' 
                ' You can try factoring your input or create a new column in your man roi measurements that encompasses the double expression'
                ' of your metric and proceed again. Filtering will now stop. ')
                Checks.ShowError('Duplicate name detected',message)
                return 
            if appearances_n==1 :
                perfect_match = appearances[0][1]                                                                                                # the tuple that corresponds to the only perfect name match inside a condition                                            
                startindex,stopindex = perfect_match[0], perfect_match[1] -1
                name_matches[pure_condition][name] = (startindex, stopindex)                                                                     # append start and stop index of the match in tuple format. 
                pass
    
    # sort the dict (not the defaultdict) inside the default dict based on earliest start and stop index. This will help later with condition versions in cases where condition have more than one metric and (meaning using and)
    # the condition keys themselves must be already sorted by default because we create them in the right order
    sorted_name_matches = defaultdict (dict)
    for condition, metric in name_matches.items():
        temporary_list = []
        for metric_name, tuple in metric.items():
            temporary_list.append((metric_name,tuple))
        sorted_temporary_list = sorted (temporary_list, key=lambda x: x[1])
        for sortname, sortuple in sorted_temporary_list :
            sorted_name_matches[condition][sortname]=sortuple

    return sorted_name_matches

def IndexKeeper (len_of_metric_value, len_of_metric_name):
    """In a condition string that changes dynamically when replacing metric name with a value, i.e. Area>30 -> 50>30 
       This function keeps record of len change in a string, to allow smooth replacement of all names inside a condition
       without listIndexErrors
       Input len_of_metric_value     : int corresponding to number of digits of a value of a metric
       Input len_of_metric_name      : int corresponding to number of letters of a metric name
       """
    
    if len_of_metric_value == len_of_metric_name :               # For instance , if Area = 1300, nothing will change in the number of characters in the condition "(300>Area>30)" because 1300 has 4 characters ->(300>1300>30) , just like Area
        index_shift = 0
        return index_shift
    
    elif len_of_metric_value > len_of_metric_name:
        index_shift = (len_of_metric_value-len_of_metric_name)
        return index_shift

    elif len_of_metric_value < len_of_metric_name:
        index_shift = -(len_of_metric_name-len_of_metric_value)  # Mind the minus sign. If the metric name was bigger (in terms of characters) compared to the digits of the value, then the overall length of characters in the string condition has been reduced 
        return index_shift




def FindViolatingROIs(basicdict,name_match):
    """Loops through 1) plane number 2) imagename 3) roi objects 4) condition in parenthesis (potentially including and inside) along with metric names
       that we already know that exist in this condition 5) each metric name along with its start and stop match position to the condition.
       It replaces the metric name with the roi value of this metric. For instance, '(Area>30) becomes 50>30 if roi.Area = 30.
       To maintain right replacement in a combined condition (always in parenthesis) that contains and '(i.e. Area>30 and Mean>60)', it uses
       Index keeper, that keeps track of the length changes in the string condition, when replacing letters with digits.
       Input basicdict     : dictionary that corresponds to the main_dictionary of the main code
       Input name_match    : dictionary that is the output of GetAttributeAndConditioNameMatches. More precisely, dictionary with
                             filtering condition as keys (str). For instance '(300>Area>30 and Mean>20)'
                             and as a value a dictionary tha has names of attributes as keys (i.e. 'Area') and a tuple(startindex,endindex) as a value.
                             The start and stop index are the indices where the key name responds inside the condition. The order of key names is based on
                             the tuple value, that is, the key name that has the lowest tuple value comes first, the second lowest comes second and so on
       Output               : list with two dictionaries : 
                              1)One dictionary that includes only the rejected rois based on filtering. Its format is 
                              rejectedict[planenumber][imagename][roi.name]:[list with str conditions failed to meet, with the operator symbols translated,roi].
                              2)A second dictionary that includes only the accepted rois based on filtering. Its format is 
                              acceptedict[planenumber][imagename][roi.name]= roi . Note that innermost value is in this case an object, not a list.                                                                
                              Mind that roi -that is the last element rejectedict and the (innermost value) in the acceptedict- is the actual roi object (and not the roi_object).  """
    
    def recursive_to_be_rejected_rois():
        return defaultdict(recursive_to_be_rejected_rois)
    
    def ConverOperatorsToLetters (stri_conditions):
        """Translates operators to symbols, thus allowing later creation of files with the translated names
           Input stri_conditions : list with strings correspond to conditions like '(Area>30)'
           Output                : same list but with operators now changed based on the symbol_converter"""
        symbol_converter = str.maketrans ({
            '<': '_less_than_',
            '>': '_more_than_',
            '=': '_equals_',
            '*': '_times_'
        })
        converted_conditions = []
        for cndtn in stri_conditions :
            converted_conditions.append(cndtn.translate(symbol_converter))                                                           # append a converted version to avoid windows error while creating file
        return converted_conditions
 
    rejectedict            = recursive_to_be_rejected_rois ()                                                                        # this will be the final output of rejected rois
    acceptedict            = recursive_to_be_rejected_rois ()                                                                        # this will be the final output of accepted rois
    symbol_free_conditions = ConverOperatorsToLetters(list(name_match.keys()))                                                       # Do not mistake symbol free conditions with the translated from name to value (for comparison checks). Here, we just change the operator symbols to allow saving files in the future. 
                  
    for planenumber in basicdict.keys():
        image_names = basicdict[planenumber][0].keys()
        for image_name in image_names :
            objects = basicdict[planenumber][0][image_name].keys() 
            for roi_object in objects :
                # Careful here, the actual roi object is the roi, NOT the roi_object
                roi = basicdict[planenumber][0][image_name][roi_object]
                all_conditions_boolean = []                                                                                           # each condition inside a parenthesis will be True or False when eval(changing_condition). For a ROI to pass all condition criteria (which can be more than one parenthesis), it has to have only True inside this list
                for condition, metricnames in name_match.items() :
                    index_changer = 0                                                                                                 # index changer is based on IndexKeep and keeps a record of how many characters smaller (-) or larger (+) the length of the string condition has become. We start with 0 because we dont want any index changes while replacing for the first name (remember they have been sorted based on tuple values beforehand). Before the string condition changes, indices are correct.                                                                    
                    changing_condition = condition                                                                                    # In each iteration within a condition, a metric name will change to a value. We'll be using this dynamic string till the final condition without names is formed. This happens at 1st iteration when there is only on metric name. But we might have conditions with and                                                                                    
                    for metricname, metric_match_indices_in_condition in metricnames.items():  
                        roi_metric_val     = getattr(roi, metricname)
                        n_of_digits        = len(str(roi_metric_val))
                        metricname_len     = len(metricname)
                        start,end          = metric_match_indices_in_condition[0],metric_match_indices_in_condition[1]+1
                        start,end          = start+index_changer, end+index_changer                                                   # if the string of the condition has changed (from second iteration only inside a condition with many and that contain different names), then the indices in the match have to change too
                        changing_condition = changing_condition[:start] + str(roi_metric_val) + changing_condition[end:]              # turning '(300>Area>30 and Mean>50)' to '(300>100>30 and Mean>50)'  And then Mean will become a number too, after the indexing is adjusted
                        index_changer     += IndexKeeper(n_of_digits,metricname_len)                                                  # += because index_changer is dynamic. It keeps the record of changes of indices towards left (minus) or right (plus) based on the name character replacement with digits

                    if "nan" in changing_condition :                                                                                  # metrics like Mean can rarely be nan due to bad shapes. If so, we will not eval the condition and deem it as false. It goes without saying that this will virtually cancel any measurement that included nan in its name. So nan should not exist within any metric name
                        print(f"A nan value was found in {image_name}, and roi object {roi_object}. Condition was {condition} and " 
                              f"the changed condition was {changing_condition}. The roi will be excluded. Ensure that you have no "
                              f"metric names that include the sequence nan")
                        result = False
                    else :
                        result = eval(changing_condition)                                                                             # the condition inside the parenthesis will (either it is a single condition or a combined one using and [but always inside a parenthesis], will be tested for true of false)
                    all_conditions_boolean.append(result)
                if all(all_conditions_boolean) == False :                                                                             # if there is at least one false, then we will get a False results here, meaning that roi didnt pass all filtering conditions
                    roi_Clerk    = []                                                                                                 # Mr. Clerk will keep record of violations of conditions
                    for index, rslt in enumerate (all_conditions_boolean):
                        if rslt == False :
                            symbol_free_cond = symbol_free_conditions[index]
                            roi_Clerk.append(symbol_free_cond)
                    roi_Clerk.append(roi)                                                                                             # after the conditions, we also add the roi object itself
                    rejectedict[planenumber][image_name][roi.name] =roi_Clerk
                else :
                    acceptedict[planenumber][image_name][roi.name] = roi                                                               
    
    return [rejectedict,acceptedict]
                



def RecreateRoisInsideFilteredDict(excluded,included,timestampath):
    """Converts the polygons to rois again, zips them and adds them to the respective planeN subdir
       Input excluded       : rejectedict[planenumber][imagename][roi.name]:[list with str conditions failed to meet, with the operator symbols translated,roi].
       Input included       : acceptedict[planenumber][imagename][roi.name]= roi
       Input timstampath    : string indicating the path where the FilteredRoisXY_timestamp is
       Output               : None of str indicating path where a pickle file with included rois will be saved"""
    

    # - - - Handling Rejected First - - - #

    symbolless_dict = defaultdict(list)                                                                      # will retain the path up to imagename (see constructed path) as keys and values will be all roi paths corresponding to the constructed path. This helps to create a zip file with all rois without looping from scratch

    for planenumber in excluded.keys():
        for imagename in excluded[planenumber].keys():
            for roiname in excluded[planenumber][imagename].keys():
                conditions = excluded[planenumber][imagename][roiname][:-1]                                  # everything before the last element is the conditions with translated operators
                planen_folder_name = f'plane{planenumber}_Rois'
                poly = excluded[planenumber][imagename][roiname][-1].polygon
                poly = np.array(poly.exterior.coords[:-1])                                                   # To exclude duplicate last point if needed
                for condition in conditions :
                    constructed_path = join(timestampath,'Rejected',planen_folder_name,condition,imagename)
                    roi = ImagejRoi.frompoints(poly)
                    roi_name = roiname
                    roi.name = roiname
                    roi_path = normpath(join(constructed_path,f"{roi_name}.roi"))
                    symbolless_dict[constructed_path].append(roi_path)                                       # the particular roi file path will be saved in a list that will retain all roi paths for this image , under these conditions
                    roi.tofile(roi_path)
                     
    for path_up_to_imagename in symbolless_dict.keys(): 
        zip_filename = path_up_to_imagename + ".zip"
        with zipfile.ZipFile(zip_filename, 'w') as roi_zip:
            roi_paths = symbolless_dict[path_up_to_imagename]
            for roi_path in roi_paths:                                                                       # roi_path example  'C:\\Users\\angdid\\Desktop\\filters\\FilteredRoisXY_20250706_113114\\Rejected\\plane1_Rois\\(Area_more_than_400)\\plane1.tif\\001_001-1.roi'
                Roi_Name = basename(roi_path)                                     
                roi_zip.write(roi_path, Roi_Name)


    # - - - Handling Accepted Below - - - #

    for planenumber_inc in included.keys():
        for imagename_inc in included[planenumber_inc].keys():
            roinc_paths = []                                                                                   # paths of each newly created roi file will be appended here   
            for roiname_inc in included[planenumber_inc][imagename_inc].keys():
                planeN_folder_name_inc = f'plane{planenumber_inc}_Rois'
                poly_inc = included[planenumber_inc][imagename_inc][roiname_inc].polygon
                poly_inc = np.array(poly_inc.exterior.coords[:-1])                                               # To exclude duplicate last point if needed
                constructed_path_inc = join(timestampath,'Accepted',planeN_folder_name_inc,imagename_inc)
                roinc = ImagejRoi.frompoints(poly_inc)
                roinc_name = roiname_inc
                roinc.name = roiname_inc                                                                     # this is the name of the roi object. Real name of label (when ticking show real names in labels in fiji)
                roinc_path = normpath(join(constructed_path_inc,f"{roinc_name}.roi"))
                roinc_paths.append(roinc_path)
                roinc.tofile(roinc_path)
                pass

            zipinc_filename = constructed_path_inc + ".zip"
            with zipfile.ZipFile(zipinc_filename, 'w') as roinc_zip:
                for Roinc_Path in roinc_paths :
                    Roi_Name_inc = basename(Roinc_Path) 
                    roinc_zip.write(Roinc_Path, Roi_Name_inc)

    svmsg = (f"Your filtered ROIs have been placed inside {timestampath} .\n\n"
             "It is recommended to create a pkl file that retains the information of accepted ROIs.\n\n"
             f"Click Yes to get a pkl file inside {timestampath+'/Accepted'} or No to continue without saving") 
    if Checks.AskConfirmation('Filtering completed',svmsg) == True :
        pklsavepath = join(timestampath,'Accepted','Accepted_ROIs.pkl')
        return pklsavepath 

    else :
        messg = ("You have opted for not saving a pkl file. You can continue the analysis but if you close AResCoN "
        "you will have to run the filtering step again.")
        Checks.ShowInfoMessage("Filtered-in ROIs not saved", messg)
        return None

### This code is generated by AI, I used it to serialize data to combat a pickle creation problem
### because the rois inside the recursive dict were created in a nested class within a function in another module
### As a result, the object attributes will turn to dict with values, which means it is not equivalent to filtered in anymore
def SimpleSerialize(obj, seen=None):
    """ Coverts the filtered_in data to a serializable dict (different in innermost value type)
        to allow pickle creation"""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return "<circular>"
    seen.add(obj_id)

    if isinstance(obj, dict):
        return {k: SimpleSerialize(v, seen) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):  # handles RoiClass and others
        return {key: SimpleSerialize(val, seen) for key, val in vars(obj).items()}
    elif isinstance(obj, list):
        return [SimpleSerialize(item, seen) for item in obj]
    else:
        return obj  # int, str, float, etc.
            