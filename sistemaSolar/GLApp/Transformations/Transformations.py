import numpy as np
from math import *


def identity_mat():
    return np.identity(4, np.float32)


def translate_mat(x, y, z):
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ])


def scale_mat(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1],
    ])


def rotate_x_mat(angle):
    co = cos(radians(angle))
    si = sin(radians(angle))
    return np.array([
        [1, 0, 0, 0],
        [0, co, -si, 0],
        [0, si, co, 0],
        [0, 0, 0, 1],
    ], np.float32)


def rotate_y_mat(angle):
    co = cos(radians(angle))
    si = sin(radians(angle))
    return np.array([
        [co, 0, si, 0],
        [0, 1, 0, 0],
        [-si, 0, co, 0],
        [0, 0, 0, 1],
    ], np.float32)


def rotate_z_mat(angle):
    co = cos(radians(angle))
    si = sin(radians(angle))
    return np.array([
        [co, -si, 0, 0],
        [si, co, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ], np.float32)


def translate(matrix, x, y, z):
    trans = translate_mat(x, y, z)
    return matrix @ trans


def scale(matrix, x, y, z):
    sc = scale_mat(x, y, z)
    return matrix @ sc


def rotate(matrix, angle, axis, local=True):
    rot = identity_mat()
    if axis == 'x':
        rot = rotate_x_mat(angle)
    elif axis == 'y':
        rot = rotate_y_mat(angle)
    elif axis == 'z':
        rot = rotate_z_mat(angle)
    if local:
        return matrix @ rot
    else:
        return rot @ matrix
