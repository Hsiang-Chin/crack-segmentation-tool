# -*- coding: utf-8 -*-
from .layout import Ui_MainWindow
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import numpy as np
from .i18n import tr, set_lang, _LANG


class MainView(Ui_MainWindow):
    """Extends the generated layout with display helpers and i18n wiring.

    Owns nothing but widgets and their visual state — no business logic.
    """

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Folder path field is display-only; populated by controller via dialog
        self.folder_line_edit.setReadOnly(True)
        self.folder_line_edit.setPlaceholderText(tr('lbl_folder_hint'))

        # Language selector in the status bar
        self._lang_label = QtWidgets.QLabel(tr('lbl_language'))
        self._lang_combo = QtWidgets.QComboBox()
        self._lang_combo.addItems(['English', '繁體中文'])
        self._lang_combo.setCurrentIndex(0 if _LANG == 'en' else 1)
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        self.statusbar.addPermanentWidget(self._lang_label)
        self.statusbar.addPermanentWidget(self._lang_combo)

        self.retranslateUi(MainWindow)

    # ── i18n ─────────────────────────────────────────────────────────────────

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(tr('window_title'))
        self.SelectFolderButton.setText(tr('btn_select_folder'))
        self.PreviousImageButton.setText(tr('btn_previous'))
        self.NextImageButton.setText(tr('btn_next'))
        self.label_35.setText(tr('lbl_current_image'))
        self.draw_box_button.setText(tr('btn_draw_box'))
        self.label_29.setText(tr('lbl_class'))
        self.label_36.setText(tr('lbl_class_hint1'))
        self.label_38.setText(tr('lbl_class_hint2'))
        self.clear_boxes_button.setText(tr('btn_clear_boxes'))
        self.label_37.setText(tr('lbl_image_size'))
        self.save_b_button.setText(tr('btn_save_box'))
        self.clear_segmentation_button.setText(tr('btn_clear_segmentation'))
        self.label_33.setText(tr('lbl_seg_color'))
        self.label_39.setText(tr('lbl_seg_width'))
        self.annotation_full_screen_button_3.setText(tr('btn_annotation_fullscreen'))
        self.update_annotation_display_button_3.setText(tr('btn_update_annotation'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), tr('tab_select_image'))
        self.select_points_button.setText(tr('btn_select_end_points'))
        self.label.setText(tr('lbl_image_size_2'))
        self.label_17.setText(tr('lbl_sigmas'))
        self.label_16.setText(tr('lbl_power'))
        self.label_15.setText(tr('lbl_lambda'))
        self.update_os_button.setText(tr('btn_update_os'))
        self.show_os_button.setText(tr('btn_show_os'))
        self.update_cost_button.setText(tr('btn_update_cost'))
        self.midline_track_button.setText(tr('btn_crack_track'))
        self.crack_color_box.setItemText(0, tr('crack_dark'))
        self.crack_color_box.setItemText(1, tr('crack_bright'))
        self.label_5.setText(tr('lbl_downsample'))
        self.update_image_crop_button.setText(tr('btn_update_crop'))
        self.label_2.setText(tr('lbl_color_channel'))
        self.label_3.setText(tr('lbl_x_margin'))
        self.label_4.setText(tr('lbl_y_margin'))
        self.middpoint_update_button.setText(tr('btn_midpoint_update'))
        self.middle_point_button.setText(tr('btn_middle_point'))
        self.wavelet_button.setText(tr('btn_wavelet'))
        self.label_7.setText(tr('lbl_wavelet_size'))
        self.label_9.setText(tr('lbl_inflection'))
        self.label_10.setText(tr('lbl_overlap'))
        self.label_11.setText(tr('lbl_std'))
        self.label_12.setText(tr('lbl_window_size'))
        self.label_13.setText(tr('lbl_mn_order'))
        self.label_19.setText(tr('lbl_track_width'))
        self.update_track_display_button.setText(tr('btn_update_track'))
        self.label_20.setText(tr('lbl_track_color'))
        self.label_21.setText(tr('lbl_x_size'))
        self.label_22.setText(tr('lbl_y_size'))
        self.track_full_screen_button.setText(tr('btn_track_fullscreen'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), tr('tab_tracking'))
        self.edge_mask_button.setText(tr('btn_edge_mask'))
        self.label_23.setText(tr('lbl_filter_size'))
        self.edge_tracks_button.setText(tr('btn_edge_tracks'))
        self.label_24.setText(tr('lbl_track_color_2'))
        self.label_25.setText(tr('lbl_track_width_2'))
        self.edge_tracks_full_screen_button.setText(tr('btn_edge_fullscreen'))
        self.save_current_segment_button.setText(tr('btn_save_segment'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), tr('tab_segmentation'))
        self.draw_segment_button.setText(tr('btn_draw_segment'))
        self.save_manuall_segment_button.setText(tr('btn_save_manual'))
        self.manual_segment_full_screen_button.setText(tr('btn_show_fullscreen'))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), tr('tab_manual'))
        if hasattr(self, '_lang_label'):
            self._lang_label.setText(tr('lbl_language'))

    def _on_language_changed(self, index: int):
        set_lang('en' if index == 0 else 'zh-TW')
        self.retranslateUi(self.MainWindow)

    # ── Display helpers ───────────────────────────────────────────────────────

    def render_image(self, label: QtWidgets.QLabel, image: np.ndarray,
                     grayscale: bool = False):
        """Convert numpy array → QPixmap and display in label."""
        im = np.ascontiguousarray(image.astype(np.uint8))
        fmt = (QImage.Format.Format_Grayscale8 if grayscale
               else QImage.Format.Format_RGB888)
        qimage = QImage(im.data, im.shape[1], im.shape[0],
                        im.strides[0], fmt)
        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(label.width(), label.height(),
                               Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.FastTransformation)
        label.setPixmap(scaled)

    def show_error(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(tr('error_text'))
        msg.setWindowTitle(tr('error_title'))
        msg.exec()

    def set_workflow_state(self, state: str):
        """Set button colours to reflect pipeline progress."""
        RED  = "background-color: red; color: black"
        BLUE = "background-color: lightblue; color: black"
        reset_buttons = [
            self.update_image_crop_button, self.middle_point_button,
            self.middpoint_update_button,  self.update_os_button,
            self.update_cost_button,       self.midline_track_button,
            self.update_track_display_button, self.track_full_screen_button,
            self.edge_mask_button,         self.edge_tracks_button,
            self.edge_tracks_full_screen_button, self.save_current_segment_button,
            self.draw_segment_button,      self.show_os_button,
        ]
        activate = {
            'crop_done':  [self.update_os_button, self.show_os_button],
            'os_done':    [self.update_cost_button, self.show_os_button],
            'cost_done':  [self.midline_track_button],
            'track_done': [self.update_track_display_button,
                           self.track_full_screen_button,
                           self.edge_mask_button],
            'edge_done':  [self.edge_tracks_button],
            'edges_done': [self.edge_tracks_full_screen_button,
                           self.save_current_segment_button],
        }
        if state == 'reset':
            for b in reset_buttons:
                b.setStyleSheet(RED)
        elif state in activate:
            for b in activate[state]:
                b.setStyleSheet(BLUE)

    # ── Color helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def track_color(combo: QtWidgets.QComboBox) -> tuple:
        return {'R': (255, 0, 0), 'G': (0, 255, 0),
                'B': (0, 0, 255), 'W': (255, 255, 255)}.get(
            combo.currentText(), (255, 0, 0))

    @staticmethod
    def boundary_color(combo: QtWidgets.QComboBox) -> tuple:
        return {'R': (1, 0, 0), 'G': (0, 1, 0),
                'B': (0, 0, 1), 'W': (1, 1, 1)}.get(
            combo.currentText(), (1, 0, 0))
