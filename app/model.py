# -*- coding: utf-8 -*-
import json
import os
import numpy as np


class CrackModel:
    """Holds all persistent application state and handles annotation I/O."""

    def __init__(self):
        # File/image list
        self.image_names: list = []
        self.n: int = -1

        # Current image data
        self.image: np.ndarray | None = None
        self.original_image: np.ndarray | None = None
        self.name: str = ''
        self.ann_name: str = ''
        self.annotation: dict = {}

        # Annotation interaction state
        self.bb_pts: np.ndarray = np.array([])
        self.saved: bool = False
        self.end_points: list = []
        self.mid_pt: list = []
        self.mask: list = []
        self.crack_tracks: dict = {}
        self.cracks_stored_endpoints: dict = {}

        # Processed data – crop / downsample
        self.image_crop: np.ndarray | None = None
        self.pts_crop: list | None = None
        self.image_crop_down: np.ndarray | None = None
        self.pts_crop_down: list | None = None
        self.image_down: np.ndarray | None = None
        self.pts_down: list | None = None

        # Pipeline results
        self.osGFCost = None
        self.multiscalecostLIFExtReg = None
        self.costFunction = None
        self.track_crop = None
        self.track = None
        self.track_e1 = None
        self.track_e2 = None
        self.edge_mask1: np.ndarray | None = None
        self.edge_mask2: np.ndarray | None = None
        self.edge_mask1_crop: np.ndarray | None = None
        self.edge_mask2_crop: np.ndarray | None = None
        self.manuall_x: np.ndarray | None = None
        self.manuall_y: np.ndarray | None = None

    # ── State management ──────────────────────────────────────────────────────

    def reset_state(self):
        self.mid_pt = []
        self.end_points = []
        self.mask = []
        self.crack_tracks = {}
        self.cracks_stored_endpoints = {}

    # ── Annotation I/O ────────────────────────────────────────────────────────

    def load_annotation(self):
        if os.path.exists(self.ann_name):
            with open(self.ann_name) as f:
                self.annotation = json.load(f)
        else:
            self.annotation = {
                'image_name': self.name,
                'annotations': {
                    'cracks end-points': [],
                    'crack_pixels': [],
                    'tracks': [],
                    'box': {},
                },
            }

    def save_annotation(self):
        self.annotation['annotations']['cracks end-points'] = \
            self.cracks_stored_endpoints
        m = np.sum(np.array(self.mask), axis=0)
        crack_pixels = np.argwhere(m >= 1).tolist()
        self.annotation['annotations']['crack_pixels'] = crack_pixels
        self.annotation['annotations']['tracks'] = self.crack_tracks
        with open(self.ann_name, 'w') as f:
            json.dump(self.annotation, f)
