# -*- coding: utf-8 -*-
import numpy as np
import cracktools as ct
from PyQt6.QtCore import QThread, pyqtSignal
from skimage.segmentation import mark_boundaries


class BoundaryWorker(QThread):
    """Runs mark_boundaries off the main thread."""
    finished = pyqtSignal(np.ndarray, int)   # (result_image, generation)

    def __init__(self, image: np.ndarray, mask: np.ndarray,
                 color: tuple, generation: int):
        super().__init__()
        self._image = image
        self._mask = mask
        self._color = color
        self._gen = generation

    def run(self):
        result = (mark_boundaries(self._image / 255, self._mask,
                                  color=self._color, mode='inner',
                                  background_label=1) * 255).astype(np.uint8)
        self.finished.emit(result, self._gen)


class OSWorker(QThread):
    """Runs OrientationScoreTransform off the main thread."""
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)

    def __init__(self, image_slice: np.ndarray, params: dict):
        super().__init__()
        self._image_slice = image_slice
        self._params = params

    def run(self):
        try:
            result = ct.os.OrientationScoreTransform(self._image_slice,
                                                     **self._params)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class CostWorker(QThread):
    """Runs MultiScaleVesselness + CostFunction off the main thread."""
    finished = pyqtSignal(object, object, np.ndarray)
    error    = pyqtSignal(str)

    def __init__(self, osGFCost, ksi: float, sigmas: list,
                 lambdaa: float, p: float):
        super().__init__()
        self._os = osGFCost
        self._ksi = ksi
        self._sigmas = sigmas
        self._lambdaa = lambdaa
        self._p = p

    def run(self):
        try:
            multi = ct.os.MultiScaleVesselness(
                self._os.real, self._ksi, 1, self._sigmas, "LIF",
                sigmas_ext=1)
            costmulti = ct.os.MultiScaleVesselnessFilter(multi)
            costFunc  = ct.os.CostFunction(costmulti,
                                           lambdaa=self._lambdaa, p=self._p)
            c00 = np.min(ct.os.Rescale(costFunc), axis=0)
            c00 = c00 - np.min(c00)
            c00 = (c00 * 255 / np.max(c00)).astype(np.uint8)
            self.finished.emit(multi, costFunc, c00)
        except Exception as e:
            self.error.emit(str(e))


class TrackWorker(QThread):
    """Runs fast_marching off the main thread."""
    finished = pyqtSignal(object, object)   # track_crop, track
    error    = pyqtSignal(str)

    def __init__(self, costFunction, pts_crop_down, pts,
                 downsample_factor: int, y_margin: int, x_margin: int,
                 g11: float, g22: float, g33: float):
        super().__init__()
        self._cost   = costFunction
        self._pcd    = pts_crop_down
        self._pts    = pts
        self._ds     = downsample_factor
        self._ym     = y_margin
        self._xm     = x_margin
        self._g11    = g11
        self._g22    = g22
        self._g33    = g33

    def run(self):
        try:
            tcd = ct.tracking.fast_marching(
                self._cost, self._pcd[0], self._pcd[1],
                g11=self._g11, g22=self._g22, g33=self._g33)
            tcd[0] -= 0.5
            tcd[1] -= 0.5
            tc = tcd.copy()
            tc[0] = tcd[0] * self._ds
            tc[1] = tcd[1] * self._ds
            track = ct.tools.track_crop_to_full(
                tc, self._pts[0], self._pts[1], self._ym, self._xm)
            self.finished.emit(tc, track)
        except Exception as e:
            self.error.emit(str(e))
