# import cv2
# import time
# import glob
# import os
# import numpy as np
# from numpy import array, rot90


# MARKER_SIZE = 7

# BORDER_COORDINATES = [
#     [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 0], [1, 6], [2, 0], [2, 6], [3, 0],
#     [3, 6], [4, 0], [4, 6], [5, 0], [5, 6], [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6],
# ]

# ORIENTATION_MARKER_COORDINATES = [[1, 1], [1, 5], [5, 1], [5, 5]]

# marker1156 = np.array([[0, 0, 0, 0, 0, 0, 0],
#                       [0, 1, 1, 0, 0, 0, 0],
#                       [0, 1, 1, 0, 0, 1, 0],
#                       [0, 1, 1, 0, 0, 0, 0],
#                       [0, 0, 1, 0, 0, 1, 0],
#                       [0, 0, 1, 0, 0, 0, 0],
#                       [0, 0, 0, 0, 0, 0, 0]],
#                      dtype=np.float32)

# marker114 = np.array([[0, 0, 0, 0, 0, 0, 0],
#                        [0, 1, 0, 0, 0, 0, 0],
#                        [0, 0, 0, 0, 0, 0, 0],
#                        [0, 0, 0, 1, 1, 1, 0],
#                        [0, 1, 0, 1, 0, 1, 0],
#                        [0, 0, 0, 1, 0, 0, 0],
#                        [0, 0, 0, 0, 0, 0, 0]],
#                       dtype=np.float32)

# min_contour_length = min(320, 240) / 10

# warped_size = 49
# canonical_marker_coords = np.array(
#     (
#         (0, 0),
#         (warped_size - 1, 0),
#         (warped_size - 1, warped_size - 1),
#         (0, warped_size - 1)
#     ),
#     dtype='float32')


# # print(marker114, marker1156)
# def validate_and_turn(marker):
#     # first, lets make sure that the border contains only zeros
#     for crd in BORDER_COORDINATES:
#         if marker[crd[0], crd[1]] != 0.0:
#             raise ValueError('Border contians not entirely black parts.')
#     # search for the corner marker for orientation and make sure, there is only 1
#     orientation_marker = None
#     for crd in ORIENTATION_MARKER_COORDINATES:
#         marker_found = False
#         if marker[crd[0], crd[1]] == 1.0:
#             marker_found = True
#         if marker_found and orientation_marker:
#             raise ValueError('More than 1 orientation_marker found.')
#         elif marker_found:
#             orientation_marker = crd
#     if not orientation_marker:
#         raise ValueError('No orientation marker found.')
#     rotation = 0
#     if orientation_marker == [1, 5]:
#         rotation = 1
#     elif orientation_marker == [5, 5]:
#         rotation = 2
#     elif orientation_marker == [5, 1]:
#         rotation = 3
#     marker = rot90(marker, k=rotation)
#     return marker


# def marker_detect(black):
#     contours, hierarchy = cv2.findContours(black, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
#     contours = [contour for contour in contours if len(contour) > min_contour_length]
#     marker_number = 0
#     for contour in contours:  
#         approx_curve = cv2.approxPolyDP(contour, len(contour) * 0.01, True)
#         if (len(approx_curve) == 4) and cv2.isContourConvex(approx_curve):  
#             sorted_curve = np.array(cv2.convexHull(approx_curve, clockwise=False), dtype='float32')
#             persp_transf = cv2.getPerspectiveTransform(sorted_curve, canonical_marker_coords)
#             warped_img = cv2.warpPerspective(black, persp_transf, (warped_size, warped_size))
#             marker = warped_img.reshape([MARKER_SIZE, warped_size // MARKER_SIZE, MARKER_SIZE, warped_size // MARKER_SIZE])
#             marker = marker.reshape([7, 7, 7, 7])   
#             marker = marker.mean(axis=3).mean(axis=1)
#             marker[marker < 120] = 0
#             marker[marker >= 120] = 1
#             try:
#                 marker = validate_and_turn(marker)
#                 if np.array_equal(marker, marker114):
#                     marker_number = 114
#                 elif np.array_equal(marker, marker1156):
#                     marker_number = 1156
#             except ValueError:
#                 continue
#         else:
#             continue
#     return marker_number


