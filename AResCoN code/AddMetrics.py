# from shapely.geometry import Polygon
from os import listdir
from os.path import join, isdir, isfile
from read_roi import read_roi_zip
from collections import defaultdict
import copy
import pandas as pd
import shapely
from shapely import Polygon
import Checks
# roipath = r"C:\Users\angdid\Desktop\testit\RoisFolder\plane1Rois"
# path_to_measurements = r"C:\Users\angdid\Desktop\testit\save\plane1_Measurements"
# plane=1



################# COMMENTS MUST BE RE-WRITTEN BASED ON CHANGES ! ###########

def LoadRoiMeasurements(run=False, **kwargs) : 
    """Receives a path with planeN_Rois and a path with planeN_Measurements and then passes all info to the newly created roi objects.
       Also checks for overlaps across the same plane and registers them in each overlapping object.
       Slightly changes the name of the rois too, to include information about the plane number.
       Input run : by default False. If set to True, function will eventually be executed
       Inputs for kwargs : the roipath of a planeN folder (str), the path to csv measurements of the same planeN folder(str) and the plane number (int)""" 

    roipath              = kwargs.get('PlaneWithRois')
    path_to_measurements = kwargs.get('SaveMetricPath')
    plane                = kwargs.get('plane')
    # roipath = r'C:\Users\angdid\Desktop\testit\RoisFolder\plane1_Rois'
    # path_to_measurements = r'C:\Users\angdid\Desktop\testit\save\plane1_Measurements'
    # plane = 1

    def ListZips ():
        """ Creates a list will all paths directing to zip files that were created in fiji and contain rois.  
            Input : string which is a path to the planeN_Rois folder containing the zip files
            Output: list with strings. Each string a path to a particular zip file"""
        
        list_with_all_zips = [roipath+'/'+file for file in listdir(roipath) if isfile(join(roipath, file))]
        return list_with_all_zips

    def ReadRoiZips(zipaths) :
        """ Reads the information of rois (per zip file), such as their coordinates.
            Slightly changes the name to include the plane info (-N, where N corresponds to plane number)
            Input : list with strings. Each string a path to a particular zip file
            Output: No returned values. Yet, it creates and a new instance based on the name of the image and the roi (see RoiClass).
                    The name of the image is passed to the imagename of the RoiClass, the name of the roi to the roiname of the RoiClass
                    and the rest of the info regarding the roi is passed to the info of the RoiClass"""
        
        for zipfilepath in zipaths :
            all_rois_in_a_zip= read_roi_zip(zipfilepath)                                             # if there is an error related to the channel, try resaving your rois after first implementing them with fiji on top of the image (dont bake them into the image)                                                                              # rois are named 001_001 , 001_002, 001_003 etc      
            last_slash_index = max(zipfilepath.rfind('/'), zipfilepath.rfind('\\'))
            zipfilename = zipfilepath[last_slash_index:]
            zipfilename = zipfilename.strip(".zip").strip("/").strip("\\")
            for roiname, roinfo in all_rois_in_a_zip.items():             
                roiname = f'{roiname}-{plane}'                                                       # rois will turn from 001_045 to 001_045-2 to encompass plane number info
                RoiClass (zipfilename,roiname,roinfo)                                                # create new instance with zipfilename as imagename, roiname as roiname and roinfo as info.


    class RoiClass :                                                    
        roi_instances = defaultdict(dict)                                                            # create a directory with instance names (imagename) as main keys and dict as values (where key is the name of the roi and value the whole instance)

        #intersects with does not work properly !!!!!!!!!!
        def __init__ (self, imagename, roiname, info) :                                                        
            self.imagename = imagename
            self.name = roiname
            self.info = info                                                                         # info is the ordered dict produced by read_roi_zip() in ReadRoiZips. Contains information such as coordinates
            self.polygon = Polygon(list(zip(self.info['x'],self.info['y'])))                         # creates a polygon based on the coordinates
            self.intersects_with = []                                                                # Overlap in the same plane only. Initially empty but will include roi names of rois that overlap in this plane with each object
            RoiClass.roi_instances[self.imagename][roiname]= self                                    # the whole instance is attributed as value. This helps easy retrieval.

        # This classmethod can be used in detection pipelines that allos overlap in same image
        # It is slow though. The deep copy has to be taken out. Nested for loops are also 
        # problematic in this case because rois might be many.
            
        # @classmethod
        # def FindOverlapSamePlane (cls,name_of_image):
        #     """Finds overlaps across the same plane. Then appends them to the intersects_with 
        #     list that corresponds to each particular roi (object) tested for overlaps.
        #     This means that if 001_010 overlaps with 001_430, the latter will also be
        #     overlapping with the first in its own intersects_with instance list"""
            
        #     copied_instances = copy.deepcopy(cls.roi_instances[name_of_image])                       # Making a copy helps a bit with readability
        #     for name_of_roi, roinstance in cls.roi_instances[name_of_image].items():                 # Iterate through the items (roi name and whole object) of the particular image
        #         main_polygon = roinstance.polygon                                                    # make the polygon roi
        #         for name_of_copy_roi, copyroinstance in copied_instances.items():                    # Iterate again through the items (roi name and whole object) of the particular image
        #             compare_polygon = copyroinstance.polygon                                         
        #             if name_of_roi != name_of_copy_roi :
        #                 try :
        #                     overlapolygon = main_polygon.intersection(compare_polygon)               # Test whether there is an overlap between the two polygons
        #                 except  :                                                                    # This is explained in the stardist training steps word file. If the polygon is not drawn correctly this error might occur. Normally, the except name is GEOSException but it yields error and it is complicated to import it. Keep an eye on that. Error could be anything.
        #                     print(f" WARNING : The roi {roinstance.name} or {copyroinstance.name} is"
        #                         "probably a polygon drawn improperly. It cannot be analyzed")
        #                 else :
        #                     overlapping_area = overlapolygon.area
        #                     if overlapping_area == 0 :
        #                         continue
        #                     else : 
        #                         roinstance.intersects_with.append(copyroinstance.name)                # If there is an overlap, add the roi name of the overlapping roi to the intersects_with list of the first

        @classmethod
        def PassMeasurementsAsAttributes(cls,csvpath,imagename) :
            """Takes every measurement and passes it as attribute tho the respective [imagename][roiname] instance. 
            Input csvpath : string that is a path directing to a single csv file containing measurements of rois
            for a particular plane.
            Output : Dictionary with the the final form of the instances for the particular plane this module is running for.
            Keys are names of the rois and -N in the end, where N corresponds to a number from 0 to 9, indicating plane number.
            For instance '001_004-2'. The value is the particular instance itself, which has a set of attributes. 
            """

            errors = 0                                                                                                # will add by one every time a match could not be done
            
            measure_df = pd.read_csv(csvpath)  
            try :                                                                                                      #there is a useless initial column that we can get rid of
                measure_df.drop (" ") 
            except :
                pass   
            measurements = measure_df.columns                                                                          # gets the names of the columns, eaech one corresponding to a measurement
            overal_rows = measure_df.shape[0]
            for row in range(overal_rows) :
                cruderoiname = measure_df.loc[row, 'Label']                                                            # one column must be the label itself, where labels are like mouseID:roiname
                cruderoiname += f'-{plane}'                                                                            # rois will turn from 001_045 to 001_045-2 to encompass plane number info
                _,clearoiname = cruderoiname.rsplit(":")                                                               # for the split to work, it is essential that the format of the label column of the results.csv is like this mouseID.tif:001_001. 
                for measuremenT in measurements :                                                                      # measuremenT must be the name of a column of the results.csv (like Mean or Area)
                    if measuremenT not in [" ", "Label"]:
                        try : 
                            cls.roi_instances[imagename][clearoiname]                                                  # We need both the imagename and roiname to access an object.
                        except :
                            print(f"Could not match {clearoiname[:-2]} (which "
                                "was derived from a csv file with measurements)"
                                "to an actual roi name")
                            errors += 1          
                        else :
                            setattr(cls.roi_instances[imagename][clearoiname], measuremenT, measure_df.loc[row, measuremenT]) # add the measurement as an attribute to the object
                            setattr(cls.roi_instances[imagename][clearoiname], 'plane', plane)                                # add the plane number for extra info (although main code architecture takes care of separating planes)
            if errors != 0 : Checks.ShowMismatchError(errors)                                                                 # code goes on but user has been warned of mismatches
            return cls.roi_instances

    if run == True :
        all_instances:list = []                                                                         # all instances will be appended here and finally returned inside this list
        roipaths = ListZips()
        ReadRoiZips(roipaths)
        for an_image_name in RoiClass.roi_instances.keys():
            # RoiClass.FindOverlapSamePlane(an_image_name)                                              # the FindOverlapSamePlane is effectively uselss with cellpose-SEM, since predictions never overlap (no imaginary extension of objects on top of others)
            the_csvpath = join(path_to_measurements,an_image_name) +'.csv'
            all_instances.append (RoiClass.PassMeasurementsAsAttributes(the_csvpath,an_image_name))
        return all_instances  


if __name__ == "__main__":
    LoadRoiMeasurements(run=True)