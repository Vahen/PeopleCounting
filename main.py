from vxl import VxlCameraInfo, VxlVideo
import numpy as np
import cv2
import matplotlib.pyplot as plt

from skimage import data
from skimage.morphology import disk

cameraInfo = VxlCameraInfo('OPT8241')

background = VxlVideo.readAsAvgImage("videos/video_1_ap.vxl", cameraInfo)

video = VxlVideo.read("videos/video_1.vxl", cameraInfo)

miniv = min(min([frame.amplitude.min() for frame in video]), background.amplitude.min())
maxiv = max(max([frame.amplitude.max() for frame in video]), background.amplitude.max())

minivd = min(min([frame.depth.min() for frame in video]), background.depth.min())
maxivd = max(max([frame.depth.max() for frame in video]), background.depth.max())


def depth_objects(frame):
    nn = 255

    mini = minivd
    maxi = maxivd

    image = (nn * ((frame.depth - mini) / (maxi - mini))).astype(np.uint8)
    image = cv2.medianBlur(image, 5)

    bg = (nn * ((background.depth - mini) / (maxi - mini))).astype(np.uint8)
    bg = cv2.medianBlur(bg, 5)

    foreground = bg.astype(np.int16) - image.astype(np.int16)
    foreground = cv2.medianBlur(foreground, 5)

    objects = (foreground > 10).astype(np.uint8)
    objects = cv2.morphologyEx(objects, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    return objects


def amplitude_objects(frame):
    foreground = abs(frame.amplitude - background.amplitude)

    mini = 0
    maxi = maxiv - miniv
    nn = 100
    forg = (nn * ((foreground - mini) / (maxi - mini))).astype(np.uint8)

    forg = cv2.medianBlur(forg, 3)

    _, objects = cv2.threshold(foreground.astype(np.uint8), mini, maxi, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    objects = cv2.morphologyEx(objects, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return objects


def process(frame):
    return np.logical_or(depth_objects(frame), amplitude_objects(frame))


from scipy.signal import *
from scipy.ndimage import *


def isPerson(img, sigma):
    som = []
    h, w = img.shape
    som = img.sum(axis=0)
    x = np.array(range(w))
    filtered = filters.gaussian_filter1d(som, sigma)
    y = np.array(filtered)

    maxm = argrelmax(y)
    #minm = argrelextrema(y, np.less)

    # plt.plot(x, y)

    # for i in maxm:
    #     plt.plot(i, filtered[i], 'o', color="red")
        # plt.annotate('Max Local',
        #          ha='center', va='bottom',
        #          xytext=(-1.5 +i, 3. +som[i]),
        #          xy=(i, som[i]),
        #          arrowprops={'facecolor': 'black', 'shrink': 0.05})
    # plt.show()  # affiche la figure a l'ecran

    if len(maxm[0]) == 1:
        return True

    if len(maxm[0]) == 3:
        return len(maxm[0]) == 3 and (filtered[maxm[0][1]] > filtered[maxm[0][0]] and filtered[maxm[0][1]] > filtered[maxm[0][2]])
    return False


nb_people = 0
for i in range(len(video)):
    img = process(video.avgFrame(i, 1))

    #plt.figure(2)
    #plt.clf()
    if isPerson(img, 3):
        print("is personn")
        nb_people = nb_people+1

    plt.figure(1)
    plt.clf()
    plt.imshow(img, cmap=plt.cm.Greys_r)
    plt.text(15, 23, 'people : ' + str(nb_people), bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 10})
    plt.axis('off')
    plt.pause(0.001)
plt.show()
