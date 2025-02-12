import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import fullcontrol as fc
from projectiondot import GetProjectionDot, PlotMeshAndPointsAndTrajectories, PlotPoints
from trajectoryplanner import PlanTrajectory45Degree
from stlprocessor import CreateMesh, GetPlaneEquationDot, PlotMesh, MeshTranslate, MeshScale, MeshTranslateOrigin, SplitSTLSurfaces
from circular_trajectory import PlanCircularTrajectory
import numpy as np
import matplotlib.pyplot as plt
from stl import mesh as mesh_module
import time
import pandas as pd

def split_array_on_x_decrease(array: np.ndarray):
    """
    Split the array whenever x decreases, create a bunch of subarrays with only increasing x values
    -array: input array
    """
    # Find the indices where x suddenly decreases
    indices = np.where(array[1:, 0] < array[:-1, 0])[0] + 1

    # Split the array based on these indices
    splits = np.split(array, indices )

    return splits

def AddLayer(steps: list, layerheight: float):
    """
    Add a layer at the same x and y coordinates, but shift everything up by a certain layer height
    -steps: list of array of points
    -layerheight: height to shift the z coordinate of each point by
    """
    return [element + np.array([0,0,0.4]) for element in steps]

def MoveUpAndBack(initial_point: np.ndarray, final_point: np.ndarray, steps: list, height: float):
    """
    Move from the final point back to the initial point by first going up and then moving back across the print
    -initial point: first point to move back to, 1x3 array
    -final point: the point you ended that we need to move from, 1x3 array
    -height: how high above the final point to move
    
    """

    steps.extend(fc.travel_to(fc.Point(x = final_point[0], y = final_point[1], z= final_point[2] + height)))
    steps.extend(fc.travel_to(fc.Point(x = initial_point[0], y = initial_point[1], z = initial_point[2] + height)))
    steps.extend(fc.travel_to(fc.Point(x = initial_point[0], y = initial_point[1], z = initial_point[2])))

    return steps

def HoleCheck(point1: np.ndarray, point2: np.ndarray, base_dist:float, factor:float, steps:list):
    """
    Check each point for a whole, returns the steps in gcode where any points with too large distance in between are removed
    -point1: initial point
    -point2: point to travel to
    -base_dist: base distance from point to point
    -factor: relaxation factor on base_dist, critical distance will be factor*base_dist
    -steps: list to append all the gcode points to
    
    """
    try: 
        dist = np.linalg.norm(point2 - point1)

        #If distance between points is too large, move to the point, not extrude
        if dist > factor*base_dist:
            return steps.extend(fc.travel_to(fc.Point(x = point2[0], y = point2[1], z = point2[2])))
        else: 
            return steps.append(fc.Point(x = point2[0], y = point2[1], z = point2[2]))
    except: 
        return 

def ExportHoleCheck(steps: list, steps_p: list, layers: int, layer_height: float):
    """
    Export HoleCheck points to a gcode and plot
    -steps: initial fc formatted steps for infill
    -steps_p: fc formatted steps for perimeter
    -layers: n of layers of infill
    -layer_height: layer height for infill
    """
    p0 = steps[1]
    p1 = steps[-1]
    steps = steps[2:]
    steps += fc.travel_to(fc.relative_point(p1, 0, 0, 40)) + fc.travel_to(fc.relative_point(p0, 0, 0, 40)) + fc.travel_to(fc.relative_point(p0,0, 0, 0))#Move back to initial point for second layer
    steps_layered = fc.move(steps, fc.Vector(z=layer_height), copy=True, copy_quantity=layers)
    steps_p_layered = steps_p + fc.travel_to(fc.relative_point(steps_p[-2], 0, 0, 40)) + fc.travel_to(fc.relative_point(p0, 0, 0, 40)) + fc.travel_to(fc.relative_point(p0, 0, 0, 0)) + steps_layered
    
    #Prepare, print, and show the gcode      
      
    filename = 'nonplanar'
    printer = 'generic' 
    # printer options: generic, ultimaker2plus, prusa_i3, ender_3, cr_10, bambulab_x1, toolchanger_T0, toolchanger_T1, toolchanger_T2, toolchanger_T3
    print_settings = {'extrusion_width': 0.5,'extrusion_height': 0.2, 'nozzle_temp': 210, 'bed_temp': 40, 'fan_percent': 100}
    # 'extrusion_width' and 'extrusion_height' are the width and height of the printed line)
    fc.transform(steps_p_layered, 'plot')
    fc.transform(steps_p_layered, 'gcode', fc.GcodeControls(printer_name=printer, save_as=filename, initialization_data=print_settings))

