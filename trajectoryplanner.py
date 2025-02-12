import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt

def PlanTrajectory45Degree(bedsize: np.ndarray, z: np.ndarray, spacing: float, resolution: float, plot=True):
    """
    Make 45-degree trajectory over the whole bedsize with spacing "spacing"
    - bedsize: size of the printing bed to generate the trajectory on, [xmin, xmax, ymin, ymax]
    - spacing: spacing between each line in the trajectory
    - resolution: distance between each point on the same line in mm
    - plot: Do you want to plot
    - z: constant z height of the trajectory
    """

    ymax = bedsize[3]
    ymin = bedsize[2]
    xmax = bedsize[1]
    xmin = bedsize[0]

    # Generate x coordinates
    x = np.linspace(0, xmax, int(np.round(xmax / resolution)))

    # Generate y intercept values
    y_intercepts = np.arange(-ymax, ymax, spacing)

    # Create a 2D array of x values repeated for each y_intercept
    x_repeated = np.tile(x, (len(y_intercepts), 1))

    # Create a 2D array of y values for all lines
    y_repeated = x_repeated + y_intercepts[:, np.newaxis]

    # Create a 2D array of constant z values
    z_points = z * np.ones_like(y_repeated)

    # Stack x, y, and z arrays
    trajectories = np.stack((x_repeated, y_repeated, z_points), axis=-1)

    # Extract the items x is between 0 and xmax
    mask = (trajectories[:, :,0] > xmin) & (trajectories[:, :,0] <= xmax) 

    # Further filter based on y between 0 and ymax
    mask &= (trajectories[:, :, 1] > ymin) & (trajectories[:, :, 1] <= ymax)

    #Filter
    trajectories = trajectories[mask]

    if plot:
        # Plot all lines at once
        plt.plot(trajectories[:,0], trajectories[:,1], color='blue', marker='o', markersize=3, markerfacecolor='orange')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Lines with 45-degree angle from origin and varying y-intercepts')
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
        plt.grid(True)
        plt.show()

    return trajectories

if __name__ == "__main__":
    constant_z = 100
    trajectories1 = PlanTrajectory45Degree([150, 300, 150, 300], z=constant_z, spacing=10, resolution=1, plot=True)
    print(trajectories1[0][0]) #x coordinate of first point


    