import cv2
import time
import glob
import os
import numpy as np
from numpy import array, rot90


MARKER_SIZE = 7

BORDER_COORDINATES = [
    [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 0], [1, 6], [2, 0], [2, 6], [3, 0],
    [3, 6], [4, 0], [4, 6], [5, 0], [5, 6], [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6],
]

ORIENTATION_MARKER_COORDINATES = [[1, 1], [1, 5], [5, 1], [5, 5]]

marker922 = np.array([[0, 0, 0, 0, 0, 0, 0],
                      [0, 1, 1, 0, 0, 0, 0],
                      [0, 0, 0, 1, 1, 0, 0],
                      [0, 0, 1, 1, 0, 0, 0],
                      [0, 1, 1, 0, 1, 1, 0],
                      [0, 0, 0, 1, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0]],
                     dtype=np.float32)

marker114 = np.array([[0, 0, 0, 0, 0, 0, 0],
                       [0, 1, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 1, 1, 1, 0],
                       [0, 1, 0, 1, 0, 1, 0],
                       [0, 0, 0, 1, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0]],
                      dtype=np.float32)

marker2537 = np.array([[0, 0, 0, 0, 0, 0, 0],
                       [0, 1, 0, 0, 1, 0, 0],
                       [0, 1, 0, 0, 1, 0, 0],
                       [0, 0, 1, 0, 1, 1, 0],
                       [0, 0, 0, 0, 1, 1, 0],
                       [0, 0, 0, 0, 1, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0]],
                      dtype=np.float32)

min_contour_length = min(320, 240) / 10

warped_size = 49
canonical_marker_coords = np.array(
    (
        (0, 0),
        (warped_size - 1, 0),
        (warped_size - 1, warped_size - 1),
        (0, warped_size - 1)
    ),
    dtype='float32')


# print(marker114, marker1156)
def validate_and_turn(marker):
    # first, lets make sure that the border contains only zeros
    for crd in BORDER_COORDINATES:
        if marker[crd[0], crd[1]] != 0.0:
            raise ValueError('Border contians not entirely black parts.')
    # search for the corner marker for orientation and make sure, there is only 1
    orientation_marker = None
    for crd in ORIENTATION_MARKER_COORDINATES:
        marker_found = False
        if marker[crd[0], crd[1]] == 1.0:
            marker_found = True
        if marker_found and orientation_marker:
            raise ValueError('More than 1 orientation_marker found.')
        elif marker_found:
            orientation_marker = crd
    if not orientation_marker:
        raise ValueError('No orientation marker found.')
    rotation = 0
    if orientation_marker == [1, 5]:
        rotation = 1
    elif orientation_marker == [5, 5]:
        rotation = 2
    elif orientation_marker == [5, 1]:
        rotation = 3
    marker = rot90(marker, k=rotation)
    return marker


def marker_detect(black):
    contours, hierarchy = cv2.findContours(black, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
    contours = [contour for contour in contours if len(contour) > min_contour_length]
    marker_number = 0
    for contour in contours:  
        approx_curve = cv2.approxPolyDP(contour, len(contour) * 0.01, True)
        if (len(approx_curve) == 4) and cv2.isContourConvex(approx_curve):  
            sorted_curve = np.array(cv2.convexHull(approx_curve, clockwise=False), dtype='float32')
            persp_transf = cv2.getPerspectiveTransform(sorted_curve, canonical_marker_coords)
            warped_img = cv2.warpPerspective(black, persp_transf, (warped_size, warped_size))
            marker = warped_img.reshape([MARKER_SIZE, warped_size // MARKER_SIZE, MARKER_SIZE, warped_size // MARKER_SIZE])
            marker = marker.reshape([7, 7, 7, 7])   
            marker = marker.mean(axis=3).mean(axis=1)
            marker[marker < 120] = 0
            marker[marker >= 120] = 1
            try:
                marker = validate_and_turn(marker)
                if np.array_equal(marker, marker114):
                    marker_number = 114
                elif np.array_equal(marker, marker922):
                    marker_number = 922
                elif np.array_equal(marker, marker2537):
                    marker_number = 2537
            except ValueError:
                continue
        else:
            continue
    return marker_number