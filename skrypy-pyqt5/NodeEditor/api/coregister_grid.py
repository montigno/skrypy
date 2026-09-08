import sys
import nibabel as nib
from nibabel.processing import resample_from_to
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import numpy as np
import pyvista as pv
from scipy.ndimage import binary_erosion
from scipy.ndimage import binary_fill_holes
import matplotlib
import os
import json
import re
import vtk
import threading

from vtkmodules.vtkRenderingAnnotation import vtkAnnotatedCubeActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QSlider, QComboBox, QSizePolicy,
    QPushButton, QListWidget, QListWidgetItem, QAbstractItemView, QMainWindow,
    QLineEdit, QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.Qt import QImage, QMenu


VERSION_OVER = 1.1

app = QApplication(sys.argv)

# =========================================================
# LOADING FILES
# =========================================================

paths = json.loads(sys.argv[1])

# =========================================================
# RESAMPLING DATA
# =========================================================

if not paths:
    exit()

print("Starting ......")

def sanity_check(img):
    print("shape:", img.shape)
    print("zoom:", img.header.get_zooms())
    print("orientation:", nib.orientations.aff2axcodes(img.affine))

    if img.shape[0] == 1 or img.shape[1] == 1 or img.shape[2] == 1:
        print("volume dégénéré (slice 2D déguisée en 3D)")

def to_3d_nifti(img, number, time_index=0, channel_index=0):

    # sanity_check(img)

    # data = img.get_fdata(dtype=np.float32)
    data = np.asarray(img.dataobj, dtype=np.float32)

    if data.ndim == 3:
        data_3d = data

    elif data.ndim == 4:
        print(f"img {number}: 4D image! 4th dimension indexing set to 0")
        data_3d = data[..., time_index]

    elif data.ndim == 5:
        print(f"img {number}: 5D image! 4th and 5th dimension indexing set to 0")
        data_3d = data[..., time_index, channel_index]

    else:
        raise ValueError(f"Unsupported ndim={data.ndim}")

    # IMPORTANT :create a clean header 3D
    new_header = img.header.copy()

    # force dimensions 3D
    new_header.set_data_shape(data_3d.shape)

    img_3d = nib.Nifti1Image(
        np.ascontiguousarray(data_3d, dtype=np.float32),
        affine=img.affine,
        header=new_header
    )

    return img_3d

def ensure_min_thickness(img):
    data = img.get_fdata(dtype=np.float32)

    shape = list(data.shape)

    for ax in range(3):
        if shape[ax] == 1:
            data = np.repeat(data, 2, axis=ax)
            shape[ax] = 2

    return nib.Nifti1Image(
        data,
        img.affine,
        img.header
    )

def get_world_corners(img):
    shape = img.shape[:3]
    corners = np.array(list(product(
        [0, shape[0]-1],
        [0, shape[1]-1],
        [0, shape[2]-1]
    )))
    return nib.affines.apply_affine(img.affine, corners)

# raws = [to_3d_nifti(nib.load(p)) for p in paths]

raws = [
    ensure_min_thickness(
        to_3d_nifti(nib.load(p), i)
    )
    for i, p in enumerate(paths)
]

all_corners = np.vstack([get_world_corners(img) for img in raws])

world_min = all_corners.min(axis=0)
world_max = all_corners.max(axis=0)

# --------------------------------------------------
# CIBLE : isotrope commune
# --------------------------------------------------

zooms = np.array([img.header.get_zooms()[:3] for img in raws])

# robust isotropic spacing (évite upsampling excessif)
target_spacing = np.median(zooms)
# target_spacing = np.min(zooms)


print("Target isotropic spacing:", target_spacing)

# --------------------------------------------------
# Grid cible isotrope
# --------------------------------------------------

target_shape = np.ceil((world_max - world_min) / target_spacing).astype(int)

target_affine = np.array([
    [target_spacing, 0, 0, world_min[0]],
    [0, target_spacing, 0, world_min[1]],
    [0, 0, target_spacing, world_min[2]],
    [0, 0, 0, 1]
])

target = (tuple(target_shape), target_affine)

# --------------------------------------------------
# Resampling ALL images into same isotropic space
# --------------------------------------------------

def do_resample(args):
    img, target, order = args
    return resample_from_to(img, target, order)

print("Resampling in progress... please wait")
with ProcessPoolExecutor() as ex:
    resampled_files = list(
        ex.map(
            do_resample,
            [(img,target,int(sys.argv[2])) for img in raws]
        )
    )

# resampled_files = []
#
# for i, img in enumerate(raws):
#     print(f"Resampling img {i}", flush=True)
#
#     resampled = resample_from_to(
#         img,
#         target,
#         order=int(sys.argv[2]) # linear interpolation (safe default) has to be in the range 0-5
#     )
#     # sh = resampled.shape
#     # zm = resampled.header.get_zooms()
#     # fov = tuple(x * y for x, y in zip(sh, zm))
#     # print(sh, fov)
#     # print(resampled.get_fdata(dtype=np.float32).min(), resampled.get_fdata(dtype=np.float32).max())
#     resampled_files.append(resampled)

# =========================================================
# LOAD DATA
# =========================================================
vols, raw_vols = [], []

for img in resampled_files:
    # img = nib.load(p)
    # data = img.get_fdata()
    data = np.asarray(img.dataobj)
    data[np.isnan(data)] = 0
    # data = np.transpose(data, (2, 1, 0))  # (Z, Y, X)
    # data = np.flip(data, axis=2)  # ou data[::-1, :, :]
    # data = np.flip(data, axis=0)
    # data = np.flip(data, axis=1)

    while data.ndim > 3:
        data = data[..., 0]

    data = data.astype(np.float32)
    raw_vols.append(data)

    dmin, dmax = data.min(), data.max()
    data = (data - dmin) / (dmax - dmin + 1e-8)
    
    # p1 = np.percentile(data, 1)
    # p99 = np.percentile(data, 99)
    # data = np.clip(data, p1, p99)
    # data = (data - p1) / (p99 - p1 + 1e-8)

    vols.append(data)

shape = vols[0].shape
delta_y, delta_z = shape[1], shape[2]
print("shape of the 1st:", shape)

# =========================================================
# MODE VIEW
# =========================================================

mode = "Radiological"

# =========================================================
# ORIENTATIONS VIEW
# =========================================================

axes = ["XY", "XZ", "YZ"]


# =========================================================
# STATE
# =========================================================

class State:
    def __init__(self):

        self.v = np.array(shape) // 2
        self.window = 1.0
        self.level = 0.5
        self.alpha = 0.40

        self.zoom = {
            "XY": 1.0,
            "XZ": 1.0,
            "YZ": 1.0
        }

        self.pan = {
            "XY": np.array([0, 0], dtype=float),
            "XZ": np.array([0, 0], dtype=float),
            "YZ": np.array([0, 0], dtype=float),
        }

state = State()

# =========================================================
# COLORMAPS LIST
# =========================================================

def get_cmap_list():
    return ["gray", "hot", "turbo", "bone", "jet", "hsv", "prism", "rainbow", "copper"]


# =========================================================
# WINDOW / LEVEL
# =========================================================

def window_level(img, window, level):
    minv = level - window / 2
    maxv = level + window / 2

    img = np.clip(img, minv, maxv)
    img = (img - minv) / (maxv - minv + 1e-8)

    return img


# =========================================================
# LABELS
# =========================================================

def get_anatomical_labels(axis):

    return {
        "XY": {"top": "A", "bottom": "P", "left": "L" if mode == "Radiological" else "R", "right": "R" if mode == "Radiological" else "L"},
        "XZ": {"top": "S", "bottom": "I", "left": "L" if mode == "Radiological" else "R", "right": "R" if mode == "Radiological" else "L"},
        "YZ": {"top": "S", "bottom": "I", "left": "P", "right": "A"}
    }[axis]


def get_orientation_labels(axis):
        return {
            "XY": "Axis 0",
            "XZ": "Axis 1",
            "YZ": "Axis 2"
            }[axis]

    # return {
    #         "XY": "Axial (human)\nCoronal (rodent)\n",
    #         "XZ": "Coronal (human)\nAxial (rodent)\n",
    #         "YZ": "Sagittal\n"
    #         }[axis]

def get_zoom_labels(axis):
    return {
            "XY": "zoom A",
            "XZ": "zoom C",
            "YZ": "zoom S"
            }[axis]
# =========================================================
# HELPERS
# =========================================================

def clamp(v):
    return np.clip(v, 0, np.array(shape) - 1)


LUT = None


