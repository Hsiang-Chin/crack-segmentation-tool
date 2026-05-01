# Crack Annotation Tool
[English](README.MD) | [繁體中文](README.zh-TW.md)

> **Branch notice:** This is a fork of the original repository with the following enhancements:
> - **i18n** multilingual system (English / 繁體中文, runtime-switchable)
> - **MVC refactor** — source split into `app/` package (Model / View / Controller)
> - **PyQt6 migration** — fully ported from PyQt5
> - **QThread background processing** — annotation lag eliminated
> - **UI redesign** — Material-inspired light theme (QSS)
> - **Folder browser dialog** — native OS dialog replaces manual path input
> - **Unicode path fix** — images in directories with non-ASCII names now load correctly

The presented crack annotation tool is designed to generate pixel-wise labeling of images of cracks in a semi-automatic manner. It also allows drawing bounding boxes around objects. Its main goal is to simplify the creation of a dataset to train deep learning algorithms for crack segmentation. The mathematical underpinning was developed by Remco Duits (https://www.win.tue.nl/~rduits/) and the mathematical image analysis group at Eindhoven University of Technology.

Annotation can be made in one of two ways (or both):
1. Bounding box annotation
2. Crack segmentation

The segmentation process consists of a few main steps:
1. Manual selection of two crack end-points
2. Finding a crack path between the selected points
3. Finding crack edges along the retrieved path
4. Pixels between crack edges are marked as crack pixels
5. Optionally, a crack segment can be added by manually drawing the crack contour

The algorithm is described in our paper:

> [1] Kompanets, A., Duits, R., Leonetti, D., van den Berg, N., Snijder, H.H. (2024). *Segmentation Tool for Images of Cracks.* ICCCBE 2022, LNCE vol. 357. Springer. https://doi.org/10.1007/978-3-031-35399-4_8

Preprint: https://www.win.tue.nl/~rduits/CD.pdf

---

## Project structure

```
crack-segmentation-tool/
├── crack_tool.py          # Entry point — run this to launch the app
├── app/                   # MVC application source
│   ├── controller.py      # Button handlers; owns QThread workers
│   ├── model.py           # All persistent state + annotation I/O
│   ├── view.py            # Display helpers, i18n, workflow button states
│   ├── workers.py         # QThread workers (Boundary / OS / Cost / Track)
│   ├── i18n.py            # Translation dictionaries + tr() / set_lang()
│   ├── stylesheet.py      # Material-inspired QSS theme
│   ├── layout.py          # Auto-generated PyQt6 UI definition
│   └── app.ui             # Qt Designer source file
├── cracktools/            # Core segmentation algorithm library
├── notebooks/             # Jupyter notebooks
│   ├── check annotation.ipynb
│   ├── generate_mask_from_json.ipynb
│   └── Segmentation.ipynb
├── images/                # Background images used by the UI
├── video/                 # Tutorial GIFs and videos
├── README.MD
└── README.zh-TW.md
```

---

## Dependencies

- Python **3.10+** (tested on 3.11)
- PyQt6
- agd 0.2.16+
- hfm 0.2.13 (https://github.com/Mirebeau/HamiltonFastMarching)
- numpy, opencv-python, scikit-image, matplotlib, plotly

### Install with pip (recommended — use a virtual environment)

```console
pip install PyQt6 numpy opencv-python scikit-image matplotlib plotly
pip install agd
pip install hfm==0.2.13
```

### Install with conda (original method)

```console
conda install agd
conda install -c agd-lbr hfm=0.2.13
```

---

## Run the app

```console
python crack_tool.py
```

The language switcher (English / 繁體中文) is in the bottom-right of the status bar and takes effect immediately without restarting.

---

## Cite

If you use this code or app in your own work, please cite:

> [1] Kompanets, A., Duits, R., Leonetti, D., van den Berg, N., Snijder, H.H. (2024). *Segmentation Tool for Images of Cracks.* ICCCBE 2022, LNCE vol. 357. Springer. https://doi.org/10.1007/978-3-031-35399-4_8

---

# App Tutorial

## "Select Image" Tab

#### Start annotation
1. Click **Select Folder** to open a native folder browser and choose the directory that contains your images.
2. A list of images in the folder will appear. If an annotation file for an image exists, the annotation is displayed automatically.

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/1.gif)

#### Annotate bounding box (optional)
1. Set **Image size** to adjust the drawing window size.
2. Press **Draw Box** to open the drawing window.
3. Draw a single bounding box:
   - Mouse wheel to zoom in/out
   - Left-click to select the first corner; left-click again for the opposite corner
   - Right-click to undo the previous selection
   - Esc to close the window
4. Set the **Class** integer (0 = crack, 1 = corrosion, or any integer).
5. Press **Save Box** to save to the annotation file.
6. **Clear Boxes** removes all boxes; **Clear segmentation** removes all crack pixels.

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/2.gif)

---

## "Tracking" Tab

#### Select crack endpoints
1. Press **Select Crack End-Points**.
2. Adjust **Image size** to fit the window to your screen.
3. Mouse wheel to zoom; left-click to select a point; right-click to undo.
4. Select two points (crack tips), then press Esc.

#### Crop image around crack
1. Choose **Dark crack** or **Bright crack** based on contrast.
2. Pick the color channel with the most contrast.
3. Set **Downsample factor** to reduce image size and speed up processing.
4. Set **X / Y margins** to frame the crack comfortably.
5. Press **Update cropped Image** — the LCD display below shows the cropped size.

#### (Optional) Design wavelet
1. Press **Check wavelet** to preview the cake wavelet.
2. Press **Select crack point to check width** to pick a representative midpoint.
3. Press **Update** to display the crack mid-point region.
4. Tune wavelet parameters so its bright center matches the crack width.

#### Create orientation scores and cost function
1. Press **Update OS** (runs in background — progress bar fills when done).
2. Press **Update Cost** (also background).
3. Adjust cost parameters to maximize crack response in the projection.

#### Crack track
1. Press **Crack Track** to run the tracking algorithm (background).
2. Tune g11, g22, g33 (see [1] for description).
3. Adjust **Track width** / **Track color** for visualization.
4. Press **Update track display** or **Track full screen** to inspect results.

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/3.gif)

---

## "Segmentation" Tab

#### Retrieve crack edges
1. Set **filter size** (how far from the track edges can be found).
2. Press **Edge mask**.
3. Tune mu, l, p parameters.
4. Press **Edge tracks**.
5. Press **Edge tracks full screen** for a full-size preview.

#### Save segment
Press **Save segment** to commit the current segmentation mask. You can repeat the process to add multiple segments to the same image. A JSON file is written alongside the image containing all pixel coordinates.

For instructions on reading the JSON files, see `notebooks/generate_mask_from_json.ipynb`.

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/4.gif)

---

## "Add segment manually" Tab

1. Press **Draw segment** to open the drawing window.
2. Mouse wheel to zoom.
3. Hold left-click and drag to draw a contour part; release to fix it. Click again to start a new part (connected by a straight line).
4. Right-click to erase the previous part.
5. Esc to close — the contour is closed automatically.
6. Press **Save segment** to add it to the annotation mask.

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/5.gif)