def ExportGCode(steps: list, steps_p: list, layer_height: float, layers: int):

    p0 = steps[1]
    p1 = steps[-1]

    steps += fc.travel_to(fc.relative_point(p1, 0, 0, 40)) + fc.travel_to(fc.relative_point(p0, 0, 0, 40)) + fc.travel_to(fc.relative_point(p0,0, 0, 0))#Move back to initial point for second layer

    steps_layered = fc.move(steps, fc.Vector(z=layer_height), copy=True, copy_quantity=layers)
    #Add perimeter steps
    steps_p_layered = steps_p + fc.travel_to(fc.relative_point(steps_p[-2], 0, 0, 40)) + fc.travel_to(fc.relative_point(steps_layered[0], 0, 0, 40)) + fc.travel_to(steps_layered[0]) + steps_layered
            
    time_formatted = time.time()
    print("Points Formatted into FC, Time = ", time_formatted - time_projection)

    #Prepare, print, and show the gcode      
            
    filename = 'nonplanar'
    printer = 'generic' 
    # printer options: generic, ultimaker2plus, prusa_i3, ender_3, cr_10, bambulab_x1, toolchanger_T0, toolchanger_T1, toolchanger_T2, toolchanger_T3
    print_settings = {'extrusion_width': 0.4, 'extrusion_height': 0.2, 'nozzle_temp': 210, 'bed_temp': 40, 'fan_percent': 100}
    #relative_e / nozzle_temp / bed_temp / fan_percent / print_speed_percent / material_flow_percent / primer
    
    # 'extrusion_width' and 'extrusion_height' are the width and height of the printed line)

    fc.transform(steps_p_layered, 'plot')
    fc.transform(steps_p_layered, 'gcode', fc.GcodeControls(printer_name=printer, save_as=filename, initialization_data=print_settings))

    time_gcode = time.time()
    print("Points Made into Gcode and Plot, Time = ", time_gcode - time_formatted)
    print("Net Time = ", time_gcode - time_zero)
    
    return

def plot_points_vectors_translated(initial_points, vectors, translated_vectors, translated_points):
    fig, axs = plt.subplots(2, 2, figsize=(12, 12))

    # Plot initial points
    axs[0, 0].scatter(initial_points[:, 0], initial_points[:, 1], c='blue')
    axs[0, 0].set_title('Initial Points')
    axs[0, 0].set_aspect('equal', 'box')

    # Plot vectors
    axs[0, 1].quiver(initial_points[:, 0], initial_points[:, 1], vectors[:, 0], vectors[:, 1], angles='xy', scale_units='xy', scale=1, color='red')
    axs[0, 1].set_title('Vectors')
    axs[0, 1].set_aspect('equal', 'box')

    # Plot translated vectors
    axs[1, 0].quiver(initial_points[:, 0], initial_points[:, 1], translated_vectors[:, 0], translated_vectors[:, 1], angles='xy', scale_units='xy', scale=1, color='green')
    axs[1, 0].set_title('Translated Vectors')
    axs[1, 0].set_aspect('equal', 'box')

    # Plot translated points
    axs[1, 1].scatter(translated_points[:, 0], translated_points[:, 1], c='purple')
    axs[1, 1].set_title('Translated Points')
    axs[1, 1].set_aspect('equal', 'box')

    plt.tight_layout()
    plt.show()

