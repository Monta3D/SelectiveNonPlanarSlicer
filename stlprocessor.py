import numpy as np
from stl import mesh as mesh_module  # Rename the module
from mpl_toolkits import mplot3d
from matplotlib import pyplot
from matplotlib.colors import LightSource
from matplotlib import cm
import time
import matplotlib.pyplot as plt


#need to understand how these stlf files are stored, what does it mean for triangles to be next to each other
#should it be checking each neighbour iteratively, or just taking a streak of consecutive true/false
#how to even see which triangles are neighbors?
#make a cmap viridis plot of the stl?

def CreateMesh(filepath: str):
    """
    Create a Mesh from an STL file
    Parameters:
    - filepath: filepath relative to current directory, use quotations
    """
    my_mesh = mesh_module.Mesh.from_file(filepath, calculate_normals=True, remove_empty_areas=False, remove_duplicate_polygons=False)  # Rename the variable
    return my_mesh


def MeshTranslate(x_translate, y_translate, z_translate, meshvectors): 
    """
    Translate the mesh by a given x y or z value
    -x_translate: how much to translate in the x direction
    -y_translate: how much to translate in the y direction 
    -z_translate: how much to translate in the z direction
    -mesh.vectors: vectors of the mesh, shape (nx3x3)
    """
    meshvectors[:,:,0] = meshvectors[:,:,0] + x_translate
    meshvectors[:,:,1] = meshvectors[:,:,1] + y_translate
    meshvectors[:,:,2] = meshvectors[:,:,2] + z_translate

    return meshvectors

def MeshTranslateOrigin(printbed: np.ndarray, meshvectors:np.ndarray):
    """
    Translate the mesh by a given x y or z value
    -printbed: [x,y] coordinates of the printbed
    -mesh.vectors: vectors of the STL mesh, shape (nx3x3)
    """

    x_middle = (np.max(meshvectors[:,:,0]) + np.min(meshvectors[:,:,0]))/2
    y_middle = (np.max(meshvectors[:,:,1]) + np.min(meshvectors[:,:,1]))/2

    x_printbedmiddle, y_printbedmiddle = printbed/2
    
    x_shift = x_printbedmiddle - x_middle
    y_shift = y_printbedmiddle - y_middle

    shifted_mesh = MeshTranslate(x_shift, y_shift, 0, meshvectors)
    return shifted_mesh
    
     

def MeshScale(x_scale, y_scale, z_scale, meshvectors): 
    """
    Translate the mesh by a given x y or z value
    -x_translate: how much to translate in the x direction
    -y_translate: how much to translate in the y direction 
    -z_translate: how much to translate in the z direction
    -mesh.vectors: vectors of the mesh, shape (nx3x3)
    """
    meshvectors[:,:,0] = meshvectors[:,:,0]*x_scale
    meshvectors[:,:,1] = meshvectors[:,:,1]*y_scale
    meshvectors[:,:,2] = meshvectors[:,:,2]*z_scale

    return meshvectors

def PlotMesh(mesh_vectors: np.ndarray):
    """
    Plot the Mesh
    Parameters:
    - my_mesh: STL mesh
    """
    # Create a new plot
    figure = pyplot.figure()
    axes = figure.add_subplot(projection='3d')

    # Load the STL files and add the vectors to the plot
    fig = mplot3d.art3d.Poly3DCollection(mesh_vectors)
    axes.add_collection3d(fig)

    # Auto scale to the mesh size
    scale = mesh_vectors.flatten()
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.show()

    return figure

def GetPlaneEquationParametric(v0:np.ndarray, v1: np.ndarray, v2: np.ndarray):
    """
    Create the adjacent vectors and initial point for the parametric equation of a plane
    -v1, v2, v3: The vertices in question    
    """
    p0 = v0
    u1 = v0 - v1
    u2 = v2 - v0
    return np.stack((p0, u1, u2), axis = -1)

def ElementWiseDotProduct(x1: np.ndarray, x2:np.ndarray):
    """
    Elementwise dot product of big arrays, for future use and I couldnt find a numpy library that did what I want. Output is shape (n)
    -x1: first array (nxm)
    -x2: second array (nxm)
    """
    return np.sum(x1*x2, axis = 1)

def GetPlaneEquationDot(n:np.ndarray, C: np.ndarray):
    """
    Create the equation of the plane in the form C*n - d = 0. Returns  C, n and d in that order
    -n: normal vectors of each plane
    -C: centroid of each plane
    """

    # Element-wise dot product
    d = ElementWiseDotProduct(n, C)
    return n, C, d

def GetNeighborFacets(facet: np.ndarray, possible_neighbors: np.ndarray):
    """
    Find which facets in possible neighbours share a point with that in facet:
    - facet: facet to check points again, is a 3x3 array, 3 points each with 3 coordiantes
    - possible_neighbours: array with possible neighbours. is an nx3x3 array
    returns the actual neighbours of the facet
    """
    #Now we want to remove all neighbors from left_over_facets array
    matches = np.any(np.all(np.isin(possible_neighbors, facet), axis= 2), axis = 1)
    
    # Apply mask to filter out matched facets
    neighbors = possible_neighbors[matches]

    if len(neighbors) > 0:
        new_finding = True
    else: 
        new_finding = False

    return neighbors[1:], new_finding

