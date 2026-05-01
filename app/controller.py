# -*- coding: utf-8 -*-
import os
import numpy as np
import cv2
import skimage.measure
import matplotlib.pyplot as plt
import cracktools as ct
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt

from .model import CrackModel
from .view import MainView
from .workers import BoundaryWorker, OSWorker, CostWorker, TrackWorker
from .i18n import tr


class CrackController:
    """Connects MainView signals to CrackModel operations."""

    def __init__(self, view: MainView, model: CrackModel):
        self.view = view
        self.model = model

        self._image_gen: int = 0
        self._boundary_worker: BoundaryWorker | None = None
        self._os_worker:       OSWorker | None = None
        self._cost_worker:     CostWorker | None = None
        self._track_worker:    TrackWorker | None = None

        self._connect_signals()
        self.view.set_workflow_state('reset')

    # ── Signal wiring ─────────────────────────────────────────────────────────

    def _connect_signals(self):
        v = self.view
        v.SelectFolderButton.clicked.connect(self.select_folder)
        v.PreviousImageButton.clicked.connect(self.previous_image)
        v.NextImageButton.clicked.connect(self.next_image)
        v.draw_box_button.clicked.connect(self.draw_box)
        v.save_b_button.clicked.connect(self.save_box)
        v.clear_boxes_button.clicked.connect(self.clear_boxes)
        v.clear_segmentation_button.clicked.connect(self.clear_segmentation)
        v.files_list.itemSelectionChanged.connect(self.name_selected)
        v.select_points_button.clicked.connect(self.select_end_points)
        v.update_image_crop_button.clicked.connect(self.update_image_crop)
        v.wavelet_button.clicked.connect(self.check_wavelet)
        v.middle_point_button.clicked.connect(self.select_middle_point)
        v.middpoint_update_button.clicked.connect(self.update_midpoint_image)
        v.update_os_button.clicked.connect(self.update_os)
        v.show_os_button.clicked.connect(self.show_os)
        v.update_cost_button.clicked.connect(self.update_cost)
        v.midline_track_button.clicked.connect(self.midline_tracking)
        v.update_track_display_button.clicked.connect(self.update_track_display)
        v.track_full_screen_button.clicked.connect(self.track_full_screen)
        v.edge_mask_button.clicked.connect(self.edge_mask)
        v.edge_tracks_button.clicked.connect(self.edge_tracking)
        v.edge_tracks_full_screen_button.clicked.connect(self.edge_tracks_full_screen)
        v.save_current_segment_button.clicked.connect(self.save_current_segment)
        v.draw_segment_button.clicked.connect(self.draw_segment)
        v.save_manuall_segment_button.clicked.connect(self.save_manual_segment)
        v.manual_segment_full_screen_button.clicked.connect(self.manual_segment_full_screen)

    # ── Select Image tab ──────────────────────────────────────────────────────

    def select_folder(self):
        start = self.view.folder_line_edit.text() or os.path.expanduser('~')
        dir_ = QFileDialog.getExistingDirectory(
            self.view.MainWindow, tr('dlg_select_folder'), start)
        if not dir_:
            return
        try:
            self.view.folder_line_edit.setText(dir_)
            self.view.files_list.clear()
            self.model.image_names = ct.tools.get_files(
                folder=dir_, formats=['jpg', 'png'], basename=False)
            for filename in self.model.image_names:
                self.view.files_list.addItem(os.path.basename(filename))
            self.model.n = 0
            self.change_image()
        except Exception:
            self.view.show_error()

    def name_selected(self):
        self.model.n = self.view.files_list.currentRow()
        self._reset_state()
        self.change_image()

    def _reset_state(self):
        self.model.reset_state()
        self.view.set_workflow_state('reset')

    def _update_selected_item(self, name: str):
        items = self.view.files_list.findItems(
            name, Qt.MatchFlag.MatchExactly)
        self.view.files_list.setCurrentItem(items[0])

    def change_image(self):
        self._image_gen += 1
        gen = self._image_gen
        m = self.model
        v = self.view

        color = v.boundary_color(v.segment_color_box_2)
        self._update_selected_item(os.path.basename(m.image_names[m.n]))
        m.name = m.image_names[m.n]
        m.ann_name = (os.path.splitext(os.path.splitext(m.name)[0])[0]
                      + '.json')

        # cv2.imread silently fails on Windows paths with non-ASCII chars;
        # np.fromfile uses Python's Unicode I/O instead.
        raw = cv2.imdecode(np.fromfile(m.name, dtype=np.uint8), cv2.IMREAD_COLOR)
        if raw is None:
            v.show_error()
            return
        m.image = raw[:, :, ::-1].astype(np.uint8)
        m.original_image = m.image.copy()
        v.filename_label_2.setText(os.path.basename(m.name))
        v.render_image(v.ImageScreen, m.original_image)

        m.load_annotation()
        anns = m.annotation.get('annotations', {})
        crack_pixels = anns.get('crack_pixels', [])

        if crack_pixels:
            mask = np.zeros(m.image.shape[:2])
            c = np.array(crack_pixels)
            mask[list(c[:, 0]), list(c[:, 1])] = 1

            if self._boundary_worker and self._boundary_worker.isRunning():
                self._boundary_worker.finished.disconnect()
            self._boundary_worker = BoundaryWorker(
                m.original_image, mask, color, gen)
            self._boundary_worker.finished.connect(self._on_boundary_ready)
            self._boundary_worker.start()
        else:
            self._draw_boxes_and_display(gen)

    def _on_boundary_ready(self, result: np.ndarray, gen: int):
        if gen != self._image_gen:
            return
        self.model.image = result
        self._draw_boxes_and_display(gen)

    def _draw_boxes_and_display(self, gen: int):
        if gen != self._image_gen:
            return
        m = self.model
        boxes = m.annotation.get('annotations', {}).get('box', {})
        for key in boxes:
            cls = boxes[key]['class']
            color_cv = {0: (0, 0, 255), 1: (0, 255, 0)}.get(cls, (255, 0, 0))
            bb = np.array(boxes[key]['bounding_box'])
            p0, p1 = (bb[0, 0], bb[0, 1]), (bb[1, 0], bb[1, 1])
            cv2.line(m.image, p0, (p1[0], p0[1]), color_cv, 5)
            cv2.line(m.image, p0, (p0[0], p1[1]), color_cv, 5)
            cv2.line(m.image, p1, (p0[0], p1[1]), color_cv, 5)
            cv2.line(m.image, p1, (p1[0], p0[1]), color_cv, 5)
        if not boxes:
            m.annotation.setdefault('annotations', {})['box'] = {}
        self.view.render_image(self.view.ImageScreen, m.image)

    def next_image(self):
        try:
            self._reset_state()
            self.model.n += 1
            self.change_image()
        except Exception:
            self.view.show_error()

    def previous_image(self):
        try:
            self._reset_state()
            self.model.n -= 1
            self.change_image()
        except Exception:
            self.view.show_error()

    def draw_box(self):
        v = self.view
        m = self.model
        image_size = v.select_image_size_2.value()
        m.bb_pts, _ = ct.tools.Draw().bounding_box(
            m.image[:, :, ::-1], image_size)
        m.bb_pts = np.array(m.bb_pts, dtype=np.int32)
        m.saved = False
        if len(m.bb_pts) == 2:
            p0 = (m.bb_pts[0, 0], m.bb_pts[0, 1])
            p1 = (m.bb_pts[1, 0], m.bb_pts[1, 1])
            cv2.line(m.image, p0, (p1[0], p0[1]), (0, 255, 0), 5)
            cv2.line(m.image, p0, (p0[0], p1[1]), (0, 255, 0), 5)
            cv2.line(m.image, p1, (p0[0], p1[1]), (0, 255, 0), 5)
            cv2.line(m.image, p1, (p1[0], p0[1]), (0, 255, 0), 5)
            v.render_image(v.ImageScreen, m.image)

    def save_box(self):
        v = self.view
        m = self.model
        class_ = v.ClassSpinBox.value()
        if not m.saved:
            m.saved = True
            if len(m.bb_pts) > 0:
                box = m.annotation['annotations']['box']
                existing_keys = np.fromiter(box.keys(), float)
                new_key = (1 if len(existing_keys) == 0
                           else int(np.max(existing_keys) + 1))
                box[new_key] = {'bounding_box': m.bb_pts.tolist(),
                                'class': class_}
                import json
                with open(m.ann_name, 'w') as fp:
                    json.dump(m.annotation, fp)
                print(tr('saved'))
            else:
                print(tr('no_box'))
        self.change_image()

    def clear_boxes(self):
        import json
        self.model.annotation['annotations']['box'] = {}
        with open(self.model.ann_name, 'w') as fp:
            json.dump(self.model.annotation, fp)
        self.change_image()

    def clear_segmentation(self):
        import json
        ann = self.model.annotation['annotations']
        ann['cracks end-points'] = []
        ann['crack_pixels'] = []
        ann['tracks'] = []
        with open(self.model.ann_name, 'w') as fp:
            json.dump(self.model.annotation, fp)
        self.change_image()

    # ── Tracking tab ──────────────────────────────────────────────────────────

    def select_end_points(self):
        v = self.view
        m = self.model
        try:
            image_size = v.select_image_size.value()
            ptss = ct.tools.Draw().points(m.image[:, :, ::-1],
                                          image_size, move_x=0, move_y=0)
            m.end_points = ptss
            points_pairs_list = [ptss[b * 2:b * 2 + 2] for b in range(len(ptss))]
            ok = len(points_pairs_list) == 2
            style = ("background-color: lightblue; color: black" if ok
                     else "background-color: red; color: black")
            v.update_image_crop_button.setStyleSheet(style)
            v.middle_point_button.setStyleSheet(style)
        except Exception:
            v.show_error()
            v.update_image_crop_button.setStyleSheet("background-color: red; color: black")
            v.middle_point_button.setStyleSheet("background-color: red; color: black")

    def update_image_crop(self):
        v = self.view
        m = self.model
        try:
            y_margin = v.y_margin_box.value()
            x_margin = v.x_margin_box.value()
            ds       = v.downsample_factor_box.value()
            ch       = {'R': 0, 'G': 2, 'B': 1}.get(
                v.color_chenel_box.currentText(), 2)
            black_crack = (np.min if v.crack_color_box.currentText()
                           == tr('crack_dark') else np.max)

            if m.end_points == []:
                self.select_end_points()
            pts = m.end_points

            m.image_crop, m.pts_crop = ct.tools.image_crop(
                m.original_image, pts[0], pts[1], pts, y_margin, x_margin)
            m.image_crop_down = skimage.measure.block_reduce(
                m.image_crop, block_size=(ds, ds, 1), func=black_crack, cval=0)
            m.pts_crop_down = [x / ds for x in m.pts_crop]
            m.image_down = skimage.measure.block_reduce(
                m.original_image, block_size=(ds, ds, 1), func=black_crack, cval=0)
            m.pts_down = [x / ds for x in pts]

            gs = np.ascontiguousarray(m.image_crop_down[:, :, ch].astype(np.uint8))
            gs = cv2.circle(gs, (int(m.pts_crop_down[0][0]),
                                 int(m.pts_crop_down[0][1])), 2, (0, 255, 0), 2)
            gs = cv2.circle(gs, (int(m.pts_crop_down[1][0]),
                                 int(m.pts_crop_down[1][1])), 2, (0, 255, 0), 2)
            v.render_image(v.image_crop_down_display, gs, grayscale=True)
            v.x_size_show.display(m.image_crop_down.shape[1])
            v.y_size_show.display(m.image_crop_down.shape[0])
            v.set_workflow_state('crop_done')
        except Exception:
            v.show_error()
            v.update_os_button.setStyleSheet("background-color: red; color: black")

    def check_wavelet(self):
        v = self.view
        try:
            wavelet = ct.os.CheckWavelet(
                window_size=v.wavelet_window_size_box.value(),
                size=v.wavelet_size_box.value(),
                nOrientations=v.wavelet_norientations_box.value(),
                design="N",
                inflectionPoint=v.wavelet_inflection_point_box.value(),
                mnOrder=v.wavelet_mnorder_box.value(),
                splineOrder=3,
                overlapFactor=v.wavelet_overlap_factor_box.value(),
                dcStdDev=v.wavelet_STD_box.value(),
                directional=False,
                display_orientations=[0])[0, :, :]
            wavelet = wavelet - np.min(wavelet)
            wavelet = (wavelet * 254 / np.max(wavelet)).astype(np.uint8)
            v.render_image(v.wavelet_check_display, wavelet, grayscale=True)
        except Exception:
            v.show_error()

    def select_middle_point(self):
        v = self.view
        m = self.model
        try:
            image_size = v.select_image_size.value()
            ds = v.downsample_factor_box.value()
            pt = ct.tools.Draw().points(m.image[:, :, ::-1],
                                        image_size, move_x=0, move_y=0)
            m.mid_pt = (int(pt[0][0] / ds), int(pt[0][1] / ds))
            v.middpoint_update_button.setStyleSheet(
                "background-color: lightblue; color: black")
        except Exception:
            v.show_error()
            v.middpoint_update_button.setStyleSheet(
                "background-color: red; color: black")

    def update_midpoint_image(self):
        v = self.view
        m = self.model
        try:
            ds = v.downsample_factor_box.value()
            ch = {'R': 0, 'G': 2, 'B': 1}.get(
                v.color_chenel_box.currentText(), 2)
            d  = int(v.wavelet_window_size_box.value() / 2)

            if m.mid_pt == []:
                self.select_middle_point()

            if m.image_down is None:
                black_crack = (np.min if v.crack_color_box.currentText()
                               == tr('crack_dark') else np.max)
                m.image_down = skimage.measure.block_reduce(
                    m.original_image, block_size=(ds, ds, 1),
                    func=black_crack, cval=0)

            x0, y0 = int(m.mid_pt[1]), int(m.mid_pt[0])
            mid_image = m.image_down[y0 - d:y0 + d, x0 - d:x0 + d, ch]
            v.render_image(v.middlepoint_display, mid_image, grayscale=True)
        except Exception:
            v.show_error()

    def update_os(self):
        v = self.view
        m = self.model
        try:
            v.os_progress_bar.setValue(0)
            ch = {'R': 0, 'G': 2, 'B': 1}.get(
                v.color_chenel_box.currentText(), 2)
            black_crack = (-1 if v.crack_color_box.currentText()
                           == tr('crack_bright') else 1)
            params = dict(
                size=v.wavelet_size_box.value(),
                nOrientations=v.wavelet_norientations_box.value(),
                design="N",
                inflectionPoint=v.wavelet_inflection_point_box.value(),
                mnOrder=v.wavelet_mnorder_box.value(),
                splineOrder=3,
                overlapFactor=v.wavelet_overlap_factor_box.value(),
                dcStdDev=v.wavelet_STD_box.value(),
                directional=False,
            )
            image_slice = (m.image_crop_down[:, :, ch] / 255 * black_crack)

            if self._os_worker and self._os_worker.isRunning():
                return
            v.update_os_button.setEnabled(False)
            self._os_worker = OSWorker(image_slice, params)
            self._os_worker.finished.connect(self._on_os_ready)
            self._os_worker.error.connect(self._on_worker_error)
            self._os_worker.start()
        except Exception:
            v.show_error()

    def _on_os_ready(self, result):
        self.model.osGFCost = result
        self.view.os_progress_bar.setValue(100)
        self.view.update_os_button.setEnabled(True)
        self.view.set_workflow_state('os_done')

    def show_os(self):
        import plotly.graph_objects as go
        v = self.view
        m = self.model
        ch = [{'R': 0, 'G': 2, 'B': 1}.get(v.color_chenel_box.currentText(), 2)]
        shift = -30
        osGFCost_shift = np.roll(m.osGFCost, shift=shift, axis=0)
        values = osGFCost_shift[:int(m.osGFCost.shape[0] / 2), :, :].real
        X, Y, Z = np.mgrid[:values.shape[0], :values.shape[1], :values.shape[2]]

        yim = np.linspace(0, m.image_crop_down.shape[0], m.image_crop_down.shape[0])
        zim = np.linspace(0, m.image_crop_down.shape[1], m.image_crop_down.shape[1])
        yim, zim = np.meshgrid(yim, zim)
        xim = np.ones(yim.shape) * 0

        a = m.osGFCost.shape[0] / 2 - 1
        b = m.osGFCost.shape[1]
        c = m.osGFCost.shape[2]

        fig = go.Figure(data=go.Volume(
            x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
            value=values.flatten(),
            isomin=np.min(values), isomax=np.max(values),
            opacity=1, opacityscale='min', colorscale='Hot',
            caps=dict(x_show=False, y_show=False, z_show=False, x_fill=1),
        ))
        fig.update_traces(
            lighting=dict(ambient=0.4, diffuse=0.9, fresnel=0.8,
                          roughness=0.5, specular=0.05),
            selector=dict(type='volume'))
        fig.update_traces(
            surface=dict(count=5, fill=1, pattern='all', show=True),
            selector=dict(type='volume'))
        r = m.image_crop.shape[0] / m.image_crop_down.shape[1]
        fig.update_layout(scene_aspectmode='manual',
                          scene_aspectratio=dict(x=0.5, y=r, z=1))
        fig.update_layout(scene_xaxis_showticklabels=False,
                          scene_yaxis_showticklabels=False,
                          scene_zaxis_showticklabels=False)
        fig.add_surface(x=xim, y=yim, z=zim,
                        surfacecolor=m.image_crop_down[:, :, ch][:, :, 0].T,
                        colorscale='gray', showscale=False)
        fig.add_scatter3d(
            x=[0, 0, a, a, 0, 0, a, a, a, 0, 0, 0, 0, a, a, a],
            y=[0, b, b, 0, 0, 0, 0, b, b, b, b, 0, b, b, 0, 0],
            z=[0, 0, 0, 0, 0, c, c, c, 0, 0, c, c, c, c, c, 0],
            mode='lines', line=dict(color='black', width=2))
        fig.update_layout(
            scene=dict(xaxis=dict(showbackground=False),
                       yaxis=dict(showbackground=False),
                       zaxis=dict(showbackground=False)),
            scene_camera=dict(up=dict(x=1, y=0, z=0),
                              center=dict(x=-0.15, y=0, z=0),
                              eye=dict(x=0.085 * 4.5, y=0.23 * 4.5, z=0.2 * 4.5)),
            font=dict(size=60))
        fig.update_traces(showscale=True, selector=dict(type='volume'))
        fig.show()

    def update_cost(self):
        v = self.view
        m = self.model
        try:
            v.update_cost_bar.setValue(0)
            lambdaa = v.lambda_box.value()
            p       = v.power_box.value()
            sigmas  = [float(s) for s in v.sigmas_line_edit.text().split(',')]

            if self._cost_worker and self._cost_worker.isRunning():
                return
            v.update_cost_button.setEnabled(False)
            self._cost_worker = CostWorker(
                m.osGFCost, ksi=1, sigmas=sigmas, lambdaa=lambdaa, p=p)
            self._cost_worker.finished.connect(self._on_cost_ready)
            self._cost_worker.error.connect(self._on_worker_error)
            self._cost_worker.start()
        except Exception:
            v.show_error()

    def _on_cost_ready(self, multiscale, costFunc, c00: np.ndarray):
        m = self.model
        v = self.view
        m.multiscalecostLIFExtReg = multiscale
        m.costFunction = costFunc
        v.update_cost_bar.setValue(100)
        v.update_cost_button.setEnabled(True)
        v.render_image(v.cost_display, c00, grayscale=True)
        v.set_workflow_state('cost_done')

    def midline_tracking(self):
        v = self.view
        m = self.model
        try:
            v.tracking_bar.setValue(0)
            ds       = v.downsample_factor_box.value()
            y_margin = v.y_margin_box.value()
            x_margin = v.x_margin_box.value()
            g11, g22, g33 = (v.g11_box.value(),
                             v.g22_box.value(),
                             v.g33_box.value())

            if self._track_worker and self._track_worker.isRunning():
                return
            v.midline_track_button.setEnabled(False)
            self._track_worker = TrackWorker(
                m.costFunction, m.pts_crop_down, m.end_points,
                ds, y_margin, x_margin, g11, g22, g33)
            self._track_worker.finished.connect(self._on_track_ready)
            self._track_worker.error.connect(self._on_worker_error)
            self._track_worker.start()
        except Exception:
            v.show_error()

    def _on_track_ready(self, track_crop, track):
        m = self.model
        v = self.view
        m.track_crop = track_crop
        m.track      = track
        v.midline_track_button.setEnabled(True)
        v.tracking_bar.setValue(100)
        color = v.track_color(v.track_color_box)
        w   = v.track_width_box.value()
        pts = (np.array(track_crop).transpose(1, 0)
               .reshape(-1, 1, 2).astype(np.int32))
        im = cv2.polylines(m.image_crop.astype(np.uint8).copy(),
                           [pts], False, color, w)
        v.render_image(v.track_display, im)
        v.set_workflow_state('track_done')

    def update_track_display(self):
        v = self.view
        m = self.model
        try:
            w     = v.track_width_box.value()
            color = v.track_color(v.track_color_box)
            pts   = (np.array(m.track_crop).transpose(1, 0)
                     .reshape(-1, 1, 2).astype(np.int32))
            im = cv2.polylines(m.image_crop.astype(np.uint8).copy(),
                               [pts], False, color, w)
            v.render_image(v.track_display, im)
        except Exception:
            v.show_error()

    def track_full_screen(self):
        v = self.view
        m = self.model
        try:
            w = v.track_width_box.value()
            c = {'R': 'r', 'G': 'g', 'B': 'b', 'W': 'w'}.get(
                v.track_color_box.currentText(), 'r')
            plt.imshow(m.image.astype(np.uint8))
            plt.plot(m.track[0], m.track[1], color=c, linewidth=w)
            plt.show()
        except Exception:
            v.show_error()

    # ── Segmentation tab ──────────────────────────────────────────────────────

    def edge_mask(self):
        v = self.view
        m = self.model
        try:
            half = int(v.edge_filter_size_box.value() / 2)
            y_margin = v.y_margin_box.value()
            x_margin = v.x_margin_box.value()
            black_crack = (-1 if v.crack_color_box.currentText()
                           == tr('crack_bright') else 1)
            ch = {'R': 0, 'G': 2, 'B': 1}.get(
                v.color_chenel_box.currentText(), 2)
            m.edge_mask1, m.edge_mask2 = ct.segmentation.edge_masks(
                m.original_image[:, :, ch] * black_crack,
                np.array(m.track), window_half_size=half)
            m.edge_mask1_crop, _ = ct.tools.image_crop(
                m.edge_mask1[:, :, np.newaxis],
                m.end_points[0], m.end_points[1],
                m.end_points, y_margin, x_margin)
            m.edge_mask2_crop, _ = ct.tools.image_crop(
                m.edge_mask2[:, :, np.newaxis],
                m.end_points[0], m.end_points[1],
                m.end_points, y_margin, x_margin)

            em = m.edge_mask1_crop - np.min(m.edge_mask1_crop)
            em = (em * 255 / np.max(em)).astype(np.uint8)
            v.render_image(v.edge_map_display, em, grayscale=True)
            v.set_workflow_state('edge_done')
        except Exception:
            v.show_error()
            v.edge_tracks_button.setStyleSheet("background-color: red; color: black")

    def edge_tracking(self):
        v = self.view
        m = self.model
        try:
            ch = {'R': 0, 'G': 2, 'B': 1}.get(
                v.color_chenel_box.currentText(), 2)
            y_margin = v.y_margin_box.value()
            x_margin = v.x_margin_box.value()
            w     = v.edge_track_width_box.value()
            color = v.track_color(v.edge_track_color_box)
            mu, l, p = (v.mu_box.value(),
                        v.l_box.value(),
                        v.p_box.value())

            te1, te2 = ct.segmentation.edges_tracking(
                m.image_crop[:, :, ch], m.pts_crop,
                m.edge_mask1_crop, m.edge_mask2_crop,
                mu=mu, l=l, p=p)
            for t in (te1, te2):
                t[:] = t[::-1]
                t[0] -= 0.5
                t[1] -= 0.5

            m.track_e1 = ct.tools.track_crop_to_full(
                te1, m.end_points[0], m.end_points[1], y_margin, x_margin)
            m.track_e2 = ct.tools.track_crop_to_full(
                te2, m.end_points[0], m.end_points[1], y_margin, x_margin)

            pts1 = np.array(te1).transpose(1, 0).reshape(-1, 1, 2).astype(np.int32)
            pts2 = np.array(te2).transpose(1, 0).reshape(-1, 1, 2).astype(np.int32)
            im = m.image_crop.astype(np.uint8).copy()
            im = cv2.polylines(im, [pts1], False, color, w)
            im = cv2.polylines(im, [pts2], False, color, w)
            v.render_image(v.edge_tracks_display, im)
            v.set_workflow_state('edges_done')
        except Exception:
            v.show_error()
            v.edge_tracks_full_screen_button.setStyleSheet(
                "background-color: red; color: black")
            v.save_current_segment_button.setStyleSheet(
                "background-color: red; color: black")

    def edge_tracks_full_screen(self):
        v = self.view
        m = self.model
        try:
            w = v.edge_track_width_box.value()
            c = {'R': 'r', 'G': 'g', 'B': 'b', 'W': 'w'}.get(
                v.edge_track_color_box.currentText(), 'r')
            plt.imshow(m.image.astype(np.uint8))
            plt.plot(m.track_e1[0], m.track_e1[1], color=c, linewidth=w)
            plt.plot(m.track_e2[0], m.track_e2[1], color=c, linewidth=w)
            plt.show()
        except Exception:
            v.show_error()

    def save_current_segment(self):
        v = self.view
        m = self.model
        try:
            edge_x = np.concatenate((m.track_e1[1][::-1], m.track_e2[1]))
            edge_y = np.concatenate((m.track_e1[0][::-1], m.track_e2[0]))
            mask_fm = ct.segmentation.create_mask(m.image, edge_y, edge_x)
            m.mask.append(mask_fm)
            m.cracks_stored_endpoints[len(m.cracks_stored_endpoints)] = [
                m.end_points[0].tolist(), m.end_points[1].tolist()]
            m.crack_tracks[len(m.crack_tracks)] = [list(x) for x in m.track]

            total = np.sum(np.array(m.mask), axis=0)
            total = (total >= 1).astype(np.uint8) * 255
            v.render_image(v.all_segments_display, total, grayscale=True)

            pts1 = np.array(m.track_e1).transpose(1, 0).reshape(-1, 1, 2).astype(np.int32)
            pts2 = np.array(m.track_e2).transpose(1, 0).reshape(-1, 1, 2).astype(np.int32)
            im = m.image.astype(np.uint8).copy()
            im = cv2.polylines(im, [pts1], False, (0, 255, 0), 1)
            im = cv2.polylines(im, [pts2], False, (0, 255, 0), 1)
            m.image = im
            self._save_annotation()
        except Exception:
            v.show_error()

    # ── Manual segment tab ────────────────────────────────────────────────────

    def draw_segment(self):
        v = self.view
        m = self.model
        try:
            image_size = v.select_image_size.value()
            x, y = ct.tools.Draw().counturs(m.image[:, :, ::-1], image_size)
            if len(x) == 0:
                return
            x = np.concatenate([x, np.array(x[0]).reshape(1)])
            y = np.concatenate([y, np.array(y[0]).reshape(1)])
            m.manuall_x = np.array(x)
            m.manuall_y = np.array(y)
            pts = (np.array([x, y]).transpose(1, 0)
                   .reshape(-1, 1, 2).astype(np.int32))
            im = cv2.polylines(m.image.astype(np.uint8).copy(),
                               [pts], False, (0, 255, 0), 1)
            v.render_image(v.manual_segment_screen, im)
        except Exception:
            v.show_error()

    def manual_segment_full_screen(self):
        m = self.model
        try:
            plt.imshow(m.image.astype(np.uint8))
            plt.plot(m.manuall_x, m.manuall_y, 'r', linewidth=1)
            plt.show()
        except Exception:
            self.view.show_error()

    def save_manual_segment(self):
        v = self.view
        m = self.model
        try:
            mask_fm = ct.segmentation.create_mask(
                m.image, m.manuall_x, m.manuall_y)
            m.mask.append(mask_fm)
            total = np.sum(np.array(m.mask), axis=0)
            total = (total >= 1).astype(np.uint8) * 255
            pts = (np.array([m.manuall_x, m.manuall_y])
                   .transpose(1, 0).reshape(-1, 1, 2).astype(np.int32))
            im = cv2.polylines(m.image.astype(np.uint8).copy(),
                               [pts], False, (0, 255, 0), 1)
            m.image = im
            self._save_annotation()
        except Exception:
            v.show_error()

    # ── Annotation persistence ────────────────────────────────────────────────

    def _save_annotation(self):
        try:
            self.model.save_annotation()
            self.change_image()
            self.view.set_workflow_state('reset')
        except Exception:
            self.view.show_error()

    # ── Worker error handler ──────────────────────────────────────────────────

    def _on_worker_error(self, msg: str):
        print(f"Worker error: {msg}")
        self.view.show_error()
        for btn in (self.view.update_os_button,
                    self.view.update_cost_button,
                    self.view.midline_track_button):
            btn.setEnabled(True)
