import ij.IJ
import ij.ImagePlus
import ij.gui.PointRoi
import ij.gui.Roi
import ij.plugin.frame.RoiManager
import java.awt.Rectangle
import java.awt.Polygon

// Get current image and ROI Manager
ImagePlus imp = IJ.getImage()
RoiManager roiManager = RoiManager.getRoiManager()
if (roiManager == null) {
    IJ.showMessage("Error", "Open the ROI Manager first.")
    return
}

// Retrieve all ROIs
Roi[] rois = roiManager.getRoisAsArray()
if (rois.length == 0) {
    IJ.showMessage("Error", "No ROIs found in the ROI Manager.")
    return
}

// Collect unique points from all ROIs
Set<String> uniquePoints = new HashSet<>()
List<Integer> xPoints = new ArrayList<>()
List<Integer> yPoints = new ArrayList<>()

for (Roi roi : rois) {
    if (roi instanceof PointRoi) {
        // Handle multi-point ROIs
        PointRoi pr = (PointRoi) roi
        Rectangle bounds = pr.getBounds()
        for (int i = 0; i < pr.getNCoordinates(); i++) {
            int x = pr.getXCoordinates()[i] + bounds.x
            int y = pr.getYCoordinates()[i] + bounds.y
            String key = x + "," + y
            if (uniquePoints.add(key)) {
                xPoints.add(x)
                yPoints.add(y)
            }
        }
    } else {
        // Handle all other ROI types (polygons, rectangles, ellipses, etc.)
        Polygon poly = roi.getPolygon()
        for (int i = 0; i < poly.npoints; i++) {
            int x = poly.xpoints[i]
            int y = poly.ypoints[i]
            String key = x + "," + y
            if (uniquePoints.add(key)) {
                xPoints.add(x)
                yPoints.add(y)
            }
        }
    }
}

// Create a new multi-point ROI with all vertices
PointRoi allPointsRoi = new PointRoi(
    xPoints.stream().mapToInt(i -> i).toArray(),
    yPoints.stream().mapToInt(i -> i).toArray(),
    xPoints.size()
)

// Generate the convex hull
imp.setRoi(allPointsRoi)
IJ.run("Convex Hull")
Roi convexHull = imp.getRoi()

// Add convex hull to ROI Manager and clean up
if (convexHull != null) {
    roiManager.addRoi(convexHull)
    imp.killRoi() // Remove temporary points from image
    roiManager.select(roiManager.getCount() - 1) // Select the new hull
    IJ.showStatus("Convex hull created from " + rois.length + " ROIs")
} else {
    IJ.showMessage("Error", "Convex hull creation failed.")
}