def RemoveNeighbors(neighbors: np.ndarray, left_over_facets: np.ndarray):
    """
    Remove the found neighbors from the left over facets to test:
    - neighbors: facets to remove,  nx3x3 array, 3 points each with 3 coordiantes
    - left_over_facets: array with remaining facets, remove the neighbors found from this array, nx3x3
    returns left_over_facets but then without the neighbors found
    """
    #Now we want to remove all neighbors from left_over_facets array
    matches = np.all(np.isin(left_over_facets, neighbors), axis=(1, 2))
    mask = ~matches
    
    # Apply mask to filter out matched facets
    left_over_facets = left_over_facets[mask]

    return left_over_facets

def GetIndex(big_array: np.ndarray, small_array: np.ndarray):
    """
    Check what index the small array is in the the big array, returns the index. This function is mostly used in the projection dot funtion
    so the assumed shaped of the big and small array are nx3x3 and 1x3x3 respectively
    -big_array: big array that contains the small array
    -small_array: small array that is somewhere in the big array
    """

    indices = np.arange(0, big_array.shape[0],1)
    small_array_tiled = np.tile(small_array, (big_array.shape[0],1,1))
    return indices[np.all((np.all((big_array == small_array_tiled), axis = 2)), axis = 1)]


def GetTriangleNormal(triangles: np.ndarray):
    """
    Calculate and return the normal of a triangle defined by coordinates
    -triangles : nx3x3 array
    """
    # The cross product of two sides is a normal vector
    return np.cross(triangles[:,1] - triangles[:,0], 
                    triangles[:,2] - triangles[:,0], axis=1)

def GetTriangleArea(triangles: np.ndarray):
    """
    Calculate and return the area of a triangle defined by coordinates
    -triangles : nx3x3 array
    """
    # The norm of the cross product of two sides is twice the area
    return np.linalg.norm(GetTriangleNormal(triangles), axis=1) / 2

def PlotSurfaces(arrnp, arrp):
    
    """
    Plot the planar and non planar surfaces
    Parameters:
    - arrnp: nx3x3 array
    - arrp: nx3x3 array
    """

    # Create a new plot
    figure = pyplot.figure()
    # Define a subplot grid. In this case, 1 row, 3 columns
    axes1 = figure.add_subplot(1, 3, 1, projection='3d')  # First subplot
    axes2 = figure.add_subplot(1, 3, 2, projection='3d')  # Second subplot
    axes3 = figure.add_subplot(1, 3, 3, projection='3d')  # Third subplot

    # Load the STL files and add the vectors to the plot
    fignp1 = mplot3d.art3d.Poly3DCollection(arrnp)
    fignp1.set_facecolor("#32a852")
    fignp1.set_alpha(0.9)
    fignp1.set_edgecolor("#2c6910")
    fignp1.set_linewidth(0.1)
    
    figp1 = mplot3d.art3d.Poly3DCollection(arrp)
    figp1.set_facecolor("#FB9B9B")
    figp1.set_edgecolor("#000000")
    figp1.set_linewidth(0.1)
    figp1.set_verts(arrp)

    #Subplot 1 is both
    axes1.add_collection3d(fignp1)
    axes1.add_collection3d(figp1)

    #Subplot 2 is nonplanar only

    # Load the STL files and add the vectors to the plot
    fignp2 = mplot3d.art3d.Poly3DCollection(arrnp)
    fignp2.set_facecolor("#32a852")
    fignp2.set_alpha(0.9)
    fignp2.set_edgecolor("#2c6910")
    fignp2.set_linewidth(0.1)
    axes2.add_collection3d(fignp2)

    #Subplot 3 is planar only
    figp3 = mplot3d.art3d.Poly3DCollection(arrp)
    figp3.set_facecolor("#FB9B9B")
    figp3.set_edgecolor("#000000")
    figp3.set_linewidth(0.1)
    figp3.set_verts(arrp)
    axes3.add_collection3d(figp3)

    # Auto scale to the mesh size, can we get this to acually zoom in onto the surface? xlim(min, max) doesnt work because of the different scales on the different axes, makes it look very stretched
    # Would be nice if matplotlib had readable documentation
    scalenp = arrnp.flatten()
    scalep = arrp.flatten()

    axes1.auto_scale_xyz(scalenp, scalenp, scalenp)
    axes2.auto_scale_xyz(scalenp, scalenp, scalenp)
    axes3.auto_scale_xyz(scalep, scalep, scalep)

    # Show the plot to the screen
    #pyplot.title("Non Planar Printable and Planar Surfaces")
    pyplot.show()


def PlotScatter3D(array):
    """
    Create a scatter plot from an input array of shape (n, 3, 3).

    Parameters:
    array (numpy.ndarray): Input array of shape (n, 3, 3).

    Returns:
    None
    """

    # Extract x, y, z coordinates from flattened array
    x = array[:,:,0]
    y = array[:,:,1]
    z = array[:,:,2]

    # Create a new figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Scatter plot
    ax.scatter(x, y, z, c='#32a852', s=1)

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Show plot
    plt.show()

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[py] = px