def GetPerimeter(trajectory_arrays: np.ndarray):
    """
    Get the Perimeter of the projected points, returns perimetery array containing the points with 2d coordinates, and then the corresponding z coordiantes
    -trajectory_arrays: nxnx3 array, formatted in the form of n trajectories, with n points with 3 coordinates. 
    """
    l = []
    r = []
    for i, t in enumerate(trajectory_arrays):
        if len(t)>1: 
            if i%2 == 0:
                l.append(t[0])
                r.append(t[-1])
            else:
                l.append(t[-1])
                r.append(t[0])
    

    s = np.concatenate((np.array(l)[::-1], np.array(r)))
    perimeter_array = s[:,:2] 
    return perimeter_array, s[:, -1]

    
def ScalePerimeter(trajectory_arrays:np.ndarray, extrusion_width:float):
    """
    Scale the perimeter of the projected points inwards, returns the scaled perimeter with x,y and z coordinates in one array
    -trajectory_arrays: nxnx3 array, formatted in the form of n trajectories, with n points with 3 coordinates. 
    -extrusion_width: how far to shift the perimeter inwards by
    """

    perimeter_array, z = GetPerimeter(trajectory_arrays = trajectory_arrays)
    z1 = z[:, np.newaxis]

    # Calculate centroid
    centroid = np.mean(perimeter_array, axis=0)
    
    # Calculate distances from centroid
    distances = np.linalg.norm(perimeter_array - centroid, axis=1)

    dv = perimeter_array - centroid
    magnitudes = np.linalg.norm(dv, axis=1)
    
    # Ensure magnitudes are non-zero
    non_zero_magnitudes = magnitudes.copy()
    non_zero_magnitudes[magnitudes == 0] = 1
    
    # Normalize vectors
    uv = dv / non_zero_magnitudes[:, np.newaxis]
    
    # Compute new points
    scaled_perimeter_array = centroid + (uv) * (distances - extrusion_width)[:, np.newaxis]
    scaled_perimeter_array = np.concatenate((scaled_perimeter_array, z1), axis = 1)

    #plot_points_vectors_translated(perimeter_array, dv, uv, scaled_perimeter_array)

    return scaled_perimeter_array


def BuildPerimeters(trajectory_arrays, nwalls, nlayers, layer_height, extrusion_width):
    """
    Final function to produce the gcode for the perimeters, scaled inwards, and then adding the layers. Final return is the gcode for the whole perimeters with layers and scalings included
    -trajectory_arrays: nxnx3 array, formatted in the form of n trajectories, with n points with 3 coordinates. 
    -nwalls: how many perimeter scalings to do
    -nlayers: how many vertical layers to do
    -layer_height: layer height of vertical layers
    -extrusion_width: how far to shift each perimeter inwards
    """
    perimeters = []
        
    for n in range(nwalls):
        current_width = (n+1)*extrusion_width
        p_scaled = ScalePerimeter(trajectory_arrays, current_width)
        perimeters.append(p_scaled)
        
    steps_perimeters = [fc.Point(x=point[0], y=point[1], z=point[2]) for p in perimeters for point in p]
    #MoveUpAndBack(perimeters[-1][0], perimeters[-1][-1], steps_perimeters, 5)

    steps_layered = fc.move(steps_perimeters, fc.Vector(z=layer_height), copy=True, copy_quantity=nlayers)
    

    return steps_layered, perimeters

def point_inside_polygon(point, perimeter):
    # Ensure the perimeter has at least 3 vertices
    if len(perimeter) < 3:
        raise ValueError("Perimeter must have at least 3 vertices")
    
    # Initialize counter for number of intersections
    num_intersections = 0
    
    # Iterate over each edge of the perimeter
    for i in range(len(perimeter)):
        # Define vertices of the edge
        p1 = perimeter[i]
        p2 = perimeter[(i + 1) % len(perimeter)]
        
        # Check if the ray intersects with the edge
        if (p1[1] > point[1]) != (p2[1] > point[1]) and \
           point[0] < (p2[0] - p1[0]) * (point[1] - p1[1]) / (p2[1] - p1[1]) + p1[0]:
            num_intersections += 1
    
    # Return True if number of intersections is odd, False otherwise
    return num_intersections % 2 == 1

