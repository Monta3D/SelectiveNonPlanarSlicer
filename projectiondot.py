import numpy as np
from mpl_toolkits import mplot3d
from trajectoryplanner import PlanTrajectory45Degree
from stlprocessor import CreateMesh, ElementWiseDotProduct, GetPlaneEquationDot
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

##Get rid of the for loop

def PlotMeshAndPointsAndTrajectories(my_mesh: np.ndarray, points: list, trajectories: np.ndarray):
    """
    Plot the Mesh, Points, and Trajectories.
    Parameters:
    - my_mesh: STL mesh (assumed to have 'vectors' attribute)
    - points: List of points to be plotted, in the form nx3
    - trajectories: Trajectories of the points
    """
    # Create a new plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Load the STL files and add the vectors to the plot
    ax.add_collection3d(mplot3d.art3d.Poly3DCollection(my_mesh.vectors))

    # Convert list of sequences to a single NumPy array
    points_array = np.array(points)

    # Extract x, y, z coordinates from points
    x_points, y_points, z_points = points_array.T

    # Plot the points
    ax.scatter(x_points, y_points, z_points, c='orange', s=1, label='Projected Points')

    # Plot trajectories with colormap and adjusted line width
    ax.plot(trajectories[:, 0], trajectories[:, 1], trajectories[:, 2], linewidth=0.5, color='green', marker='*', markersize=0.7, 
            markeredgecolor='red', label='Trajectories')
    


    # Auto scale to the mesh size
    scale = my_mesh.points.flatten()
    ax.auto_scale_xyz(scale, scale, scale)

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Mesh, Points, and Trajectories')

    # Add legend
    ax.legend()

    # Show the plot
    plt.show()

def PlotPoints(points: list ):
    """
    Plot the Points
    Parameters:
    - points: Points to be plotted, in the form nx3
    """
    # Create a new plot
    figure = plt.figure()
    axes = figure.add_subplot(projection='3d')

     # Convert list of sequences to a single NumPy array
    points_array = np.array([np.array(point) for point in points])

    # Extract x, y, z coordinates from points
    x_points = points_array[:, 0]
    y_points = points_array[:, 1]
    z_points = points_array[:, 2]

    # Plot the points
    axes.scatter(x_points, y_points, z_points, cmap ='viridis', s = 3, label='Points')


    # Show the plot to the screen
    plt.show()


def GetProjectionDot(mesh_vectors: np.ndarray, n: np.ndarray, c: np.ndarray, d: np.ndarray, point:np.ndarray, projection_vector = np.array([0, 0, -1]), layer_up = True, layer_height = 0.4 ):
    
    """
    Get the point projected down onto the STL surface
    -n: plane normals
    -c: plane centroids
    -d: parameter d in plane equations defined by normal and centroid (dot product of normal and centroid)
    -point: the point in question to be projected, 1x3 array
    -plane_equations_parametric: the equations of all the planes in parametric form, p0, u1, u2, nx3x3 array
    -projection vector: the vector used to project the point onto the surface
    -mesh_vectors: vectors of the vertices of each plane in the STL file, shape nx3x3
    -layer_up: should projected points be shifted one layer up with respect to surface, default is true in order to not collide with planar slicing
    -layer height: how far up should projected points be w.r.t. planar slicing
    """

    
    #Solve for t
    p0 = point
    p0_tiled = np.tile(p0, (n.shape[0],1))
    projection_vector_tiled = np.tile(projection_vector, (n.shape[0], 1))

    t_num = -(-d + ElementWiseDotProduct(n, p0_tiled))
    t_den = (ElementWiseDotProduct(projection_vector_tiled, n))
    t = t_num/t_den

    #Get the projected point
    projected_points = p0_tiled + np.stack([t, t, t], axis = -1)*projection_vector_tiled


    #Rename mesh vectors for ease
    v = mesh_vectors

    p0x = p0_tiled[:,0]
    p0y = p0_tiled[:,1]

    v1x = v[:, 0, 0]
    v1y = v[:, 0, 1]

    v2x = v[:, 1, 0]
    v2y = v[:, 1, 1]

    v3x = v[:, 2, 0]
    v3y = v[:, 2, 1]


    #Solve for s and w to check if its in the plane
    s_num = (p0x - v2x)*(v3y - v2y) - (v3x - v2x)*(p0y - v2y)
    s_den = (v1x - v2x)*(v3y - v2y) - (v3x - v2x)*(v1y - v2y)
    s = s_num/s_den

    w_num = (p0y - v2y)*(v1x - v2x) - (v1y - v2y)*(p0x - v2x)
    w_den = (v1x - v2x)*(v3y - v2y) - (v3x - v2x)*(v1y - v2y)
    w = w_num/w_den

    #stack w and s into one array
    sol = np.stack((s,w), axis = -1)

    # Extract the items where s and w are greater than 0,
    mask = (sol[:, 0] > 0) & (sol[:, 1] > 0) 

    # Further filter based on the sum of the first and second entries, sum of s and w has to be less than or equal to 1
    mask &= (sol[:, 0] + sol[:, 1] <= 1)

    #Filter
    projected_points_filtered = projected_points[mask]

    try:
        # Find the index of the subarray with the largest z value, or the smallest t value
        max_z_index = np.argmax(projected_points_filtered[:, 2])
        final_point = projected_points_filtered[max_z_index]
    
    except:
        return
    
    if layer_up:
        final_point[2] = final_point[2] + layer_height
    return final_point




if __name__ == "__main__":

    #Get Mesh, normals and centroids
    mesh = CreateMesh("surface_double_curved.stl")  # Use a different variable name

    centroids = np.mean(mesh.vectors, axis=1)
    normals = mesh.normals

    ##Get Plane equations
    n, C, d = GetPlaneEquationDot(normals, centroids)

    #Get trajectories array
    trajectories = PlanTrajectory45Degree([150,150], 40, spacing = 10, resolution = 1, plot=False)

    ##Reshape into (npoints, 3)
    points = trajectories.reshape(-1,3)

    projected_points = []
    for i, point in enumerate(points):
        projected_points.append(GetProjectionDot(mesh.vectors, n, C, d, point))

        if i%1000 == 0:
            print("Projecting")
            print(f"Lemme Cook, i = {i}/{len(points)}")
            
    
    non_none_elements = [element for element in projected_points if element is not None]

    print(non_none_elements)

    PlotMeshAndPointsAndTrajectories(mesh, non_none_elements, trajectories)

    PlotPoints(non_none_elements)