import dill as pickle
from shapely import Polygon
from shapely.ops import unary_union
from shapely.geometry import Point, Polygon
from shapely.affinity import scale
from collections import defaultdict
import copy
import Checks
from roifile import ImagejRoi
from os.path import normpath, join, basename
from os import listdir, mkdir
import numpy as np
import zipfile
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from rtree import index
import io
from pathlib import Path
from rtree import index
from shapely.errors import GEOSException
from shapely.geometry import Polygon
from collections import defaultdict
import PathMaker


# This module Returns None if runs correctly and writes the filtered ROIs
# In case FindEdges or another crucial metric was missing from the Measurements, it returns "aborted due to missing FindEdges"

def FilterZplane(accepted,rootAndsuffix,max_plane,writepath,**kwargs):
    """Input accepted      : dict from the accepted_rois.pkl file that was created from XY filtering
       Input rootAndsuffix : tuple with two elements, first str indicating rootname, second str indicating suffix.
       Input max_plane     : number indicating the maximum planes a brain ID can have
       Input writepath     : the particular path str that includes the root name of a specific brain ID. Will be used for writing the zip file to this path."""

    # values will be default unless the user has typed some
    ratio_intersecting = kwargs.get('ratio_intersecting')
    one_to_1_engulf_size_threshold = kwargs.get('one_to_1_engulf_size_threshold')
    one_to_1_engulfed_intersection_threshold = kwargs.get('one_to_1_engulfed_intersection_threshold')
    negligible_1to1_iou = kwargs.get('negligible_1to1_iou')
    minimum_1to1_intersection = kwargs.get('minimum_1to1_intersection')
    minimum_1to1_size_difference = kwargs.get('minimum_1to1_size_difference')
    minimize_factor = kwargs.get('minimize_factor')
    marginal_iou = kwargs.get('marginal_iou')
    minimum_intersection_to_consider_engulfed = kwargs.get('minimum_intersection_to_consider_engulfed')
    overall_intersecting_ratio = kwargs.get('overall_intersecting_ratio')
    proximity_threshold = kwargs.get('proximity_threshold')
    iou_threshold = kwargs.get('iou_threshold')
    minimize_factor2 = kwargs.get('minimize_factor2')

    name,suffix = rootAndsuffix                                                                                        # this is a tuple that has the root name (up to _ome_plane without N) as 1st element and the extension like .tif as 2nd


    def FindAllOverlaps ():
        """For every ROI, finds its overlaps across all planes.
        Returns a defaultdict with str roinames as keys and a list as default value.
        The list contains names of overlaps.
        It is required that the names of the same brain images are the same except for planeN in the end."""

        idx         = index.Index()
        polygons    = {}      
        id_counter  = 0

        for plane in range(1,max_plane+1):
            imagename = f"{name}{plane}{suffix}"
            try :
                rois = accepted[plane][imagename]                                                
            except KeyError :
                print (f"Brain {name} stops at plane {plane-1} ")
                # this can also be logged !!!
                break                                                                             # for instance, if a brain ID cannot be found in plane6, then there is no reason to look in plane 7
                
            for roiname, data in rois.items():                                                    # The structure is roiname as key and then measurements of the roi is the value
                poly = data.get('polygon')                                                        # polygon is one of the measuremennts/info
                if poly is None:
                    continue
                try:                                                                              # this is to repair shapes with invalid geometry
                    if not poly.is_valid:
                        poly = poly.buffer(0)
                    if not poly.is_valid or poly.is_empty:
                        continue

                    polygons[id_counter] = {'plane': plane,'roiname': roiname,'polygon': poly}
                    idx.insert(id_counter, poly.bounds)                                         # using the idx to accelerate finding of overlaps later
                    id_counter += 1

                except GEOSException:                                                           # if shapes cannot be fixed, then just continue...
                    continue

        # Second phase : Query R-tree and group all overlaps per ROI
        
        overlap_dict = defaultdict(list)                                                        # Keys will be roinames and value a list with all roinames that display overlap with the key                                               

        for i, data_i in polygons.items():
            poly_i = data_i['polygon']
            for j in idx.intersection(poly_i.bounds):                                           # First check with bounding box
                if i >= j:                                                                      # if pair 0,1 has been tested, there's no reason to test ids 1,0 later
                    continue

                data_j = polygons[j]
                poly_j = data_j['polygon']

                try:
                    if poly_i.intersects(poly_j):                                               # eventually we test for real intersection here
                        key_i = data_i['roiname']
                        key_j = data_j['roiname']
                        overlap_dict[key_i].append(key_j)
                        overlap_dict[key_j].append(key_i)
                except GEOSException:
                    continue
        
        return overlap_dict

    def GetRoiPlane(roiname):
        """Returns the plane number a roi belongs to"""
        
        return int (roiname[roiname.rfind("-")+1:])

    def GetRoiImageName (roiname, extension = suffix ):
        """Returns the str corresponding to the particular image the roi was generated based on"""
        # The extension changed from the fixed .tif to suffix for flexibility
        plane = roiname[roiname.rfind("-")+1:]
        reconstructed_name = name + plane + extension
        return reconstructed_name
    
    def CalculateEngulf(main_polygon,second_polygon, ratio_intersecting=ratio_intersecting, booltype = True):
        """Input main polygon   : shapely polygon
        Input second polygon : shapely polygon 
        ratio_intersecting   : float
        boolytype            : boolean
        
        Calculates extent of engulf but really depends on the booltype. 
        If booltype is True :
        Then it checks whether the second polygon intersects significantly (ratio_intersecting) 
        with the first. If so, returns True. If not returns False.
        If booltype if False:
        Then it checks the extent to which the second polygon is part of the main polygon.
        This is usefull for cases where an enlongated dim ROI is erroneously detected as one
        by virtue of the halo of two or more adjacent. It returns a float which is the ratio 
        that the second polygon occupies space inside the main. 
        """
        
        if booltype == True :
            second_polygon_intersection = second_polygon.intersection(main_polygon)
            if second_polygon_intersection.area / second_polygon.area > ratio_intersecting:
                return True
            else :
                return False
        
        if booltype == False :
            main_polygon_intersection = main_polygon.intersection(second_polygon).area                           # here we see how much the main overlaps to the second. Then we convert to ratio below
            return main_polygon_intersection / main_polygon.area           

    def DetectionOfEngulfers(testingPolygon,lista,already_marked, one_to_1_engulf_size_threshold=one_to_1_engulf_size_threshold, one_to_1_engulfed_intersection_threshold=one_to_1_engulfed_intersection_threshold):
        """ Input testingPolygon                           : shapely polygon
            Input lista                                    : list with all roinames (str) overlapping with each other
            Input already_marked                           : list with roinames (str) that are already marked for removal
            Input one_to_1_engulf_size_threshold           : float indicating ratio in size difference between two ROIs
            Input one_to_1_engulfed_intersection_threshold : float indicating extent to which a roi's body is inside another 
            
            Output : True, meaning that the testingPolygon (main polygon) will be rejected or False, meaning it will survive.
            
            Detects ROIs that engulf other ROIs. Usually, these are just dimmer and larger versions of smaller, crisp neurons
            originating from another plane."""
        roi_and_poly:list = []
        for roiname in lista :
            plane = GetRoiPlane (roiname)
            image = GetRoiImageName(roiname)
            if roiname in already_marked:                                                                          # we dont want to include again rois that have been marked for deletion because if 3 planes are adjacent and shapes are same, they will all cancel each other out
                continue
            roi_and_poly.append(accepted[plane][image][roiname]['polygon'])

        boolresults = [CalculateEngulf(testingPolygon, x) for x in roi_and_poly[:]]                                # every time a significant engulf is detected a True will be returned. 

        if boolresults.count(True) >= 2:                                                                           # if there are at least two significantly engulfed ROIs by the testingPolygon (this is the main polygon, by main it means the key roiname that we test)              
            return True
        
        if boolresults.count(True) == 1:                                                                           # if there is only one engulfed, we still have to test whether the engulfer is much larger. If not, then we won't further process it in this function, since it is to be checked in FilterAdjacent1to1Overlaps.              
            overlpr_poly = roi_and_poly[boolresults.index(True)]                       
            if (overlpr_poly.area * one_to_1_engulf_size_threshold < testingPolygon.area):                
                if overlpr_poly.intersection(testingPolygon).area >= one_to_1_engulfed_intersection_threshold :    # If the engulfed is significantly smaller and is virtually inside the large one, then we remove the engulfer, as it is probably a halo reflection of the crisp/small version. Aanother condition can be added here for findedges although the size ratio is large enough to ensure that the smalle is the crisper
                    return True
        else :
            return False
        
    def ExclusionOfEngulfers():
        """ Output : list with roinames that have already been deleted from all overlaps in this function right before the return.
            Calls functions to detect engulfers and finally exclude them from all overlaps. At this stage, the exclusion is only in the keys
            of all overlaps and not the values yet."""
        engulfers_to_delete = []
        for potential_engulfer in all_overlaps:
            pe_plane = GetRoiPlane(potential_engulfer)
            pe_image = GetRoiImageName(potential_engulfer)
            pe_polyg = accepted[pe_plane][pe_image][potential_engulfer]['polygon']                                # this is the testingPolygon in the functions called afterwards
            
            if DetectionOfEngulfers(pe_polyg, all_overlaps[potential_engulfer],engulfers_to_delete) == True:
                engulfers_to_delete.append(potential_engulfer)
        
        for verified_engulfer in engulfers_to_delete:
            del(all_overlaps[verified_engulfer])                                                                  # we remove all engulfers from all overlaps

        return engulfers_to_delete

    def GetAllRoinames():
        """Output : dict with roiname as key and value a list with the plane it belongs to (str) and the imagename it originates (str)
        For ALL ROIs, creates a respective key where plane and imagename is saved inside a list."""
        allroinames = {}
        for plane, image in accepted.items():                                                  # test how this works after making this module flexible to work with different number of plane per brain (having set a max_plane number which is the maximum POSSIBLE number of plane) Brains with less planes will not exist in the latest numbers but this should just yield empty dicts
            imagename = f"{name}{plane}{suffix}"
            rois = image.get(imagename, {})
            for roi in rois :
                allroinames[roi] = [plane,imagename]

        return allroinames

    def WriteROIs (writepath):

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as roi_zip:
            for finalROI in allROInames.keys():
                if finalROI in finalROIs:
                    roiplane, roiname = GetRoiPlane(finalROI), GetRoiImageName(finalROI)
                    poly = accepted[roiplane][roiname][finalROI]['polygon']
                    poly = np.array(poly.exterior.coords[:-1])                                  # Remove duplicate last point if needed
                    roi = ImagejRoi.frompoints(poly)
                    roi.name = finalROI                                                    
                    roi_bytes = roi.tobytes()                                                   # Convert ROI to bytes (instead of saving to file)
                    roi_filename = f"{finalROI}.roi"
                    roi_zip.writestr(roi_filename, roi_bytes)                                   # Write directly to the zip archive

        zip_filename_ = writepath + ".zip"                                                      # save the zip file to disk at the end
        with open(zip_filename_, "wb") as f:
            f.write(zip_buffer.getvalue())
        
    def Separate1to1MatchesAnd1toMore (dict_with_overlaps_in_list):
        """Input  : The 'accepted' dictionary. See its architecture description elsewhere.
        Merely seperates all overlaps to different dictionaries.
        Namely : one overlapping with one
                    one overlapping with more
                    one not overlapping with any (standalone)"""

        one_to_one :dict = {}                                                                                                    # one to one for two planes only, it is always possible that 2nd plane still overlaps with 3rd. The filtering always works in couples only (and can continue in another iteration with 2-3 if 3 exists)
        one_to_more:dict = {}
        standalone_rois  = {}

        for roiname, lista in dict_with_overlaps_in_list.items():
            if len (lista) == 1 :
                one_to_one[roiname] = lista[0]
            elif len(lista) > 1:
                one_to_more[roiname] = lista
            else :
                standalone_rois[roiname] = 'standalone'

        return one_to_one,one_to_more,standalone_rois

    def FilterAdjacent1to1Overlaps (one_to_one, negligible_1to1_iou=negligible_1to1_iou, minimum_1to1_intersection=minimum_1to1_intersection, minimum_1to1_size_difference=minimum_1to1_size_difference, minimize_factor=minimize_factor, marginal_iou=marginal_iou):
        """Read the decision tree in the documentation for complete understanding
        input one_to_one : dict with roinames as keys and roinames as values"""
        
        excluded:dict  = {}
        included:dict  = {}

        for roiname, overlap in one_to_one.items():                                                                             # This is a later-stage comment but must be valid : roiname and overlap are both roinames. The first is the basic roiname we are testing and the second the overlappng one. 
            pln = GetRoiPlane (roiname)
            im  = GetRoiImageName (roiname)
            ovplan= GetRoiPlane(overlap)
            ovimg = GetRoiImageName (overlap)
            intersection = accepted[pln][im][roiname]['polygon'].intersection(accepted[ovplan][ovimg][overlap]['polygon']).area 
            union        = accepted[pln][im][roiname]['polygon'].union(accepted[ovplan][ovimg][overlap]['polygon']).area
            iou          = intersection / union
            
            if iou < negligible_1to1_iou:
                included[roiname] = f'overlapping with low iou {iou} with {overlap} '
                # the overlap will be present as roiname later in the loop
                continue

            if accepted[pln][im][roiname]['Area'] >= accepted[ovplan][ovimg][overlap]['Area'] :                                 # Find which of the two is the largest one and name it as large
                large,smaller = roiname,overlap
                large_plane   = pln
                large_image   = im
                small_plane   = ovplan
                small_image   = ovimg 
            elif accepted[pln][im][roiname]['Area'] < accepted[ovplan][ovimg][overlap]['Area'] :
                large,smaller = overlap,roiname
                large_plane   = ovplan
                large_image   = ovimg
                small_plane   = pln
                small_image   = im  

            
            small_polygon, large_polygon  = accepted[small_plane][small_image][smaller]['polygon'], accepted[large_plane][large_image][large]['polygon']
            small_to_large_intrsct        = small_polygon.intersection(large_polygon)
            area_of_small                 = accepted[small_plane][small_image][smaller]['Area']
            area_of_large                 = accepted[large_plane][large_image][large]['Area']

            try :
                lista = [accepted[pln][im][roiname]['FindEdgesStdDev'],accepted[ovplan][ovimg][overlap]['FindEdgesStdDev']]         # find which object has the best metric score to subsitute the other
            except KeyError:
                er_msg = "You have (most likely) forgot to add the FindEdgesStdDev measurement to your main save folder before XY filtering." \
                         " Please include FindEdgesStdDev to your main measurements and re-run XY filtering. Then you can try Z-filtering again." \
                         " Make sure that you provide the new Accepted_ROIs.pkl file.\n\n" \
                         "It is also possible that Area measurement was not checked in the set measurements of Fiji while obtaining the first measurements." \
                         " If the error persists, investigate the Zfilter.py"
                Checks.ShowError("A metric could not be found",er_msg)
                return "FindEdgesStdDev_missing_from_main_save_folder","aborting_procedure"
            
            index = lista.index(max(lista))


            if small_to_large_intrsct.area / area_of_small > minimum_1to1_intersection :                                        # if the body of the small roi is significantly inside the body of the large
                
                if area_of_small / area_of_large > minimum_1to1_size_difference :                                               # and the small roi is not very small relative to the large one (if it was, it could be that we are looking on an edge of the same object due to different plane - we dont want to differentiate there)
                    if index == 0 :
                        excluded[overlap] = f'excluded by metric comparison inside the significant intersection condition'
                        included[roiname] = f'included by metric comparison inside the significant intersection condition'
                    elif index == 1:
                        excluded[roiname] = f'excluded by metric comparison inside the significant intersection condition'
                        included[overlap] = f'included by metric comparison inside the significant intersection condition'
                
                else :                                                                                                          # if the small roi is significantly smaller. We will first see whether the small roi's center is close to the large roi's center, by minimizing the small one and testing whether the large roi centerpoint in inside the minimized version. If so, we will measure with findedges to find the most crisp
                    # I can add FeretAngle here too.                                                                            # The dimmest&largest version of the small crisp should reflect the feretangle direction                                                                                                           
                    try:
                        small_cent = small_polygon.centroid
                        large_cent = large_polygon.centroid                                                                  
                        minimized_small = scale (small_polygon,xfact=minimize_factor,yfact=minimize_factor,origin=small_cent)   # minimizing the small roi to create something like a kernel version of it and see whether the center of the large lies within
                    except :
                        print (f"Could not minimize the small ROI {smaller} which is found inside {large} or one poly is wrong")
                        print ( f"This might lead to erroneous estimation of the more crisp version along planes")
                    else :
                        try :
                            do_centers_overlap = minimized_small.covers(large_cent)
                        except : 
                                print (f"Could not check for an overlap between {smaller} and {large} center points")
                                print (f"This is probably an error occuring from a badly shaped polygon")
                                do_centers_overlap = False                                                                      # do_centers overlap will be defined here for the first time in case of an exception to prevent error in the next if command
                            

                    # consider adding feretangle here too
                    if do_centers_overlap == True :                                                                             # if the center of the large roi is included in the minimized version of the small roi, then use the findedges measurement as usual
                        if index == 0 :
                            excluded[overlap] = f'excluded by metric comparison inside the significant intersection condition'
                            included[roiname] = f'included by metric comparison inside the significant intersection condition'
                        elif index == 1:
                            excluded[roiname] = f'excluded by metric comparison inside the significant intersection condition'
                            included[overlap] = f'included by metric comparison inside the significant intersection condition'

                    else :                                                                                                      # if the small roi (after minimized) does not include the center point of the large, then just exclude it, as it is likely-not certainly though-a smaller part of the large one
                        excluded [smaller] = 'excluded due to high overlap inside a larger one'                                     
                        included [large]   = 'included as a large one that is engulfing a smaller one' 

            elif iou >= marginal_iou :                                                                                          # if iou is high enough, chances are that it is the same neuron. Center point could possible be used too here                                                                    
                if index == 0 :
                    excluded[overlap] = 'excluded by metric comparison'
                    included[roiname] = 'included by metric comparison'
                elif index == 1:
                    excluded[roiname] = 'excluded by metric comparison'
                    included[overlap] = 'included by metric comparison'
            
            elif iou < marginal_iou :
                if accepted[pln][im][roiname]['Area'] >= accepted[ovplan][ovimg][overlap]['Area'] :
                    large,smaller = roiname,overlap
                elif accepted[pln][im][roiname]['Area'] < accepted[ovplan][ovimg][overlap]['Area'] :
                    large,smaller = overlap,roiname

                    included[large]   = 'included and overlapping'
                    included[smaller] = 'included and overlapping'


        return included, excluded

    def ClearEngulfersFromDictValues(engulfers):
        """Clears the elements with roinames of the engulfers from lists which are values in all_overlaps """
        for engulfer in engulfers :
            for survivoroi, its_overlaps in all_overlaps.items():
                if engulfer in its_overlaps :
                    all_overlaps[survivoroi].remove(engulfer)

    def AddStandalonesToFinalROIs():
        """Adds the ROIs that do not overlap with any (standalones) to the finalROIs"""
        for standalone in standalones:
            finalROIs[standalone] = 'Ended up standalone'

    def ExclusionOf1to1Overlaps():
        """Deletes from all_overlaps the ROIs that have been excluded from FilterAdjacent1to1Overlaps"""
        for excluded_roi in oneto1_excluded:
            del(all_overlaps[excluded_roi])

    def AddThoseNeverRegisteredInall_overlapsToFinalROIs():
        """Adds the rois that were standalones from the first place to the final ROIs.
        These might have not been captured because we mainly operate based on all_overlaps to produce finalROIs
        but standalones by default dont have overlaps."""
        for oneroi in allROInames:
            if oneroi not in first_stage_all_overlaps :
                finalROIs[oneroi] = 'direct standalone from the start'

    def IOU(one_roi,anotheroi):
        """ Input one_roi : str
            Input antheroi: str
            Output        : tuple with float as 1st element and str indicating a second roiname as second element
            Finds the IOU between two ROIS"""
        pl, img       = GetRoiPlane(one_roi), GetRoiImageName(one_roi)
        ovplane,ovimg = GetRoiPlane(anotheroi),GetRoiImageName(anotheroi)
        intersection  = accepted[pl][img][one_roi]['polygon'].intersection(accepted[ovplane][ovimg][anotheroi]['polygon']).area   # by default, since we never looped through the second plane for overlaps, the roiname is from plane1 and overlaps from plane2
        union         = accepted[pl][img][one_roi]['polygon'].union(accepted[ovplane][ovimg][anotheroi]['polygon']).area
        iou           = intersection / union

        return (iou,anotheroi)

    def FilterOnetoMoreOverlaps(iou_threshold=iou_threshold, proximity_threshold=proximity_threshold, minimize_factor2=minimize_factor2, overall_intersecting_ratio=overall_intersecting_ratio, minimum_intersection_to_consider_engulfed=minimum_intersection_to_consider_engulfed):
        """Input iou_threshold                             : float indicating threshold for iou between two ROIs
        Input proximity_threshold                       : int indicating proximity in terms of planes where ROIs originate from
        Input minimize_factor                           : float dictating what the minimize ratio of a ROI will be
        Input overall_intersecting_ratio                : float indicating the minimum total intersection that a large ROI displays with other ROIs
        Input minimum_intersection_to_consider_engulfed : float indicating the minimum intersection of a ROI with another, so that it is considered as a ROI significantly intersecting with it 
        Output : dictionary with roinames as str and value a string indicating the condition of acceptance.
        Read the documentation for understanding of the decision tree"""
        

        to_add_to_finalROIs = {}
        to_exclude = {}

        for overlapping_with_many, list_with_its_overlaps in onetoMore_unfiltered.items():
            main_plane= GetRoiPlane(overlapping_with_many)
            main_img = GetRoiImageName(overlapping_with_many)
            metric_scores = {overlapping_with_many: accepted[main_plane][main_img][overlapping_with_many]['FindEdgesStdDev']}
            main_poly     = accepted[main_plane][main_img][overlapping_with_many]['polygon']
            main_area     = main_poly.area
            copied_overlaps = list_with_its_overlaps [:]
            copied_overlaps = [o for o in copied_overlaps if accepted[GetRoiPlane(o)][GetRoiImageName(o)][o]['polygon'].intersection(main_poly).area > minimum_intersection_to_consider_engulfed]   # there is still a chance that a roi that engulfs two and is actually created by their halo is smaller than a fourth roi which forms overlap with it. This chance is significantly reduced here, whereby we remove small ROIs that do not belong by large inside the main engulfer.
            
            if len(copied_overlaps) >=2 :                                                                                                                                                           # here we want to capture the case that a large roi is engulfing two rois because it is the halo of the other two. Sometimes this cannot be captured in the engulfers function because the engulfer is actually not covering all the part of the engulfed ones
                if main_area > max ([accepted[GetRoiPlane(o)][GetRoiImageName(o)][o]['polygon'].area for o in copied_overlaps]):                                                                    # we first need to verify that the main polygon is indeed the larger one. Otherwise it cannot be an engulfer. Thereby, its area must be larger than the max area of all ROIs overlapping significantly (more than minimum_intersection_to_consider_engulfed)
                    overlapolygons:list = []
                    for an_overlap in copied_overlaps:
                        ove_plane   = GetRoiPlane     (an_overlap)
                        ove_img     = GetRoiImageName (an_overlap)
                        ovrlp_poly  = accepted[ove_plane][ove_img][an_overlap]['polygon']
                        overlapolygons.append(ovrlp_poly)

                    overall_intersecting_area_of_main_poly    = sum([CalculateEngulf(main_poly, x, booltype=False) for x in overlapolygons[:]])                                                     # mind that the booltype is False, thereby, a list with ratios corresponding to the extent that the engulfer's body is overlapping with smaller bodies is returned here and the sum is taken                                              # the result here is a ratio, not a raw area. How much of the main large roi is in total found inside other rois
                    if overall_intersecting_area_of_main_poly > overall_intersecting_ratio :                                                                                                        # this means that the large is mostly part of the smallest ROIs. It comprises the smallest
                        to_exclude[overlapping_with_many]     = 'Overlapping with at least two and probably a mere result of their z-distant halo. Hence excluded'
                        continue

            for one_overlap in list_with_its_overlaps:
                ov_plane,ov_image = GetRoiPlane(one_overlap),GetRoiImageName(one_overlap)
                metric_scores[one_overlap] = accepted[ov_plane][ov_image][one_overlap]['FindEdgesStdDev']
            
            max_key = max(metric_scores, key=metric_scores.get)
            max_key_plane = GetRoiPlane(max_key)
            
            if max_key_plane == overlapping_with_many :
                to_add_to_finalROIs[overlapping_with_many] = 'added due to its clarity. Overlapping with at least 2'
                #excluded here? depends on overlap extent
            
            elif abs(max_key_plane - main_plane) > proximity_threshold :
                to_exclude[overlapping_with_many] = 'Overlapping with at least two but not proximal to the crisp one'
            
            else :
                dic_with_ious ={}
                for one_overlap in list_with_its_overlaps:
                    dic_with_ious[one_overlap] = IOU(overlapping_with_many,one_overlap)
                maximum_overlap = max(dic_with_ious.values(), key = lambda x: x[0])
                
                if maximum_overlap[0] < iou_threshold :
                    to_add_to_finalROIs[overlapping_with_many] = f'overlapping with at least two. Did not surpass iou threshold {iou_threshold} '
                
                else :
                    max_ov_pln= GetRoiPlane(maximum_overlap[1])
                    max_ov_img= GetRoiImageName(maximum_overlap[1])
                    ov = maximum_overlap[1]

                    if accepted[main_plane][main_img][overlapping_with_many]['Area'] >= accepted[max_ov_pln][max_ov_img][ov]['Area'] :
                        large,smaller = overlapping_with_many, ov
                        large_plane   = main_plane
                        large_image   = main_img
                        small_plane   = max_ov_pln
                        small_image   = max_ov_img
                    elif accepted[main_plane][main_img][overlapping_with_many]['Area'] < accepted[max_ov_pln][max_ov_img][ov]['Area'] :
                        large,smaller = ov,overlapping_with_many
                        large_plane   = max_ov_pln
                        large_image   = max_ov_img
                        small_plane   = main_plane
                        small_image   = main_img 

            
                    small_polygon, large_polygon  = accepted[small_plane][small_image][smaller]['polygon'], accepted[large_plane][large_image][large]['polygon']
                    lista = [accepted[main_plane][main_img][overlapping_with_many]['FindEdgesStdDev'],accepted[max_ov_pln][max_ov_img][ov]['FindEdgesStdDev']]                        # find which object has the best metric score to subsitute the other
                    index = lista.index(max(lista))

                    try:
                        small_cent = small_polygon.centroid
                        large_cent = large_polygon.centroid                                                                  
                        minimized_small = scale (small_polygon,xfact=minimize_factor2,yfact=minimize_factor2,origin=small_cent)   # minimizing the small roi to create something like a kernel version of it and see whether the center of the large lies within
                    except :
                        print (f"Could not minimize the small ROI {smaller} which is found inside {large} or one poly is wrong")
                        print ( f"This might lead to erroneous estimation of the more crisp version along planes")
                    else :
                        try :
                            do_centers_overlap = minimized_small.covers(large_cent)
                        except : 
                                print (f"Could not check for an overlap between {smaller} and {large} center points")
                                print (f"This is probably an error occuring from a badly shaped polygon")
                                do_centers_overlap = False                                                                      # do_centers overlap will be defined here for the first time in case of an exception to prevent error in the next if command
                            
                    # consider adding feretangle here too
                    if do_centers_overlap == True :  
                        if index == 0 :
                            to_exclude[ov] = f'excluded by metric comparison as an overlap of a roi that overlaps with at least two'
                            to_add_to_finalROIs[overlapping_with_many] = f'included by metric comparison. Overlapping with more than two'
                        elif index == 1:
                            to_exclude[overlapping_with_many] = f'excluded by metric comparison. Overlapping with more than two'
                            to_add_to_finalROIs[ov] = f'included by metric comparison. Overlapping with more than two'

                    else :                                                                                                      # if the small roi (after minimized) does not include the center point of the large, then just exclude it, as it is likely-not certainly though-a smaller part of the large one
                        to_add_to_finalROIs[overlapping_with_many] = 'included - overlapping with more than two, but not belonging to one'


        return to_add_to_finalROIs



    finalROIs                                          = {}
    allROInames                                        = GetAllRoinames()
    all_overlaps                                       = FindAllOverlaps()
    first_stage_all_overlaps                           = copy.deepcopy(all_overlaps)
    excluded_engulfers                                 = ExclusionOfEngulfers()
    _                                                  = ClearEngulfersFromDictValues(excluded_engulfers)
    oneto1_unfiltered,onetoMore_unfiltered,standalones = Separate1to1MatchesAnd1toMore(all_overlaps)
    oneto1_included, oneto1_excluded                   = FilterAdjacent1to1Overlaps(oneto1_unfiltered)
    if oneto1_excluded == 'aborting_procedure': 
        return "aborted due to missing FindEdges"                                                        # in case the FindEdgesStdDev is missing from measurements
    _                                                  = ExclusionOf1to1Overlaps()
    _                                                  = AddStandalonesToFinalROIs()
    _                                                  = AddThoseNeverRegisteredInall_overlapsToFinalROIs()
    onetoMore_included                                 = FilterOnetoMoreOverlaps ()

    finalROIs.update(oneto1_included)
    finalROIs.update(onetoMore_included)
    # One more function can be added here, aimed to filter out neurons of similar size that have high IOU. There are a few cases like this.

    WriteROIs(writepath)
 

if __name__ == "__main__":
    FilterZplane()