# 裂縫標註工具
[English](README.MD) | [繁體中文](README.zh-TW.md)

> **分支說明：** 本分支為原始倉庫的改良版（由 Claude Code 協助撰寫），包含以下優化：
> - **i18n 多語言系統** — 繁體中文 / English，可即時切換
> - **MVC 重構** — 原始碼拆分為 `app/` 套件（Model / View / Controller）
> - **PyQt6 遷移** — 完整從 PyQt5 移植
> - **QThread 背景運算** — 消除標記時的卡頓問題
> - **UI 重新設計** — Material 風格淺色主題（QSS）
> - **資料夾瀏覽對話框** — 以原生 OS 對話框取代手動輸入路徑
> - **Unicode 路徑修正** — 路徑含非 ASCII 字元（如中文）的資料夾現在可正確載入

所呈現的裂縫標註工具旨在以半自動的方式生成裂縫圖像的逐像素標籤，並支援在物件周圍繪製邊界框。其主要目標是簡化訓練深度學習算法所需的資料集建立流程。分割算法的數學基礎由 Remco Duits（https://www.win.tue.nl/~rduits/）與埃因霍溫科技大學的數學圖像分析團隊開發。

標註可透過以下兩種方式之一或兩者進行：
1. 邊界框標註
2. 裂縫分割

分割流程包含以下主要步驟：
1. 手動選擇兩個裂縫端點
2. 在選定點之間尋找裂縫路徑
3. 沿著路徑尋找裂縫邊緣
4. 裂縫邊緣之間的像素標記為裂縫像素
5. 可選擇手動繪製裂縫輪廓來新增裂縫區段

算法說明可參考論文：

> [1] Kompanets, A., Duits, R., Leonetti, D., van den Berg, N., Snijder, H.H. (2024). *Segmentation Tool for Images of Cracks.* ICCCBE 2022, LNCE vol. 357. Springer. https://doi.org/10.1007/978-3-031-35399-4_8

預印本：https://www.win.tue.nl/~rduits/CD.pdf

---

## 專案結構

```
crack-segmentation-tool/
├── crack_tool.py          # 程式進入點 — 執行此檔案啟動應用程式
├── app/                   # MVC 應用程式原始碼
│   ├── controller.py      # 按鈕事件處理；管理 QThread workers
│   ├── model.py           # 所有持久狀態 + 標註資料 I/O
│   ├── view.py            # 顯示輔助函式、i18n、工作流程按鈕狀態
│   ├── workers.py         # QThread workers（Boundary / OS / Cost / Track）
│   ├── i18n.py            # 翻譯字典 + tr() / set_lang()
│   ├── stylesheet.py      # Material 風格 QSS 主題
│   ├── layout.py          # 自動生成的 PyQt6 UI 定義
│   └── app.ui             # Qt Designer 來源檔
├── cracktools/            # 核心分割算法函式庫
├── notebooks/             # Jupyter 筆記本
│   ├── check annotation.ipynb
│   ├── generate_mask_from_json.ipynb
│   └── Segmentation.ipynb
├── images/                # UI 使用的背景圖片
├── video/                 # 教學 GIF 與影片
├── README.MD
└── README.zh-TW.md
```

---

## 相依套件

- Python **3.10+**（已在 3.11 測試）
- PyQt6
- agd 0.2.16+
- hfm 0.2.13（https://github.com/Mirebeau/HamiltonFastMarching）
- numpy、opencv-python、scikit-image、matplotlib、plotly

### 使用 pip 安裝（建議搭配虛擬環境）

```console
pip install PyQt6 numpy opencv-python scikit-image matplotlib plotly
pip install agd
pip install hfm==0.2.13
```

### 使用 conda 安裝（原始方法）

```console
conda install agd
conda install -c agd-lbr hfm=0.2.13
```

---

## 執行應用程式

```console
python crack_tool.py
```

語言切換器（English / 繁體中文）位於視窗底部狀態列右側，切換後立即生效，無需重新啟動。

---

## 引用

如果您在自己的工作中使用此程式碼或應用程式，請引用：

