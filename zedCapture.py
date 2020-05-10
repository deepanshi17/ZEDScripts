# Last edited by: Spencer Trihus
# Date: 2/12/2020
# Added argument parsing to allow camera setting customization and added loop

import time
import pyzed.sl as sl
import math
import numpy as np
import sys
import saveFileTools
import sys
import datetime
import argparse

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--depth_mode', type=str, default = 'PERFORMANCE', choices = {'PERFORMANCE', 'ULTRA', 'QUALITY'}, help='determine ZED depth mode')
    parser.add_argument('--sensing_mode', type=str, default = 'STANDARD', choices = {'STANDARD', 'FILL'}, help='determine ZED sensing mode')
    parser.add_argument('--min_distance', type=min_restricted_float, default = -1, help='set minimum distance recognized by ZED between 0.3-3m, data before this range will not be computed')
    parser.add_argument('--max_distance', type=max_restricted_float, default = -1, help='set maximum distance recognized by ZED between 0-40m, data beyond this range will not be computed')
    parser.add_argument('--num_frames', type=int, default = 1, choices = range(1,50), metavar = '[1,50]', help='set number of frames to capture')
    parser.add_argument('-l', '--loop', action='store_true', help='run until manual exit')
    opt = parser.parse_args()


    # Create a Camera object
    numFrames = opt.num_frames
    base = "C:/Users/User/Desktop/TSL_Repo/SERPENT-SWD"
    name = "captured"

    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.coordinate_units = sl.UNIT.MILLIMETER  # Use milliliter units (for depth measurements)

    init_params.depth_minimum_distance = opt.min_distance*1000 # Set the minimum depth perception distance
    init_params.depth_maximum_distance = opt.max_distance*1000 # Set the maximum depth perception distance

    if opt.depth_mode == 'ULTRA':
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # Use ULTRA depth mode
    elif opt.depth_mode == 'QUALITY':
        init_params.depth_mode = sl.DEPTH_MODE.QUALITY  # Use ULTRA depth mode
    else:
        init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE  # Use PERFORMANCE depth mode



    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Create and set RuntimeParameters after opening the camera
    runtime_parameters = sl.RuntimeParameters()
    if opt.sensing_mode == 'FILL':
        runtime_parameters.sensing_mode = sl.SENSING_MODE.FILL  # Use FILL sensing mode
    else:
        runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode

    # Capture 50 images and depth, then stop
    rgb_image = sl.Mat()
    depth_image = sl.Mat()
    point_cloud = sl.Mat()

    while 1:
        # create folder and text file to write to
        dataFolder = saveFileTools.setupFolder(base, name)
        depthData = open(dataFolder + "centerDist.txt", "w+")
        depthData.write("Start Time: " + str(datetime.datetime.now()) + "\n")

        i = 0
        while i < numFrames:
            # A new image is available if grab() returns SUCCESS
            if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # Retrieve left image
                zed.retrieve_image(rgb_image, sl.VIEW.LEFT)
                # Retrieve depth map. Depth is aligned on the left image
                zed.retrieve_image(depth_image, sl.VIEW.DEPTH)
                # Retrieve colored point cloud. Point cloud is aligned on the left image.
                zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

                # Get and print distance value in mm at the center of the image
                # We measure the distance camera - object using Euclidean distance
                x = round(rgb_image.get_width() / 2)
                y = round(rgb_image.get_height() / 2)
                err, point_cloud_value = point_cloud.get_value(x, y)

                distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
                                     point_cloud_value[1] * point_cloud_value[1] +
                                     point_cloud_value[2] * point_cloud_value[2])

                if not np.isnan(distance) and not np.isinf(distance):
                    distance = round(distance)
                    print("Distance at the center {0} mm\n".format(distance))
                    depthData.write("Frame: {0} Distance at the center {1} mm\n".format(i, distance))
                    rgb_image.write(dataFolder + "rgb_img" + str(i) + ".png")
           
                    depth_image.write(dataFolder + "depth_img" + str(i) + ".png")
                    # Increment the loop
                    i = i + 1
                else:
                    print("Can't estimate distance at this position, move the camera\n")
                sys.stdout.flush()

            # close files
            depthData.write("End Time: " + str(datetime.datetime.now()))
            # time.sleep(1) # may not be necessary if no write time issues
        
        depthData.close()
            
        # check if user desired to loop
        if not opt.loop:
            break
        user_continue = str(input('Press enter to continue. Enter any other key to quit.\n'))
        if user_continue != '':
            break
        user_continue == '*'


    # Close the camera
    zed.close()

def max_restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 100.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 40.0]"%(x,))
    return x

def min_restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.3 or x > 3.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 40.0]"%(x,))
    return x


if __name__ == "__main__":
    main()