def create_lut(name="gray"):
    cmap = matplotlib.colormaps[name]
    return (cmap(np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)


LUT = create_lut("gray")


def to_qimage(img2d):
    """
    img2d: float32 [0..1]
    """

    # 1. scale to 0–255
    img8 = (img2d * 255).astype(np.uint8)

    # 2. LUT mapping (FAST)
    rgb = LUT[img8]   # shape (H, W, 3)

    # 3. QImage (zero copy buffer)
    h, w, _ = rgb.shape

    qimg = QImage(
        rgb.data,
        w,
        h,
        rgb.strides[0],
        QImage.Format_RGB888
    )

    # return qimg.copy()  # important safety Qt

    qimg.ndarray = rgb
    return qimg
# =========================================================
# VIEWPORT (PRO RESIZE SAFE)
# =========================================================

class Viewport(QLabel):

    def __init__(self, col, axis, parent):
        super().__init__()

        self.col = col
        self.axis = axis
        self.parent = parent
        self.detached = False

        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self.setStyleSheet("""
            background-color: rgb(0,0,0);
            """)

        # self.setMinimumSize(250, 250)

        # self.setSizePolicy(
        #     QSizePolicy.Expanding,
        #     QSizePolicy.Expanding
        #     )

        # self.setContentsMargins(1, 1, 1, 1)

        self.pix = None
        self._img_w = 1
        self._img_h = 1

        self._draw_rect = (0, 0, 1, 1)
        
        self.scaled_cache = {}

    def set_image(self, pix):
        self.pix = pix
        self._img_w = pix.width()
        self._img_h = pix.height()
        # nouvelle image → cache invalide
        self.scaled_cache.clear()
        self.update()

    def paintEvent(self, event):

        global delta_y, delta_z

        if self.pix is None:
            return

        painter = QPainter(self)

        margin = -20
        if self.axis == 'XY':
            width = self.width()
            target_size = self.height()
            height = int(self.pix.height() * target_size / self.pix.width())
            delta_y = height
            # print("XY, width, height, delta_y:", self.col, self.width(), self.height(), width, height, delta_y)
        elif self.axis == 'XZ':
            width = self.width()
            target_size = self.height()
            height = int(self.pix.height() * target_size / self.pix.width())
            delta_z = height
            # print("XZ, width, height, delta_z:", self.col, self.width(), self.height(), width, height, delta_z)
        elif self.axis == 'YZ':
            width = self.width()
            target_size = self.height()
            height = int(self.pix.height() * target_size / self.pix.width())
        # elif self.axis == 'YZ':
        #     width = self.width()
        #     target_size = delta_y
        #     height = int(self.pix.height() * target_size / self.pix.width())
            # print("YZ, width, height", self.col, self.width(), self.height(), width, height, delta_y, delta_z)

        zoom = state.zoom[self.axis]

        # scaled = self.pix.scaled(
        #     int((width + margin) * zoom),
        #     int((height + margin) * zoom),
        #     Qt.KeepAspectRatio,
        #     Qt.SmoothTransformation
        # )
        
        cache_key = (
            round(zoom, 2),
            width,
            height
        )
        
        if cache_key not in self.scaled_cache:
        
            self.scaled_cache[cache_key] = self.pix.scaled(
                int((width + margin) * zoom),
                int((height + margin) * zoom),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        # if len(self.scaled_cache) > 30:
        #     self.scaled_cache.clear()
        scaled = self.scaled_cache[cache_key]
        
        self.pan = state.pan[self.axis]
        
        x = (self.width() - scaled.width()) // 2 + int(self.pan[0])
        y = (self.height() - scaled.height()) // 2 + int(self.pan[1])

        # STORE REAL IMAGE RECT (IMPORTANT)
        self._draw_rect = (x, y, scaled.width(), scaled.height())
        # painter.fillRect(self.rect(), Qt.black)

        painter.drawPixmap(x, y, scaled)

        painter.end()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return width

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.parent.auto_contrast_view(self)
            # self.parent.auto_contrast_column(self.col)
            return
        elif e.button() == Qt.LeftButton:
            self.parent.on_mouse(self, e)
        elif e.button() == Qt.MiddleButton:
            self.parent.start_pan(self, e)
            # self.parent.on_middle_drag(self, e)
            
    # def mouseMoveEvent(self, e):
    #     self.parent.on_mouse_move(self, e)

    def mouseMoveEvent(self, e):
        if self.parent.dragging:
            self.parent.on_mouse(self, e)
        elif self.parent.moving:
            self.parent.on_mouse_move(self, e)

    def mouseReleaseEvent(self, e):
        self.parent.stop_pan()
        self.parent.dragging = False
        self.parent.moving = False
        self.parent.last_mouse_pos = None

    # def mouseDoubleClickEvent(self, e):
    #     print(self.col, self.axis)
    #     self.open_second_window()
        # return super().mouseDoubleClickEvent(*args, **kwargs)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = 1 if delta > 0 else -1

        v = state.v.copy()

        if self.axis == "XY":
            v[2] += step   # slice Z
        elif self.axis == "XZ":
            v[1] += step   # slice Y
        elif self.axis == "YZ":
            v[0] += step   # slice X

        state.v = clamp(v)

        self.parent.update_all()
        event.accept()

# =========================================================
# MAIN VIEWER
# =========================================================
    # def open_second_window(self):
    #     # Créer une nouvelle fenêtre
    #     self.second_window = QMainWindow()
    #     self.second_window.setWindowTitle("Fenêtre de duplication")
    #     self.second_window.setGeometry(500, 100, 400, 300)
    #
    #     new_label = self
    #     new_label.setAlignment(self.alignment())
    #
    #     # Layout pour la deuxième fenêtre
    #     layout = QVBoxLayout()
    #     layout.addWidget(new_label)
    #
    #     container = QWidget()
    #     container.setLayout(layout)
    #     self.second_window.setCentralWidget(container)
    #
    #     # Afficher la deuxième fenêtre
    #     self.second_window.show()
class PACSViewer(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"COREGISTER Alignment - {VERSION_OVER}")
        self.setMinimumSize(600, 600)
        # self.setStyleSheet("""
        #     background-color: rgb(30,30,30);
        #     """)
        self.fullscreen_view = None  # Déjà présent
        self.original_grid_position = {}  # Nouveau : stocke la position 
        self.dragging = False
        self.moving = False
        self.last_mouse_pos = None
        self.mask = None
        self.column_titles = []
        
        # cache rendu
        self.render_cache = {}

        self.root = QVBoxLayout()
        self.setLayout(self.root)

        # sliders
        self.slider_window = QSlider(Qt.Horizontal)
        self.slider_level = QSlider(Qt.Horizontal)

        self.slider_window.setRange(1, 200)
        self.slider_level.setRange(0, 100)

        self.slider_window.setValue(100)
        self.slider_level.setValue(50)

        self.slider_window.valueChanged.connect(self.update_all)
        self.slider_level.valueChanged.connect(self.update_all)

        # labels valeurs
        self.label_window = QLabel("W: 1.00")
        self.label_level = QLabel("L: 0.50")

        self.label_window.setStyleSheet("color: black; font-weight: bold;")
        self.label_level.setStyleSheet("color: black; font-weight: bold;")

        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setRange(0, 100)
        self.slider_alpha.setValue(40)
        self.slider_alpha.setEnabled(False)
        self.slider_alpha.valueChanged.connect(self.update_all)
        self.label_alpha = QLabel("A: 0.40")
        self.label_alpha.setStyleSheet("color: black; font-weight: bold;")

        # recenter button
        self.btn_center = QPushButton("Recenter")
        self.btn_center.clicked.connect(self.recenter_crosshair)

        # group contrast
        self.btn_averagecontrast = QPushButton("Average Contrast")
        self.btn_averagecontrast.clicked.connect(self.average_contrast)

        # combobox (COLORMAP)
        self.combo_cmap = QComboBox()
        self.combo_cmap.setToolTip("Color map")
        self.combo_cmap.addItems(get_cmap_list())
        self.combo_cmap.currentTextChanged.connect(self.change_cmap)

        # combobox (VIEW)
        self.view = QComboBox()
        self.view.setToolTip("View mode")
        self.view.addItems(["Radiological", "Neurological"])
        self.view.currentTextChanged.connect(self.change_mode)

        # ROI or mask
        self.roi_mask = QComboBox()
        self.roi_mask.setToolTip("ROI or mask for Atlas")
        self.roi_mask.addItems(["mask", "ROI"])
        self.roi_mask.currentTextChanged.connect(self.change_roi_mask)

        # combobox (ATLAS)
        self.atlas = QComboBox()
        self.atlas.addItem("None")
        self.atlas.setItemData(self.atlas.count() - 1, -1, Qt.UserRole)
        self.atlas.setToolTip("select the atlas containing its label file")
        self.atlas.currentIndexChanged.connect(self.select_atlas)
        
        # Overlay
        self.btn_overlay = QPushButton("Overlay")
        self.btn_overlay.clicked.connect(self.show_overlay)

        self.col_atlas = None
        self.structure_num = []
        self.structure_list = []

        self.zoom_sliders = {}

        sliders = QHBoxLayout()
        sliders.addWidget(QLabel("Window"))
        sliders.addWidget(self.slider_window)
        sliders.addWidget(self.label_window)
        sliders.addWidget(QLabel("Level"))
        sliders.addWidget(self.slider_level)
        sliders.addWidget(self.label_level)
        sliders.addWidget(QLabel("Alpha"))
        sliders.addWidget(self.slider_alpha)
        sliders.addWidget(self.label_alpha)
        sliders.addWidget(self.btn_center)
        sliders.addWidget(self.btn_averagecontrast)
        sliders.addWidget(self.combo_cmap)
        sliders.addWidget(self.view)
        sliders.addWidget(self.roi_mask)
        sliders.addWidget(self.atlas)
        sliders.addWidget(self.btn_overlay)

        self.root.addLayout(sliders, 0)
        self.root.setAlignment(sliders, Qt.AlignTop)

        # =====================================================
        # List of visible Image
        # =====================================================
        self.image_list = QListWidget()
        self.image_list.setMinimumWidth(600)
        self.image_list.setMinimumHeight(200)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.show_context_menu)

        self.visible_images = [True] * len(paths)

        for i, path in enumerate(paths):
            item = QListWidgetItem(os.path.basename(path))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, i)
            self.image_list.addItem(item)

        self.image_list.itemChanged.connect(self.change_image_visibility)
        self.image_list.currentRowChanged.connect(self.changeTitleColor)

        # =====================================================
        # MAIN HORIZONTAL LAYOUT
        # =====================================================

        main_area = QHBoxLayout()
        self.root.addLayout(main_area, 1)

        # =====================================================
        # Explanation text LAYOUT
        # =====================================================

        explan_txt = (
            "Left button clicked and mouse movement: <b>crosshair movement</b><br>"
            "Wheel button clicked and mouse movement: <b>image movement</b><br>"
            "Wheel movement: <b>moving from slice to slice</b><br>"
            "Right button clicked: <b>automatic image contrast under the mouse</b><br>"
            "Double-clicking on an image allows for <b>a larger view in a window.</b><br>"
        )
        layout_expl = QHBoxLayout()
        layout_expl.addWidget(self.image_list)
        layout_expl.addWidget(QLabel(explan_txt), alignment=Qt.AlignLeft)
        container = QWidget()
        container.setLayout(layout_expl)
        self.root.addStretch()
        self.root.addWidget(container, alignment=Qt.AlignHCenter)
        self.root.addStretch()

        # -----------------------------------------------------
        # IMAGE GRID
        # -----------------------------------------------------

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(1)

        # titles
        self.grid.setRowStretch(0, 0)

        # # images
        # for r in range(0, 3):
        #     self.grid.setRowStretch(r, 1)

        # labels
        # self.grid.setColumnStretch(0, 0)

        # columns volumes

        self.label_value, self.button_3D, self.button_ortho = [], [], []
        # for c in range(1, len(vols) + 1):
        #     layout_bottom = QHBoxLayout()
        #     self.grid.setColumnStretch(c, 3)
        #     lab_val = QLabel()
        #     lab_val.setAlignment(Qt.AlignCenter)
        #     lab_val.setFixedHeight(30)
        #     self.label_value.append(lab_val)
        #     layout_bottom.addWidget(lab_val)
        #     but_Or = QPushButton("Or")
        #     but_Or.setFixedSize(30, 30)
        #     but_Or.setToolTip("Orthogonal Viewer")
        #     but_Or.clicked.connect(self.openOrtho)
        #     self.button_ortho.append(but_Or)
        #     layout_bottom.addWidget(but_Or)
        #     but_3d = QPushButton("3D")
        #     but_3d.setFixedSize(30, 30)
        #     but_3d.setToolTip("3D Viewer")
        #     but_3d.clicked.connect(self.open3D)
        #     self.button_3D.append(but_3d)
        #     layout_bottom.addWidget(but_3d)
        #     self.grid.addLayout(layout_bottom, 4, c)
        #
        # self.grid.setRowStretch(4, 0)

        main_area.addLayout(self.grid, 5)
        # main_area.addWidget(self.image_list)
        # main_area.addLayout(self.grid, 1)

        self.vp = {}

        self.build()
        self.update_all()

    # =====================================================
    # VISIBILITY SELECTION
    # =====================================================

    def label_clicked(self, index):
        self.image_list.setCurrentRow(index)
        self.changeTitleColor(index)

    def changeTitleColor(self, col):
        for title in self.column_titles:
            title.setStyleSheet(
                " QLabel { \
                        font-size: 10px; \
                        font-weight: bold;  \
                        border: 2px solid blue; \
                        border-radius: 10px; \
                        background-color: #e0e0ff;; \
                        padding: 8px; \
                    } \
                ")
        self.column_titles[col].setStyleSheet(
                " QLabel { \
                        font-size: 10px; \
                        font-weight: bold;  \
                        border: 2px solid blue; \
                        border-radius: 10px; \
                        background-color: #ffe000; \
                        padding: 8px; \
                    } \
                ")

    def change_image_visibility(self, item):

        col = item.data(Qt.UserRole)

        self.visible_images[col] = (
            item.checkState() == Qt.Checked
        )

        self.rebuild_grid()

    def show_context_menu(self, pos):
        menu = QMenu(self)
    
        action_check_all = menu.addAction("Select all")
        action_uncheck_all = menu.addAction("Uncheck all")
    
        menu.addSeparator()
    
        item = self.image_list.itemAt(pos)
        if item is not None:
            action_invert = menu.addAction("Invert this element")
    
        action = menu.exec_(self.image_list.viewport().mapToGlobal(pos))
    
        if action == action_check_all:
            self.set_all_items(Qt.Checked)
    
        elif action == action_uncheck_all:
            self.set_all_items(Qt.Unchecked)
    
        elif item is not None and action == action_invert:
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
                
    def set_all_items(self, state):
        self.image_list.blockSignals(True)   # Avoid triggering itemChanged for each item.
    
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            item.setCheckState(state)
            self.visible_images[item.data(Qt.UserRole)] = (state == Qt.Checked)
    
        self.image_list.blockSignals(False)
    
        self.rebuild_grid()

    # =====================================================
    # BUILD GRID
    # =====================================================

    def build(self):

        # =====================================================
        # SLICES COORD
        # =====================================================

        self.label_slice = QLabel()
        self.label_slice.setFixedWidth(150)
        self.label_slice.setStyleSheet("""
                                        font-size: 12px;
                                        font-weight: bold;
                                    """)
        self.grid.addWidget(self.label_slice, 0, 0)

        # =====================================================
        # COLUMN TITLES
        # =====================================================
        self.list_atlas = {}

        # numberOfCol = len(paths)
        longest_text = max(paths, key=lambda f: len(os.path.basename(f)))
        ref_label = QLabel(longest_text)
        ref_label.setWordWrap(True)
        ref_label.adjustSize()
        ref_height = ref_label.sizeHint().height() + 10

        # width_text_clip = 30
        # if numberOfCol > 8:
        #     width_text_clip = 20

        for col, path in enumerate(paths):
            
            if '.nii.gz' in path:
                print('split path', os.path.splitext(path))
                name, _ = os.path.splitext(path)
                name, _ = os.path.splitext(name)
            else:
                name, _ = os.path.splitext(path)
            new_name = name + ".label"
            if os.path.exists(new_name):
                self.list_atlas[f"Img {col}"] = new_name
                self.atlas.addItem(f"Img {col}")
                self.atlas.setItemData(self.atlas.count() - 1, col, Qt.UserRole)
            # filename = os.path.basename(path)
            # wrapped = "\n".join(textwrap.wrap(filename, width=width_text_clip))
            title = ClickableLabel(col, f"Img {col}")
            title.setFixedHeight(ref_height)
            title.setAlignment(Qt.AlignCenter)
            title.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
            title.setWordWrap(True)
            title.setStyleSheet(
                " QLabel { \
                        font-size: 10px; \
                        font-weight: bold;  \
                        border: 2px solid blue; \
                        border-radius: 10px; \
                        background-color: #e0e0ff; \
                        padding: 8px; \
                    } \
                ")
            title.clicked.connect(self.label_clicked)
            self.column_titles.append(title)
            self.grid.addWidget(title, 0, col + 1)

        # =====================================================
        # LABELS
        # =====================================================
        for r, axis in enumerate(axes):

            container = QWidget()
            container.setFixedHeight(150)
            layout = QVBoxLayout(container)

            label_axis = QLabel(get_orientation_labels(axis))
            label_axis.setFixedHeight(20)
            label_axis.setAlignment(Qt.AlignCenter)
            label_axis.setStyleSheet("""
                color: red;
                font-size: 12px;
                font-weight: bold;
            """)

            label_zoom = QLabel(get_zoom_labels(axis))
            label_zoom.setFixedHeight(20)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(30, 1000)
            slider.setValue(100)

            self.zoom_sliders[axis] = slider
            slider.valueChanged.connect(self.update_all)

            layout.addWidget(label_axis, 0)
            layout.addWidget(label_zoom, 0)
            layout.addWidget(slider, 1)
            layout.addStretch(3)

            self.grid.addWidget(container, r + 1, 0)

        # =====================================================
        # IMAGES
        # =====================================================

        for col in range(len(vols)):
            # self.atlas.addItem(f"Img {col}")
            for row, axis in enumerate(axes):
                w = Viewport(col, axis, self)
                w.mouseDoubleClickEvent = lambda e, vp=w: self.on_double_click(vp, e)
                # row + 1 because of titles, col + 1 because of Labels
                self.grid.addWidget(w, row + 1, col + 1)
                self.vp[(col, axis)] = w
            # self.grid.addWidget(self.label_value[col], 4, col + 1)

        # =====================================================
        # BOTTOM MENU
        # =====================================================            
        for c in range(1, len(vols) + 1):
            layout_bottom = QHBoxLayout()
            self.grid.setColumnStretch(c, 3)
            lab_val = QLabel()
            lab_val.setAlignment(Qt.AlignCenter)
            lab_val.setFixedHeight(30)
            self.label_value.append(lab_val)
            layout_bottom.addWidget(lab_val)
            but_Or = QPushButton("Or")
            but_Or.setFixedSize(30, 30)
            but_Or.setToolTip("Orthogonal Viewer")
            but_Or.clicked.connect(self.openOrtho)
            self.button_ortho.append(but_Or)
            layout_bottom.addWidget(but_Or)
            but_3d = QPushButton("3D")
            but_3d.setFixedSize(30, 30)
            but_3d.setToolTip("3D Viewer")
            but_3d.clicked.connect(self.open3D)
            self.button_3D.append(but_3d)
            layout_bottom.addWidget(but_3d)
            self.grid.addLayout(layout_bottom, 4, c)

        self.grid.setRowStretch(4, 0)

        self.grid.invalidate()
        self.grid.activate()

        # ========================

    def rebuild_grid(self):

        for c in range(1, len(vols) + 1):
            self.grid.setColumnStretch(c, 0)

        #
        # enlever tous les widgets images
        #
        for vp in self.vp.values():
            self.grid.removeWidget(vp)
            vp.hide()

        for title, orh, d3, val in zip(self.column_titles, self.button_ortho, self.button_3D, self.label_value):
            self.grid.removeWidget(title)
            title.hide()
            self.grid.removeWidget(orh)
            orh.hide()
            self.grid.removeWidget(d3)
            d3.hide()
            self.grid.removeWidget(val)
            val.hide()

        display_col = 1

        for col in range(len(vols)):

            if not self.visible_images[col]:
                continue
            self.grid.setColumnStretch(display_col, 1)
            self.grid.addWidget(self.column_titles[col], 0, display_col)
            self.column_titles[col].show()
            for row, axis in enumerate(axes):
                vp = self.vp[(col, axis)]
                self.grid.addWidget(vp, row + 1, display_col)
                vp.show()
            layout_bottom = QHBoxLayout()
            layout_bottom.addWidget(self.label_value[col])
            self.label_value[col].show()
            layout_bottom.addWidget(self.button_ortho[col])
            self.button_ortho[col].show()
            layout_bottom.addWidget(self.button_3D[col])
            self.button_3D[col].show()
            self.grid.addLayout(layout_bottom, 4, display_col)
            display_col += 1

        self.grid.invalidate()
        self.grid.activate()

    def change_cmap(self, name):
        global LUT
        LUT = create_lut(name)
        self.render_cache.clear()
        self.update_all()

    def change_roi_mask(self, name):
        self.render_cache.clear()
        self.update_all()

    def change_mode(self, name):
        global mode
        if mode != name:
            # state.v[0] = shape[0] - state.v[0] - 1
            # state.v[1] = shape[1] - state.v[1] - 1
            state.v[2] = shape[2] - state.v[2] - 1
        mode = name
        self.render_cache.clear()
        self.update_all()

    def select_atlas(self, index):
        if index > 0:
            file_atlas = self.atlas.currentText()
            col_img = self.atlas.itemData(index, Qt.UserRole)
            self.col_atlas = col_img
            self.read_label_file(self.list_atlas[file_atlas])
            self.slider_alpha.setEnabled(True)
        else:
            self.widget_structures.clear()
            self.mask = None
            self.col_atlas = None
            self.structure_num = []
            self.structure_list = []
            self.slider_alpha.setEnabled(False)
            self.slider_alpha.setValue(40)
        self.setFocus()
        self.render_cache.clear()

    def show_overlay(self):
        list_img = []
        for i in range(len(self.image_list)):
            list_img.append(f"Image {i}")
        dialog = OverlayDialog(
            list_img,
            parent=self
        )

        if dialog.exec_() == QDialog.Accepted:

            ind_img1, axis, cmap_anat, ind_img2, opac, cmap_mask = (
                dialog.get_files()
            )

            self.start_overlay([ind_img1, ind_img2], axis, cmap_anat, opac, cmap_mask)

    def start_overlay(self, inds, ax, cmap_anat, opac, cmap_mask):

        data1, data2 = vols[inds[0]], vols[inds[1]]

        nx, ny, nz = data1.shape

        plane = self.create_slice(data1, axis=2-ax)

        grid = pv.ImageData(
        dimensions=(nx, ny, nz),
        spacing=(1, 1, 1),
        origin=(0, 0, 0)
        )

        grid.point_data["mask"] = data2.astype(np.float32).ravel(order="F")

        mask_surface = grid.contour(
            isosurfaces=[0.5],
            scalars="mask"
        )

        plotter = pv.Plotter()

        plotter.add_mesh(
            plane,
            scalars="anat",
            cmap=cmap_anat,
            show_scalar_bar=False
        )

        plotter.add_mesh(
            mask_surface,
            # color="red",
            cmap=cmap_mask,
            opacity=opac
        )

        plotter.show()

    def create_slice(self, anat, axis):
        """
        axis:
            0 = sagittal
            1 = coronal
            2 = axial
        """
    
        nx, ny, nz = anat.shape
        
        posx, posy, posz = state.v.tolist()
        
        print(posx, posy, posz)
    
        if axis == 0:           # Sagittal (X constant)
    
            slice_data = anat[posx, :, :]
    
            Y, Z = np.meshgrid(
                np.arange(ny),
                np.arange(nz),
                indexing="ij"
            )
    
            X = np.full_like(Y, posx)
    
            dimensions = (ny, nz, 1)
    
        elif axis == 1:         # Coronal (Y constant)
    
            slice_data = anat[:, posy, :]
    
            X, Z = np.meshgrid(
                np.arange(nx),
                np.arange(nz),
                indexing="ij"
            )
    
            Y = np.full_like(X, posy)
    
            dimensions = (nx, nz, 1)
    
        elif axis == 2:         # Axial (Z constant)
    
            slice_data = anat[:, :, posz]
    
            X, Y = np.meshgrid(
                np.arange(nx),
                np.arange(ny),
                indexing="ij"
            )
    
            Z = np.full_like(X, posz)
    
            dimensions = (nx, ny, 1)
    
        else:
            raise ValueError("axis doit être 0, 1 ou 2")
    
        points = np.column_stack((
            X.ravel(order="F"),
            Y.ravel(order="F"),
            Z.ravel(order="F")
        ))
    
        plane = pv.StructuredGrid()
    
        plane.points = points
        plane.dimensions = dimensions
    
        plane.point_data["anat"] = slice_data.ravel(order="F")
    
        return plane

    def get_render_key(self, col, axis):

        return (
            col,
            axis,
            # position slice
            tuple(state.v),
            # contraste
            round(state.window, 3),
            round(state.level, 3),
            # overlay
            round(state.alpha, 3),
            # colormap
            self.combo_cmap.currentText(),
            # atlas
            tuple(self.structure_num),
            # mode radio/neuro
            mode,
            # ROI ou contour
            self.roi_mask.currentText()
        )

    def read_label_file(self, labels_file):

        self.labels = {}

        with open(labels_file, "r") as f:

            central = QWidget()
            layout = QVBoxLayout(central)

            self.search = QLineEdit()
            self.search.setPlaceholderText("Rechercher...")
            self.search.textChanged.connect(self.filter_list)

            self.widget_structures = QListWidget()

            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(
                    r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+\"(.+)\"",
                    line
                )
                if m:
                    idx = int(m.group(1))
                    if idx == 0:
                        continue
                    r = int(m.group(2))
                    g = int(m.group(3))
                    b = int(m.group(4))
                    alpha = float(m.group(5))
                    vis = int(m.group(6))
                    msh = int(m.group(7))
                    name = m.group(8)

                    self.labels[idx] = {
                        "name": name,
                        "color": (r, g, b),
                        "alpha": alpha,
                        "visible": vis,
                        "mesh": msh,
                    }

                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, idx)
                    # item.setData(Qt.BackgroundRole, None)
                    self.widget_structures.addItem(item)
            self.widget_structures.sortItems()
            self.widget_structures.setSelectionMode(QAbstractItemView.MultiSelection)
            self.widget_structures.selectionModel().selectionChanged.connect(self.on_selection_changed)
            self.widget_structures.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.widget_structures.setMinimumHeight(600)

            layout.addWidget(self.search)
            layout.addWidget(self.widget_structures)

            self.labels_window = LabelsWindow()
            self.labels_window.setCentralWidget(central)
            self.labels_window.closed_lab.connect(self.on_close_atlas)
            self.labels_window.show()
            # self.widget_structures.show()

    def filter_list(self, text):
        text = text.lower()

        for i in range(self.widget_structures.count()):
            item = self.widget_structures.item(i)
            visible = text in item.text().lower()
            item.setHidden(not visible)

    def on_close_atlas(self):
        self.atlas.setCurrentIndex(0)

    def on_selection_changed(self, selected, deselected):

        for index in selected.indexes():
            self.structure_list.append(index.data())
            self.structure_num.append(index.data(Qt.UserRole))
            select = True
            # print("Selected:", index.data())

        for index in deselected.indexes():
            self.structure_list.remove(index.data())
            self.structure_num.remove(index.data(Qt.UserRole))
            select = False
            # print("Deselected:", index.data(), index.data(Qt.UserRole))

        atlas = raw_vols[self.col_atlas]
        self.mask = np.where(
            np.isin(atlas, self.structure_num),
            atlas,
            0
        )

        if select:
            voxel_volume = target_spacing**3
            lab = self.structure_num[-1]
            n_voxels = np.sum(self.mask == lab)
            print(f"{index.data()} : {round(n_voxels * voxel_volume, 2)}mm3", flush=True)
        self.render_cache.clear()
        self.update_all()

    def on_close_structures(self):
        self.atlas.setCurrentIndex(0)

    # =====================================================
    # SLICE ENGINE
    # =====================================================

    def get_slice(self, vol, axis, v):

        x, y, z = v
        if axis == "XY":
            return vol[:, :, z].T, (x, y)
        if axis == "XZ":
            return vol[:, y, :].T, (x, z)
        if axis == "YZ":
            return vol[x, :, :].T, (y, z)

    # =====================================================
    # RENDER
    # =====================================================

    def outer_contour(self, mask):
    
        result = np.zeros_like(mask)
    
        # labels = np.unique(mask)
        # labels = labels[labels > 0]
    
        for lab in self.structure_num:
    
            region = (mask == lab)
    
            filled = binary_fill_holes(region)
            contour = filled & ~binary_erosion(filled)
    
            result[contour] = lab
    
        return result

    def render(self, col, axis):

        key = self.get_render_key(col, axis)
        
        if len(self.render_cache) > 200:
            self.render_cache.clear()
        if key in self.render_cache:
            self.vp[(col, axis)].set_image(
                self.render_cache[key]
            )
            return

        vp = self.vp[(col, axis)]
        vol = vols[col]
        v = clamp(state.v)

        if mode == "Neurological" and axis == "YZ":
            vol = np.flip(vol, axis=0)
        
        img2d, (cx, cy) = self.get_slice(vol, axis, v)
        img2d = window_level(img2d, state.window, state.level)

        # print(axis, "v=", v, cx, cy)

        # FLIP VERTICAL
        img2d = np.flipud(img2d)
        cy = img2d.shape[0] - cy - 1

        # value = img2d[cy, cx]
        # print(f"Img{col} {axis} Voxel={state.v.tolist()} Valeur={value}")

        # crosshair space correction (flip safe optional)
        # img2d = window_level(img2d, state.window, state.level)

        if self.mask_in_slice:
            # print(f"mask in {axis}: {self.mask_in_slice[axis].shape}")
            # df = "name"
            # print(f"mask in {axis}: {self.structure_num}, {self.labels[self.structure_num[0]]}" )
            if self.roi_mask.currentText() == "ROI":
                mask = self.roi_in_slice[axis]
            else:
                mask = self.mask_in_slice[axis]
            mask = np.flipud(mask)
            rgb = np.stack(
                [img2d]*3,
                axis=-1
            ) * 255
            rgb = rgb.astype(np.float32)

            for strc in self.structure_num:
                color = np.array(self.labels[strc]["color"], dtype=np.float32)
                tmpmask = (mask == strc)
                alpha = state.alpha
                rgb[tmpmask] = (
                        (1 - alpha) * rgb[tmpmask]
                        + alpha * color
                    )

            img8 = np.clip(rgb, 0, 255).astype(np.uint8)

            h, w, _ = img8.shape
            qimg = QImage(
                img8.tobytes(),
                w,
                h,
                3 * w,
                QImage.Format_RGB888
            ).copy()
            img = qimg
        else:
            img = to_qimage(img2d)

        pix = QPixmap.fromImage(img)

        if mode == "Neurological":
            if axis != "YZ":
                pix = QPixmap.fromImage(
                    pix.toImage().mirrored(True, False)
                )

        painter = QPainter(pix)

        painter.setPen(QColor(255, 0, 0))
        painter.drawLine(cx, 0, cx, pix.height())
        painter.drawLine(0, cy, pix.width(), cy)

        labels = get_anatomical_labels(axis)

        painter.setPen(QColor(255, 255, 0))
        painter.drawText(pix.width() // 2, 10, labels["top"])
        painter.drawText(pix.width() // 2, pix.height() - 10, labels["bottom"])
        painter.drawText(5, pix.height() // 2, labels["left"])
        painter.drawText(pix.width() - 10, pix.height() // 2, labels["right"])

        painter.end()

        self.render_cache[key] = pix
        vp.set_image(pix)

    # =====================================================
    # UPDATE ALL
    # =====================================================

    def update_all(self):

        self.label_slice.setText(f"Slice: {state.v.tolist()}")

        state.window = self.slider_window.value() / 100
        state.level = self.slider_level.value() / 100
        state.alpha = self.slider_alpha.value() / 100

        for axis in axes:
            state.zoom[axis] = (
                self.zoom_sliders[axis].value() / 100.0
            )

        # affichage valeurs
        self.label_window.setText(f"W: {state.window:.2f}")
        self.label_level.setText(f"L: {state.level:.2f}")
        self.label_alpha.setText(f"A: {state.alpha:.2f}")

        self.mask_in_slice, self.roi_in_slice = {}, {}
        if self.mask is not None:
            v = clamp(state.v)
            for axis in axes:
                mask, _ = self.get_slice(self.mask, axis, v)
                self.mask_in_slice[axis] = mask
                self.roi_in_slice[axis] = self.outer_contour(mask)

        for col in range(len(vols)):
            for axis in axes:
                self.render(col, axis)
            x, y, z = state.v
            value = raw_vols[col][x, y, z]
            self.label_value[col].setText(f"{value:.6f}")
            # print(f"Img {col}: voxel=({x},{y},{z}) value={value:.6f}")

    def start_pan(self, vp, event):
        self.moving = True
        self.active_vp = vp
        self.last_mouse_pos = event.pos()

    def stop_pan(self):
        self.moving = False
        self.active_vp = None

    # =====================================================
    # MOUSE (PRO RESIZE SAFE MAPPING)
    # =====================================================

    def on_mouse(self, vp, event):

        self.dragging = True

        x = event.pos().x()
        y = event.pos().y()

        dx, dy, dw, dh = vp._draw_rect

        # check if click is inside image
        if not (dx <= x <= dx + dw and dy <= y <= dy + dh):
            return

        # normalize inside displayed image
        x = x - dx
        y = y - dy

        # scale to real image size
        x = int(x * vp._img_w / dw)
        y = int(y * vp._img_h / dh)

        if mode == "Neurological":
            x = vp._img_w - x - 1

        # flip vertical
        y = vp._img_h - y - 1

        v = state.v.copy()

        if vp.axis == "XY":
            vx = int(x / vp._img_w * shape[0])
            vy = int(y / vp._img_h * shape[1])

            if mode == "Neurological":
                vx = shape[0] - vx - 1

            v[0] = vx
            v[1] = vy

        elif vp.axis == "XZ":
            vx = int(x / vp._img_w * shape[0])
            vz = int(y / vp._img_h * shape[2])

            if mode == "Neurological":
                vx = shape[0] - vx - 1

            v[0] = vx
            v[2] = vz

        elif vp.axis == "YZ":
            vy = int(x / vp._img_w * shape[1])
            vz = int(y / vp._img_h * shape[2])

            if mode == "Neurological":
                vy = shape[1] - vy - 1

            v[1] = vy
            v[2] = vz

        state.v = clamp(v)
        self.update_all()

    def on_middle_drag(self, vp, event):
    
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
    
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        self.last_mouse_pos = event.pos()
    
        state.pan[vp.axis] += np.array([dx, dy])
    
        self.update_all()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            if self.col_atlas is not None:
                x, y, z = state.v
                value = raw_vols[self.col_atlas][x, y, z]
                self.select_by_idx(self.widget_structures, value, False)
        elif event.key() == Qt.Key_A:
            if self.col_atlas is not None:
                x, y, z = state.v
                value = raw_vols[self.col_atlas][x, y, z]
                self.select_by_idx(self.widget_structures, value, True)

    def select_by_idx(self, list_widget, idx, concat):
        if not concat:
            list_widget.clearSelection()
        for row in range(list_widget.count()):
            item = list_widget.item(row)
            if item.data(Qt.UserRole) == idx:
                item.setSelected(True)
                list_widget.setCurrentItem(item)
                break

    def on_mouse_move(self, vp, event):

        if not self.moving or self.active_vp != vp:
            return

        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return

        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()

        self.last_mouse_pos = event.pos()

        # update pan
        state.pan[vp.axis] += np.array([dx, dy], dtype=float)
    
        # redraw synced axis views
        # for col in range(len(vols)):
        #     # self.render(col, vp.axis)
        self.update_crosshair_only(vp.axis)
        
    def average_contrast(self):

        vol = vols[0]
 
        # ignore NaN / inf
        data = vol[np.isfinite(vol)]
    
        if data.size == 0:
            return
    
        # percentiles robustes
        p2 = np.percentile(data, 0)
        p98 = np.percentile(data, 100)

        # calcul WL
        window = p98 - p2
        level = (p98 + p2) / 2
    
        # protection
        window = max(window, 1e-3)
    
        # sliders -> [0..2] et [0..1]
        self.slider_window.setValue(int(window * 100))
        self.slider_level.setValue(int(level * 100))
    
        self.update_all()
        
    def auto_contrast_view(self, vp):
    
        vol = vols[vp.col]
    
        v = clamp(state.v)
    
        img2d, _ = self.get_slice(vol, vp.axis, v)
    
        data = img2d[np.isfinite(img2d)]
    
        if data.size == 0:
            return
    
        # percentiles robustes
        p2 = np.percentile(data, 0)
        p98 = np.percentile(data, 100)
    
        window = p98 - p2
        level = (p98 + p2) / 2
    
        window = max(window, 1e-3)
    
        state.window = float(window)
        state.level = float(level)
    
        # synchro sliders
        self.slider_window.blockSignals(True)
        self.slider_level.blockSignals(True)
    
        self.slider_window.setValue(int(window * 150))
        self.slider_level.setValue(int(level * 150))
    
        self.slider_window.blockSignals(False)
        self.slider_level.blockSignals(False)
    
        self.update_all()
        
    def auto_contrast_column(self, col):
    
        vol = vols[col]
    
        data = vol[np.isfinite(vol)]
    
        if data.size == 0:
            return
    
        # auto contraste global du volume
        p2 = np.percentile(data, 0)
        p98 = np.percentile(data, 100)
    
        window = p98 - p2
        level = (p98 + p2) / 2
    
        window = max(window, 1e-3)
    
        state.window = float(window)
        state.level = float(level)
    
        # sync sliders UI
        self.slider_window.blockSignals(True)
        self.slider_level.blockSignals(True)

        self.slider_window.setValue(int(window * 100))
        self.slider_level.setValue(int(level * 100))

        self.slider_window.blockSignals(False)
        self.slider_level.blockSignals(False)

        self.update_all()

    def recenter_crosshair(self):

        state.v = np.array(shape) // 2
        self.update_all()

        for axis in axes:
            state.pan[axis] = np.array([0.0, 0.0], dtype=float)
            state.zoom[axis] = 1.0

            if axis in self.zoom_sliders:
                self.zoom_sliders[axis].blockSignals(True)
                self.zoom_sliders[axis].setValue(100)
                self.zoom_sliders[axis].blockSignals(False)

    def on_double_click(self, vp, event):

        # Récupérer la position originale dans le GridLayout
        index = self.grid.indexOf(vp)
        row, col, rowSpan, columnSpan = self.grid.getItemPosition(index)

        if vp.detached:
            return

        vp.detached = True

        # vp.setSizePolicy(
        #     QSizePolicy.Expanding,
        #     QSizePolicy.Expanding
        # )

        # Stocker la position originale
        self.original_grid_position[vp] = (row, col, rowSpan, columnSpan)
   
        window = DetachedWindow(self)
        # window.setWindowFlags(Qt.WindowStaysOnTopHint)
        window.closed.connect(
            lambda vp=vp, r=row, c=col, rs=rowSpan, cs=columnSpan:
                self.restore_to_grid(vp, r, c, rs, cs)
        )
        # Créer une nouvelle fenêtre
        self.second_window = window
        self.second_window.setWindowTitle(f"Image agrandie - {vp.axis} (Col {vp.col})")
        self.second_window.setGeometry(100, 100, 800, 800)
    
        # Supprimer temporairement l'image du GridLayout
        self.grid.removeWidget(vp)
        vp.setParent(None)  # Détacher de l'ancien parent
    
        # Ajouter l'image à la nouvelle fenêtre
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(vp)
        container = QWidget()
        container.setLayout(layout)
        self.second_window.setCentralWidget(container)
    
        # Connecter la fermeture de la fenêtre à une méthode de réintégration
        self.second_window.destroyed.connect(lambda: self.restore_to_grid(vp, row, col, rowSpan, columnSpan))
    
        # Afficher la fenêtre
        self.second_window.show()

    def restore_to_grid(self, vp, row, col, rowSpan, columnSpan):
        
        vp.detached = False
        try:
            self.grid.addWidget(vp, row, col, rowSpan, columnSpan)
            vp.show()
            self.grid.invalidate()
            self.grid.activate()
            self.update_all()
        except Exception as err:
            print(err)
    

    def update_crosshair_only(self, axis):

        for col in range(len(vols)):
            vp = self.vp[(col, axis)]

            # on ne rerender PAS l'image
            # on prend juste le pixmap déjà existant

            if vp.pix is None:
                continue

            pix = vp.pix.copy()

            painter = QPainter(pix)

            v = clamp(state.v)
            img = pix.toImage()

            w = pix.width()
            h = pix.height()
    
            # recalcul crosshair (léger)
            if axis == "XY":
                cx = int(v[0] / shape[0] * w)
                cy = int(v[1] / shape[1] * h)
    
            elif axis == "XZ":
                cx = int(v[0] / shape[0] * w)
                cy = int(v[2] / shape[2] * h)
    
            else:  # YZ
                cx = int(v[1] / shape[1] * w)
                cy = int(v[2] / shape[2] * h)
    
            painter.setPen(QColor(255, 0, 0))
            painter.drawLine(cx, 0, cx, h)
            painter.drawLine(0, cy, w, cy)
    
            painter.end()
    
            vp.setPixmap(pix)
            
    def handle_detached_key(self, key):
    
        if self.col_atlas is None:
            return
    
        x, y, z = state.v
        value = raw_vols[self.col_atlas][x, y, z]
    
        if key == "W":
            self.select_by_idx(
                self.widget_structures,
                value,
                False
            )
    
        elif key == "A":
            self.select_by_idx(
                self.widget_structures,
                value,
                True
            )
# cmap=self.combo_cmap.currentText()

    def openOrtho(self):
        button_nb = self.sender()
        col = self.button_ortho.index(button_nb)
        
        t = threading.Thread(
                target=self.view_ortho,
                args=(vols[col], (target_spacing, target_spacing, target_spacing))
                )
        
        t.start()

    def open3D(self):
        button_nb = self.sender()
        col = self.button_3D.index(button_nb)
        # [but.setEnabled(False) for but in self.button_3D]
        # self.view_3D(vols[col], (target_spacing, target_spacing, target_spacing))
        
        t = threading.Thread(
                target=self.view_3D,
                args=(vols[col], (target_spacing, target_spacing, target_spacing))
                )

        t.start()

    def view_3D(self, data, spacing):
    
        # Créer un volume PyVista
        grid = pv.ImageData()
        grid.dimensions = np.array(data.shape) + 1
    
        # réducion de résolution pendant navigation
        # factor = 2
        # data = data[::factor, ::factor, ::factor]
        # spacing = tuple(s * factor for s in spacing) 
    
        grid.spacing = spacing
        grid.origin = (0, 0, 0)
    
        # Les données doivent être aplaties en ordre Fortran
        # grid.cell_data["values"] = data.flatten(order="F")
    
        # Affichage
        plotter = pv.Plotter()
        plotter.enable_terrain_style(mouse_wheel_zooms=1.01)
        plotter.render_window.SetMultiSamples(0) # pour naviguer un peu + vite
        plotter.renderer.SetInteractive(True) # pour naviguer un peu + vite
        # plotter.set_background("magenta")
        # plotter.add_mesh_clip_plane(grid)
        # plotter.add_mesh_clip_plane(grid)
    
        # flat = np.asfortranarray(data).ravel()
        # grid.cell_data["values"] = flat
    
        grid.cell_data["values"] = data.flatten(order="F")
    
        vol = plotter.add_volume(
            grid,
            cmap=self.combo_cmap.currentText(),
            # mapper="gpu",
            opacity="linear",
            shade=True
        )
    
        data_min, data_max = vol.mapper.scalar_range
    
        # Valeurs initiales
        # data_min = float(np.min(data))
        # data_max = float(np.max(data))
    
        state = {
            "level": (data_min + data_max) / 2,
            "window": data_max - data_min,
        }
    
        light = pv.Light(position=(500, 500, 500),
                 focal_point=(0, 0, 0),
                 intensity=1.0)
    
        plotter.add_light(light)
    
        # Fonctions orientation
        def left():
            plotter.view_vector((-1, 0, 0))
    
        def right():
            plotter.view_vector((1, 0, 0))
    
        def posterior():
            plotter.view_vector((0, -1, 0))
    
        def anterior():
            plotter.view_vector((0, 1, 0))
    
        def inferior():
            plotter.view_vector((0, 0, -1))
    
        def superior():
            plotter.view_vector((0, 0, 1))
    
        def axial_p():
            plotter.view_xy()
    
        def coronal_p():
            plotter.view_xz()
    
        def sagittal_p():
            plotter.view_yz()
    
        def axial_m():
            plotter.view_yx()
    
        def coronal_m():
            plotter.view_zx()
    
        def sagittal_m():
            plotter.view_zy()
    
        def update(_=None):
            vmin = state["level"] - state["window"] / 2
            vmax = state["level"] + state["window"] / 2
            vol.mapper.scalar_range = (vmin, vmax)
            plotter.render()
    
        def set_level(value):
            state["level"] = value
            update()
    
        def set_window(value):
            state["window"] = value
            update()
    
        def update_light(value):
            light.intensity = value
            plotter.render()
    
        posX, posY = 50, 200
    
        buttons = [
            ("Left", (-1,0,0), (0,0,1), (posX,posY + 200)),
            ("Right", (1,0,0), (0,0,1), (posX,posY + 160)),
            ("Anterior", (0,1,0), (0,0,1), (posX,posY + 120)),
            ("Posterior", (0,-1,0), (0,0,1), (posX,posY + 80)),
            ("Superior", (0,0,1), (0,1,0), (posX,posY + 40)),   # rotation 90°
            ("Inferior", (0,0,-1), (0,1,0), (posX,posY)),
        ]
    
        list_button_orient = []
    
        for i, (label, vec, up, pos) in enumerate(buttons):
    
            def callback(state, v=vec, u=up, inc=i):
                # if state:
                plotter.view_vector(v, viewup=u)
                # plotter.camera_position = [tuple(-10*np.array(v)), (0, 0, 0), u]
                plotter.render()
                plotter.update()
                list_button_orient[inc].GetRepresentation().SetState(False)
    
            list_button_orient.append(plotter.add_checkbox_button_widget(
                callback,
                position=pos,
                size=25
            ))
    
            plotter.add_text(
                label,
                position=(pos[0]+40, pos[1]+5),
                font_size=10
            )
    
        plotter.add_slider_widget(
            update_light,
            rng=[0.0, 5.0],
            value=1.0,
            title="Light",
            pointa=(0.6, 0.80),
            pointb=(0.9, 0.80),
            style="modern"
        )
    
        plotter.add_slider_widget(set_level, [data_min, data_max],
                                  value=state["level"],
                                  title="Level",
                                  pointa=(0.1, 0.92),   # début du slider (fenêtre normalisée)
                                  pointb=(0.4, 0.92),   # fin du slider
                                  style="modern")
    
        plotter.add_slider_widget(set_window, [0.01, 1.0],
                                  value=state["window"],
                                  title="Window",
                                  pointa=(0.6, 0.92),
                                  pointb=(0.9, 0.92),
                                  style="modern")
    
        def update_opacity(value):
            vol.prop.opacity_unit_distance = value
            plotter.render()
    
        plotter.add_slider_widget(update_opacity,
                                  rng=[0.01, 1.0],
                                  value=0.1,
                                  title="Opacity",
                                  pointa=(0.1, 0.80),
                                  pointb=(0.4, 0.80),
                                  style="modern")
    
        vtk.vtkObject.GlobalWarningDisplayOff()
    
        cube = vtkAnnotatedCubeActor()
        cube.GetCubeProperty().SetColor(0.2, 0.5, 0.8)
    
        cube.SetXPlusFaceText("R")
        cube.SetXMinusFaceText("L")
    
        cube.SetYPlusFaceText("A")
        cube.SetYMinusFaceText("P")
    
        cube.SetZPlusFaceText("S")
        cube.SetZMinusFaceText("I")
    
        widget = vtkOrientationMarkerWidget()
    
        widget.SetOrientationMarker(cube)
        widget.SetInteractor(plotter.iren.interactor)
        widget.SetEnabled(1)
        widget.InteractiveOff()
    
        # Valeurs initiales appliquées au volume
        # update()
        # vol.prop.opacity_unit_distance = 0.1
        # light.intensity = 1.0
        # plotter.reset_camera()
        plotter.show()

    def view_ortho(self, data, spacing):

        # Créer un volume PyVista
        grid = pv.ImageData()
        grid.dimensions = np.array(data.shape) + 1

        # réducion de résolution pendant navigation
        # factor = 2
        # data = data[::factor, ::factor, ::factor]
        # spacing = tuple(s * factor for s in spacing) 

        grid.spacing = spacing
        grid.origin = (0, 0, 0)

        # Les données doivent être aplaties en ordre Fortran
        # grid.cell_data["values"] = data.flatten(order="F")

        # Affichage
        plotter = pv.Plotter()
        plotter.enable_terrain_style(mouse_wheel_zooms=1.01)
        plotter.render_window.SetMultiSamples(0) # pour naviguer un peu + vite
        plotter.renderer.SetInteractive(True) # pour naviguer un peu + vite
        # plotter.set_background("magenta")

        # flat = np.asfortranarray(data).ravel()
        # grid.cell_data["values"] = flat

        grid.cell_data["values"] = data.flatten(order="F")

        # Plans de coupe
        nx, ny, nz = data.shape
    
        slice_x = plotter.add_mesh(
            grid.slice(normal="x", origin=(nx * spacing[0] / 2, 0, 0)),
            cmap=self.combo_cmap.currentText(),
            opacity=1.0
        )

        slice_y = plotter.add_mesh(
            grid.slice(normal="y", origin=(0, ny * spacing[1] / 2, 0)),
            cmap=self.combo_cmap.currentText(),
            opacity=1.0
        )

        slice_z = plotter.add_mesh(
            grid.slice(normal="z", origin=(0, 0, nz * spacing[2] / 2)),
            cmap=self.combo_cmap.currentText(),
            opacity=1.0
        )

        data_min = float(np.min(data))
        data_max = float(np.max(data))

        state = {
            "level": (data_min + data_max) / 2,
            "window": data_max - data_min,
            "opacity": 1.0,
            "light": 1.0,
            "slice_x": nx//2,
            "slice_y": ny//2,
            "slice_z": nz//2,
        }

        reslice_x = vtk.vtkImageReslice()
        reslice_x.SetInputData(grid)
        reslice_x.SetOutputDimensionality(2)
        reslice_x.SetInterpolationModeToLinear()
        reslice_x.Update()

        slice_x.mapper.SetInputData(reslice_x.GetOutput())

        def update_window_level():

            vmin = state["level"] - state["window"] / 2
            vmax = state["level"] + state["window"] / 2

            slice_x.mapper.scalar_range = (vmin, vmax)
            slice_y.mapper.scalar_range = (vmin, vmax)
            slice_z.mapper.scalar_range = (vmin, vmax)

            plotter.render()

        def set_level(value):
            state["level"] = value
            update_window_level()

        def set_window(value):
            state["window"] = max(value, 1e-6)
            update_window_level()

        def set_opacity(value):
            slice_x.prop.opacity = value
            slice_y.prop.opacity = value
            slice_z.prop.opacity = value
            plotter.render()

        def update_light(value):
            light.intensity = value
            plotter.render()

        update_window_level()
    
        slider_level = plotter.add_slider_widget(
            set_level,
            rng=[data_min, data_max],
            value=state["level"],
            title="Level",
            pointa=(0.00, 0.94),
            pointb=(0.20, 0.94),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern"
        )
    
        slider_window = plotter.add_slider_widget(
            set_window,
            rng=[1e-6, data_max - data_min],
            value=state["window"],
            title="Window",
            pointa=(0.00, 0.84),
            pointb=(0.20, 0.84),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern"
        )
    
        slider_opacity = plotter.add_slider_widget(
            set_opacity,
            rng=[0.0, 1.0],
            value=1.0,
            title="Opacity",
            pointa=(0.00, 0.74),
            pointb=(0.20, 0.74),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern"
        )
    
        light = pv.Light(position=(500, 500, 500),
                 focal_point=(0, 0, 0),
                 intensity=1.0)
    
        plotter.add_light(light)
        
        slider_light = plotter.add_slider_widget(
            update_light,
            rng=[0.0, 5.0],
            value=1.0,
            title="Light",
            pointa=(0.00, 0.64),
            pointb=(0.20, 0.64),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern"
        )
    
        # Fonctions orientation
        def left():
            plotter.view_vector((-1, 0, 0))
    
        def right():
            plotter.view_vector((1, 0, 0))
    
        def posterior():
            plotter.view_vector((0, -1, 0))
    
        def anterior():
            plotter.view_vector((0, 1, 0))
    
        def inferior():
            plotter.view_vector((0, 0, -1))
    
        def superior():
            plotter.view_vector((0, 0, 1))
    
        def axial_p():
            plotter.view_xy()
    
        def coronal_p():
            plotter.view_xz()
    
        def sagittal_p():
            plotter.view_yz()
    
        def axial_m():
            plotter.view_yx()
    
        def coronal_m():
            plotter.view_zx()
    
        def sagittal_m():
            plotter.view_zy()
    
   
        posX, posY = 50, 200
    
        buttons = [
            ("Left", (-1,0,0), (0,0,1), (posX,posY + 200)),
            ("Right", (1,0,0), (0,0,1), (posX,posY + 160)),
            ("Anterior", (0,1,0), (0,0,1), (posX,posY + 120)),
            ("Posterior", (0,-1,0), (0,0,1), (posX,posY + 80)),
            ("Superior", (0,0,1), (0,1,0), (posX,posY + 40)),   # rotation 90°
            ("Inferior", (0,0,-1), (0,1,0), (posX,posY)),
        ]
    
        list_button_orient = []
    
        for i, (label, vec, up, pos) in enumerate(buttons):
    
            def callback(state, v=vec, u=up, inc=i):
                # if state:
                plotter.view_vector(v, viewup=u)
                # plotter.camera_position = [tuple(-10*np.array(v)), (0, 0, 0), u]
                plotter.render()
                plotter.update()
                list_button_orient[inc].GetRepresentation().SetState(False)
    
            list_button_orient.append(plotter.add_checkbox_button_widget(
                callback,
                position=pos,
                size=25
            ))
    
            plotter.add_text(
                label,
                position=(pos[0]+40, pos[1]+5),
                font_size=10
            )
   
        vtk.vtkObject.GlobalWarningDisplayOff()
    
        cube = vtkAnnotatedCubeActor()
        cube.GetCubeProperty().SetColor(0.2, 0.5, 0.8)
    
        cube.SetXPlusFaceText("R")
        cube.SetXMinusFaceText("L")
    
        cube.SetYPlusFaceText("A")
        cube.SetYMinusFaceText("P")
    
        cube.SetZPlusFaceText("S")
        cube.SetZMinusFaceText("I")
    
        widget = vtkOrientationMarkerWidget()
    
        widget.SetOrientationMarker(cube)
        widget.SetInteractor(plotter.iren.interactor)
        widget.SetEnabled(1)
        widget.InteractiveOff()
    
        def update_x(value):
            x = value * spacing[0]
            new_slice = grid.slice(normal="x", origin=(x, 0, 0))
            slice_x.mapper.SetInputData(new_slice)
            plotter.render()

        def update_y(value):
            y = value * spacing[1]
            new_slice = grid.slice(normal="y", origin=(0, y, 0))
            slice_y.mapper.SetInputData(new_slice)
            plotter.render()

        def update_z(value):
            z = value * spacing[2]
            new_slice = grid.slice(normal="z", origin=(0, 0, z))
            slice_z.mapper.SetInputData(new_slice)
            plotter.render()

        slider_x = plotter.add_slider_widget(
            update_x,
            rng=[0, nx - 1],
            value=nx // 2,
            title="Sagittal",
            pointa=(0.75, 0.94),
            pointb=(1.00, 0.94),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern",
            interaction_event="end"
        )

        slider_y = plotter.add_slider_widget(
            update_y,
            rng=[0, ny - 1],
            value=ny // 2,
            title="Axial",
            pointa=(0.75, 0.84),
            pointb=(1.00, 0.84),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern",
            interaction_event="end"
        )

        slider_z = plotter.add_slider_widget(
            update_z,
            rng=[0, nz - 1],
            value=nz // 2,
            title="Coronal",
            pointa=(0.75, 0.74),
            pointb=(1.00, 0.74),
            title_height=0.02,
            tube_width=0.02,
            slider_width=0.01,
            style="modern",
            interaction_event="end"
        )

        def reset_all(checked):
        
            # Coupes au centre
            slider_x.GetRepresentation().SetValue(state["slice_x"])
            slider_y.GetRepresentation().SetValue(state["slice_y"])
            slider_z.GetRepresentation().SetValue(state["slice_z"])
        
            update_x(state["slice_x"])
            update_y(state["slice_y"])
            update_z(state["slice_z"])
        
        
            # Contraste initial
            level0 = (data_min + data_max) / 2
            window0 = data_max - data_min
        
            state["level"] = level0
            state["window"] = window0
        
            light.intensity = 1.0
            
            # déplacer les sliders graphiques
            slider_level.GetRepresentation().SetValue(level0)
            slider_window.GetRepresentation().SetValue(window0)
            slider_opacity.GetRepresentation().SetValue(1.0)
            slider_light.GetRepresentation().SetValue(1.0)

            # appliquer
            update_window_level()
        
            set_opacity(1.0)
        
            plotter.render()
        
            reset_widget.GetRepresentation().SetState(False)
            
        reset_widget = plotter.add_checkbox_button_widget(
            reset_all,
            position=(500, 720),
            size=25
        )
        
        plotter.add_text(
            "Reset",
            position=(490, 690),
            font_size=10
        )
    
        plotter.show()


class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
        super().mousePressEvent(event)


class DetachedWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def keyPressEvent(self, event):
    
        if event.key() == Qt.Key_W:
            self.viewer.handle_detached_key("W")
    
        elif event.key() == Qt.Key_A:
            self.viewer.handle_detached_key("A")

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)


class LabelsWindow(QMainWindow):
    closed_lab = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def closeEvent(self, event):
        self.closed_lab.emit()
        super().closeEvent(event)


class OverlayDialog(QDialog):
    
    def __init__(self, listImage, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Slice–Volume Overlay")
        self.resize(500, 130)
        
        # ====================================================
        # LAYOUT PRINCIPAL
        # ====================================================

        layout = QVBoxLayout(self)

        # ====================================================
        # IMAGE ANATOMIQUE
        # ====================================================

        anatomical_layout = QHBoxLayout()
        anatomical_label = QLabel("Image 2D:")

        self.anatomical_combo = QComboBox()
        self.anatomical_combo.addItems(listImage)
        
        self.anatomical_axis = QComboBox()
        self.anatomical_axis.addItems(["Axis 0", "Axis 1", "Axis 2"])
        
        self.anatomical_cmap = QComboBox()
        self.anatomical_cmap.addItems(get_cmap_list())

        anatomical_layout.addWidget(anatomical_label)
        anatomical_layout.addWidget(self.anatomical_combo)
        anatomical_layout.addWidget(self.anatomical_axis)
        anatomical_layout.addWidget(self.anatomical_cmap)
        layout.addLayout(anatomical_layout)
        
        # ====================================================
        # MASK
        # ====================================================

        mask_layout = QHBoxLayout()
        mask_label = QLabel("Image 3D:")

        self.mask_combo = QComboBox()
        self.mask_combo.addItems(listImage)
        
        self.mask_cmap = QComboBox()
        self.mask_cmap.addItems(get_cmap_list())
        
        self.mask_opacity = QDoubleSpinBox()
        self.mask_opacity.setToolTip("Opacity")
        self.mask_opacity.setDecimals(1)
        self.mask_opacity.setSingleStep(0.1)
        self.mask_opacity.setRange(0.0, 1.0)
        self.mask_opacity.setValue(0.5)
        

        mask_layout.addWidget(mask_label)
        mask_layout.addWidget(self.mask_combo)
        mask_layout.addWidget(self.mask_opacity)
        mask_layout.addWidget(self.mask_cmap)
        layout.addLayout(mask_layout)

        # ====================================================
        # BOUTONS
        # ====================================================

        buttons = QDialogButtonBox(QDialogButtonBox.Ok |QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    # ========================================================
    # RECUPERER LES FICHIERS SELECTIONNES
    # ========================================================

    def get_files(self):
        return (self.anatomical_combo.currentIndex(),
                self.anatomical_axis.currentIndex(),
                self.anatomical_cmap.currentText(),
                self.mask_combo.currentIndex(),
                self.mask_opacity.value(),
                self.mask_cmap.currentText()
                )

# =========================================================
# RUN
# =========================================================

viewer = PACSViewer()
viewer.show()
sys.exit(app.exec_())