> [1] Kompanets, A., Duits, R., Leonetti, D., van den Berg, N., Snijder, H.H. (2024). *Segmentation Tool for Images of Cracks.* ICCCBE 2022, LNCE vol. 357. Springer. https://doi.org/10.1007/978-3-031-35399-4_8

---

# 應用程式教學

## 「選擇影像」標籤

#### 開始標註
1. 點擊 **選擇資料夾** 以開啟原生資料夾瀏覽對話框，選擇包含影像的資料夾。
2. 資料夾內的影像清單將顯示在左側。若已有標註檔案，標註內容會自動顯示。

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/1.gif)

#### 邊界框標註（可選）
1. 設定 **影像大小** 以調整繪製視窗大小。
2. 按下 **繪製框** 開啟繪製視窗。
3. 繪製單個邊界框：
   - 滑鼠滾輪 — 放大 / 縮小
   - 左鍵 — 選擇第一個角落；再次左鍵選擇對角
   - 右鍵 — 撤銷上一步
   - Esc — 關閉視窗
4. 在 **類別** 欄位設定整數（0 = 裂縫，1 = 腐蝕，或任意整數）。
5. 按下 **儲存框** 以儲存至標註檔案。
6. **清除框** 可移除所有框；**清除分割** 可移除所有裂縫像素。

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/2.gif)

---

## 「追蹤」標籤

#### 選擇裂縫端點
1. 按下 **選擇裂縫端點**。
2. 調整 **影像大小** 以適應螢幕。
3. 滑鼠滾輪縮放；左鍵選點；右鍵撤銷。
4. 選擇兩個點（裂縫尖端），然後按 Esc。

#### 裁切影像
1. 依據對比選擇 **深色裂縫** 或 **亮色裂縫**。
2. 選擇對比度最高的顏色通道。
3. 設定 **降採樣係數** 以縮減影像大小，加快處理速度。
4. 設定 **X / Y 邊距** 讓裂縫完整落在裁切區域內。
5. 按下 **更新裁切影像** — 按鈕下方 LCD 顯示裁切後大小。

#### （可選）設計小波
1. 按下 **檢查小波** 預覽蛋糕小波。
2. 按下 **選擇裂縫點以檢查寬度** 選擇具代表性的裂縫中點。
3. 按下 **更新** 顯示裂縫中點區域。
4. 調整小波參數，使其亮色中心寬度接近裂縫寬度。

#### 建立方向分數與費用函數
1. 按下 **更新 OS**（背景執行，進度條完成後代表結束）。
2. 按下 **更新費用函數**（同樣為背景執行）。
3. 調整費用函數參數，使投影圖上的裂縫反應最佳化。

#### 裂縫追蹤
1. 按下 **裂縫追蹤** 執行追蹤算法（背景執行）。
2. 調整 g11、g22、g33（參數說明見 [1]）。
3. 調整 **追蹤寬度** / **追蹤顏色** 僅影響視覺化。
4. 按下 **更新追蹤顯示** 或 **追蹤全螢幕** 檢視結果。

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/3.gif)

---

## 「分割」標籤

#### 擷取裂縫邊緣
1. 設定 **濾波器大小**（邊緣可從追蹤路徑延伸的距離）。
2. 按下 **邊緣遮罩**。
3. 調整 mu、l、p 參數。
4. 按下 **邊緣追蹤**。
5. 按下 **邊緣追蹤全螢幕** 可全螢幕預覽結果。

#### 儲存區段
按下 **儲存分割** 以提交目前的分割遮罩。可重複此流程在同一影像上新增多個區段。最終會在影像旁建立包含所有像素座標的 JSON 檔案。

讀取 JSON 檔案的方式請參考 `notebooks/generate_mask_from_json.ipynb`。

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/4.gif)

---

## 「手動新增分割」標籤

1. 按下 **繪製分割** 開啟繪製視窗。
2. 滑鼠滾輪縮放。
3. 按住左鍵拖曳繪製輪廓段；放開以固定。再次按左鍵開始新段（自動以直線連接）。
4. 右鍵撤銷上一段。
5. Esc 關閉視窗 — 輪廓自動封閉。
6. 按下 **儲存分割** 將其加入標註遮罩。

![](https://github.com/akomp22/crack-segmentation-tool/blob/main/video/gif/5.gif)
