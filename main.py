import airsim
import cv2
import numpy as np
import os
import time
import math
import pprint
import argparse
import threading
import plotter

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--camera_list', nargs='+', default=['0', '1', '2', '3', '4'], help='List of cameras visualised : [0, 1, ... , 4]')
args = parser.parse_args()

pp = pprint.PrettyPrinter(indent=4)

#plotter.init_disp()

client = airsim.CarClient()
client.confirmConnection()
client.enableApiControl(False)
print("API Control enabled: %s" % client.isApiControlEnabled())
car_controls = airsim.CarControls()

camera_data = {}

for camera_name in range(5):
    camera_info = client.simGetCameraInfo(str(camera_name))
    camera_data[str(camera_name)] = camera_info
    print("CameraInfo %d:" % camera_name)
    pp.pprint(camera_info)

cam_name = {
        '0': 'Front',
        '1': 'Back',
        '2': 'Right',
        '3': 'Left',
        '4': 'FrontLR',
}
cam_name_show = args.camera_list
mode_name = {
        0: 'Scene', 
        1: 'DepthPlanner', 
        2: 'DepthPerspective',
        3: 'DepthVis', 
        4: 'DisparityNormalized',
        5: 'Segmentation',
        6: 'SurfaceNormals'
}

def image_loop():
    while True:
        responses = client.simGetImages([
            #airsim.ImageRequest("0", airsim.ImageType.DepthVis),
            #airsim.ImageRequest("1", airsim.ImageType.DepthPerspective, True),
            #airsim.ImageRequest("2", airsim.ImageType.Segmentation),
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False),
            airsim.ImageRequest("1", airsim.ImageType.Scene, False, False),
            airsim.ImageRequest("2", airsim.ImageType.Scene, False, False),
            airsim.ImageRequest("3", airsim.ImageType.Scene, False, False),
            airsim.ImageRequest("4", airsim.ImageType.Scene, False, False),

            #airsim.ImageRequest("0", airsim.ImageType.DepthVis, True, False),
            #airsim.ImageRequest("1", airsim.ImageType.DepthVis, True, False),
            #airsim.ImageRequest("2", airsim.ImageType.DepthVis, True, False),
            #airsim.ImageRequest("3", airsim.ImageType.DepthVis, True, False),
            airsim.ImageRequest("4", airsim.ImageType.DepthVis, True, False),

            airsim.ImageRequest("0", airsim.ImageType.Segmentation, False, False),
            airsim.ImageRequest("1", airsim.ImageType.Segmentation, False, False),
            airsim.ImageRequest("2", airsim.ImageType.Segmentation, False, False),
            airsim.ImageRequest("3", airsim.ImageType.Segmentation, False, False),
            airsim.ImageRequest("4", airsim.ImageType.Segmentation, False, False),
            #airsim.ImageRequest("4", airsim.ImageType.Scene, False, False),
            #airsim.ImageRequest("4", airsim.ImageType.DisparityNormalized),
            #airsim.ImageRequest("4", airsim.ImageType.SurfaceNormals)
            ])

        for i, response in enumerate(responses):
            #print(dir(response))
            #filename = os.path.join(tmp_dir, str(x) + "_" + str(i))
            if response.pixels_as_float:
                #print("pixels_as_float Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_float), pprint.pformat(response.camera_position)))
                #airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
                #img = airsim.get_pfm_array(response)
                depth = np.array(response.image_data_float, dtype=np.float32)
                depth = depth.reshape(response.height, response.width)
                img = np.array(depth * 255, dtype=np.uint8)

            else:
                #print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_uint8), pprint.pformat(response.camera_position)))
                #airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)
                img = response.image_data_uint8
                img = np.frombuffer(img, dtype=np.uint8)
                #img = np.fromstring(img, dtype=np.uint8)
                img = img.reshape(response.height, response.width, 3)
            #print(img)
            if mode_name[response.image_type] == 'DepthVis':
                p_mat = np.array(camera_data[response.camera_name].proj_mat.matrix)
                points = cv2.reprojectImageTo3D(depth, p_mat)
                points = cv2.reprojectImageTo3D(img, p_mat)
                #points = [(0,0,0), ]
                #points = list(filter(lambda p: (-float('inf')<p).all() and (p<float('inf')).all(), points))
                #points = list(filter(lambda p: not p[0].isinf() and not p[0].isinf() and not p[0].isinf(), points))
                #print(points)
                plotter.plot_points(points)
            if response.camera_name in cam_name_show:
                #cv2.imshow(cam_name[response.camera_name] + "_" + mode_name[response.image_type], img)
                #cv2.waitKey(1)
                pass

image_loop_thread = threading.Thread(target=image_loop, daemon=True)
image_loop_thread.start()
plotter.start_graph()
exit()
while True:
    #image_loop()
    plotter.main_loop()
    plotter.start_graph()