if __name__ == "__main__":

    
    time_zero = time.time()

    #Get Mesh, Process it

    file_name = 'Test dep non planare\\camma.stl'
    my_mesh = CreateMesh(file_name)  
    my_mesh_vectors = MeshTranslateOrigin(np.array([300, 300]), my_mesh.vectors)
    arrnp, arrp, boolean_angles = SplitSTLSurfaces(my_mesh, my_mesh_vectors, max_height = 200, max_angle = np.pi/4, min_area = 0, save = True)
    time_separation = time.time()
    print("Time to Split Surfaces =", time_separation - time_zero)

    #Load the Mesh

    surface1 = mesh_module.Mesh.from_file('separated_stl_files\\non_planar_surface1.stl')
    time_load = time.time()
    print("Arrays Loaded, Time =", time_load - time_separation)

    ##Get Plane equations and trajectories

    n, Cen, d = GetPlaneEquationDot(surface1.units, surface1.centroids)
    xmax = 250
    xmin = 50
    ymax = 250
    ymin = 50
    spacing = .5
    resolution = .1
    #trajectories = PlanCircularTrajectory([xmin, xmax, ymin, ymax], z = 100, spacing = spacing, resolution = resolution, plot=False)    
    trajectories = PlanTrajectory45Degree([xmin, xmax, ymin, ymax], z = 100, spacing = spacing, resolution = resolution, plot=False)
    time_trajectories = time.time()
    print("Trajectories Loaded, Time =", time_trajectories - time_zero)

    #Extract the projected points for all points through iteration
    
    points = trajectories.reshape(-1,3)

    pl = []
    for i, point in enumerate(points):
        proj = GetProjectionDot(surface1.vectors, n, Cen, d, point)
        if proj is not None:
            pl.append(proj)

        if i%1000 == 0:
            print("Projecting")
            print(100*i/len(points))
    projected_points = np.array(pl)

    time_projection = time.time()
    print("Points Projected, Time = ", time_projection - time_trajectories)
                
    ##Formatting for the Gcode 

    ##Reorganize projected points so we don't go back across the whole print
    trajectory_arrays = split_array_on_x_decrease(projected_points) 
    trajectory_arrays = [trajectory[::-1] if i % 2 != 0 else trajectory for i, trajectory in enumerate(trajectory_arrays)] #Reorder trajectories to go smoothly from one to the next

    ##Perimeter Building, 
    nwalls = 1
    extrusion_width = .4
    layer_height = 0.2
    layers = 3

    steps_p, perimeters = BuildPerimeters(trajectory_arrays, nwalls = nwalls, nlayers = layers, layer_height = layer_height, extrusion_width= extrusion_width)
    final_p = ScalePerimeter(trajectory_arrays, extrusion_width*(nwalls+1))

    ##Now Isolate the points that belong to the infill
    infill_points = []
    for i, t in enumerate(trajectory_arrays):
        for point in t:
            if point_inside_polygon(point, final_p[:, :2]):
                infill_points.append(point)
            else:
                continue
    infill_points = infill_points[1:]
  
    
    #Hole Check Functionality
    hole_check = True
    if hole_check:
        steps = []
        base_dist = resolution*(0.5**0.5)
        factor = 2.8
        for j, point in enumerate(infill_points):
            HoleCheck(infill_points[j-1], point, base_dist, factor, steps)

        ExportHoleCheck(steps, steps_p, layers = 1, layer_height = 0.2)

    else:
        ##More Gcode Formatting to Make things go smoothly from one point to the other
        steps = [fc.Point(x = point[0], y = point[1], z = point[2]) for point in infill_points]
        ExportGCode(steps, steps_p, layer_height, layers)
        

   