def SplitSTLSurfaces(mesh: np.ndarray, mesh_vectors: np.ndarray,  max_height: float, max_angle: float, min_area: float, save = True, tol = 1e-7):
    """
    Split STL Mesh into non planar printable, and planar surfaces. 
    Returns 2 lists, arrnp and arrp which contain stl mesh objects of the respective surfaces
    then returns the boolean array of which surfaces pass the angle constraint
    Parameters:
    - my_mesh: STL mesh
    - max_height: maximum height of non planar surface
    - max_angle: maximum angle of non planar surface in radians plz
    - min_area: maximum area of non planar area
    - mesh_vectors : vectors of the mesh, given as a separate argument as these could be translated away from the origin before hand
    - save: boolean, should the separated nonplanar surfaces be saved as a new stl
    - tol: parameter to adjust the sensitivity of calling vertices equal
    """

    #First filter the surfaces based on angle of their normal
    normals_x = mesh.units[:,0]
    normals_z = mesh.units[:,2]
    max_angle = np.pi/4

    #Boolean array where normals are less than a given angle, This is according to ahlers but idk really. I would do it differently
    boolean_angles = normals_z >= np.cos(max_angle)
    #boolean_angles = abs(normals_angle) <= max_angle

    points_filtered = mesh_vectors[boolean_angles]
    planar_surface = mesh_vectors[~boolean_angles]

    #Make the planar surface into stl form and save if needed
    arrp = []
    shape = mesh_module.Mesh(np.zeros(planar_surface.shape[0], dtype = mesh_module.Mesh.dtype))
    for j, f in enumerate(arrp):
        shape.vectors[j] = f
        arrp.append(shape)
        if save:
            shape.save(f"separated_stl_files/planar_surface{j}.stl") 

    #Now Separate the Surfaces

    triangles = points_filtered
    N = len(triangles)
    
    def vertex_hash(vertex, tol=1e-5):
        return hash((int(vertex[0] / tol), int(vertex[1] / tol), int(vertex[2] / tol)))

    vertex_to_triangles = {}

    # Loop through each triangle and each vertex within that triangle
    for i, triangle in enumerate(triangles):
        for vertex in triangle:
            # Calculate hash for the current vertex
            hv = vertex_hash(vertex, tol)
            if hv not in vertex_to_triangles:
                vertex_to_triangles[hv] = set()
            vertex_to_triangles[hv].add(i)

    uf = UnionFind(N)
    
    # Union all triangles sharing at least one vertex (as per hash)
    for sets in vertex_to_triangles.values():
        sets = list(sets)
        base = sets[0]
        for s in sets[1:]:
            uf.union(base, s)
    
    # Aggregate triangles into surfaces
    surfaces = {}
    for i in range(N):
        root = uf.find(i)
        if root not in surfaces:
            surfaces[root] = set()
        surfaces[root].add(i)

    #Make a list out of the surfaces
    surfaces_list =  list(surfaces.values())

    #Get the indices out of the points_filtered array and cehck the constraints
    printable_nonplanar_surfaces = []
    for group in surfaces_list:
        int_array = np.array(list(group), dtype=int)
        surface = points_filtered[int_array]

        #Check if constraints are met, then save if yes
        points = np.squeeze(np.array([point for point in surface]))
        if len(points.shape) > 2 and points.shape[0]>= 1:

            area = np.sum(GetTriangleArea(points))
            height = np.max(points[:,:,2]) - np.min(points[:,:,2])
           
            if height <= max_height and area > min_area:
                printable_nonplanar_surfaces.append(surface)
    
    #Convert the arrays into STL format
    arrnp = []
    for i, surface in enumerate(printable_nonplanar_surfaces):
        shape = mesh_module.Mesh(np.zeros(surface.shape[0], dtype = mesh_module.Mesh.dtype))
        for j, f in enumerate(surface):
            shape.vectors[j] = f
        arrnp.append(shape)
        shape.save(f"separated_stl_files/non_planar_surface{i}.stl") 
    
    return arrnp, arrp, boolean_angles



if __name__ == "__main__": 

    time0 = time.time()

    mesh = CreateMesh('comp_utensile\\prova1\\polygonal_non_planar.stl')  # Use a different variable name

    mesh_vectors = MeshTranslateOrigin(np.array([300, 300]), mesh.vectors)

    arrnp, arrp, boolean_angles = SplitSTLSurfaces(mesh, mesh_vectors, max_height = 200, max_angle = np.pi/4, min_area = 30, save = True)

    time1 = time.time()
    print("Time to Separate Surfaces =", time1 - time0)


    #PlotMesh(my_mesh_vectors)
    #PlotMesh(arrnp[0].vectors)
    #PlotMesh(arrp.vectors)
    #PlotScatter3D(arrp.vectors)
    for arr in arrnp:
        PlotScatter3D(arr.vectors)
        PlotMesh(arr.vectors)
    
    
        
