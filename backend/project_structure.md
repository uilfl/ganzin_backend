backend/
│
├── app.py # FastAPI 主入口 (或 main.py)
│
├── models/ # 所有資料型別 dataclass/schema
│ ├── **init**.py
│ ├── gaze_point.py
│ ├── aoi_element.py
│ ├── calibration_sample.py
│ ├── hit_log.py
│ ├── cognitive_load.py
│
├── manager/ # 系統主要流程&功能模組
│ ├── **init**.py
│ ├── gaze_manager.py # gaze stream/record/分析主體
│ ├── calibration.py # 校正流程
│ ├── aoi.py # AOI 管理/驗證/自動產生
│ ├── hitlog.py # AOI 命中紀錄與匯出
│ ├── session_manager.py # (可選) session 控制
│
├── utils/ # 共用工具、分析、json 匯出
│ ├── **init**.py
│ ├── export.py
│ ├── analysis.py
│
├── data/ # 儲存所有 session raw/export 資料
│ ├── ...
│
├── requirements.txt
└── README.md

## Use the example code for our manager works

1. gaze_streaming.py 可直接用於 gaze_manager.py
   • 官方 sample gaze_streaming.py 展示了如何連線、啟動 gaze 資料串流、每次獲取 gaze event，流程簡單明確。
   • 你只需要把 sample 中的串流初始化、事件 loop、資料欄位 mapping 直接抄進 GazeDataManager 裡的 streaming thread 或 async 任務即可。
   • 建議你用 class/函式包裝，這樣管理多 session、停止/重啟 stream 都容易。

⸻

2. capture_frame_and_gaze.py（擷取單幀 + gaze）

可用的地方：
• 一次性擷取「現場畫面」+ gaze point，方便 debug/製作 ground truth/用於 calibration 時儲存 sample。
• 可延伸做「每次命中 AOI 就截圖存證」，或同步錄影/label gaze。

你要怎麼用？
• 把其中「擷取場景影像」+「同步 gaze 資料」的邏輯，做成你 GazeDataManager 內的 capture_snapshot_with_gaze() 函數。
• 在 AOI hit 或特定事件時呼叫，直接存圖+gaze 到 data 資料夾。

⸻

3. get_scene_camera_parameters.py（獲取相機內參）

可用的地方：
• 若要做 3D gaze 投影到螢幕或空間座標，必須有 scene camera 參數（焦距、主點、畸變等）。
• 你可以每次啟動時自動讀取 scene camera 內參，存成 json，供所有 3D → 2D 投影計算用。

你要怎麼用？
• 取出 sample 內參數解析那段 code，包裝成 get_scene_camera_intrinsics() 函數。
• 在 GazeDataManager 啟動時自動取得，或分析時讀 json 直接用。

⸻

4. add_tag.py / add_tag_with_corrected_timestamp.py（事件標記）

可用的地方：
• 當你偵測到 gaze 命中 AOI、或用戶執行特定動作時，可以自動產生 tag（事件標籤）存回 log。
• 有助於後續資料分析，如「用戶在某區看了幾次」「某行為發生時的 gaze 狀態」。

你要怎麼用？
• 將範例的 tag 產生/寫入方法改為「AOI hit」時自動寫 hit_log.json，或直接寫入 session hit_log list。
• 可以用在分析、debug 或同步事件紀錄。

好的，這裡是調整你原本後端架構、加強資料記錄與擴充性的建議步驟，讓你未來能更好地整合 Sol Glasses，提升資料分析與整體體驗！

⸻

一、調整後端專案架構的步驟

1. 資料結構（models/）集中化
   • 把所有重要資料格式（如 GazePoint、AOIElement、HitLog、CalibrationSample、CognitiveLoad）用 dataclass 寫在 models/ 資料夾。
   • 這樣 stream、hit log、校正、分析都能重用同一組格式。

2. 管理流程模組化（manager/）
   • gaze_manager.py：只專心負責 gaze streaming、AOI 判斷、hit log 記錄，呼叫 models 資料結構。
   • 如有校正流程複雜可拆出 calibration.py，或 hitlog/analysis 拆分。

3. 輸出/分析工具（utils/）
   • 寫一個 export.py：負責將一整個 session 的 gaze、AOI、hit log 等序列化為 json（未來分析可直接用）。
   • 寫一個 analysis.py（進階）：提供 AOI 命中次數、熱區分佈、瞳孔變化等基本統計。

4. API 與 session 資料自動儲存
   • 每次一個 session 結束後自動呼叫 export，把所有資料存到 data/ 夾下。
   • 也可加 /api/session/export 讓你手動從後端拉資料包。

⸻

二、加強資料記錄與整合（針對你眼鏡裝置）

A. 記錄內容更完整
• 2D+3D gaze（含 direction）
• pupil size（左右眼）
• gaze 有效性
• AOI 命中記錄（含 aoi_id、gaze timestamp、命中類型 2d/3d）
• 每次 calibration 的所有 sample
• session meta 資訊（start/end, 使用者 id, 裝置 id…）

B. 提升記錄精度與彈性
• 支援每筆 gaze event 都保留原始 + 校正資料
• AOI 若有更新（例如動態內容/滾動），可以讓前端每次傳 AOI 清單或定期更新
• 每次 AOI 命中都 log 下來（hit log）方便熱區、停留時間、行為分析

C. 輸出分析更方便
• 資料格式直接對齊 pandas/Excel，可一鍵做後續統計（不用重寫 mapping）
• 可直接串接可視化/機器學習 pipeline

⸻

三、實作參考架構

資料夾結構建議

backend/
├── app.py # API 主程式
├── models/
│ ├── gaze_point.py
│ ├── aoi_element.py
│ ├── hit_log.py
│ ├── calibration_sample.py
│ ├── cognitive_load.py
├── manager/
│ ├── gaze_manager.py
│ ├── calibration.py
│ ├── aoi.py
│ ├── hitlog.py
├── utils/
│ ├── export.py
│ ├── analysis.py
├── data/
│ ├── (所有 session 匯出檔)
├── requirements.txt
└── README.md

gaze_manager.py 主要邏輯精簡版

from models.gaze_point import GazePoint
from models.aoi_element import AOIElement
from models.hit_log import HitLog

class GazeDataManager:
def **init**(self):
self.gaze_trail = []
self.aoi_elements = {...} # 固定 AOI 或前端動態傳入
self.hit_log = []
def add_gaze_point(self, gaze_data):
self.gaze_trail.append(GazePoint(\*\*gaze_data)) # AOI 判斷，命中就 log
for aoi in self.aoi_elements.values():
if is_gaze_in_aoi(gaze_data, aoi):
self.hit_log.append(HitLog(gaze_timestamp=gaze_data["timestamp"], aoi_id=aoi.id, hit_type="2d")) # ... 其他方法 ...

export.py

import json
def export_session(manager, session_id):
data = {
"session_id": session_id,
"gaze_trail": [asdict(g) for g in manager.gaze_trail],
"aois": {k: asdict(v) for k,v in manager.aoi_elements.items()},
"hit_log": [asdict(h) for h in manager.hit_log], # ... 其他 meta/calibration ...
}
with open(f"data/{session_id}.json", "w") as f:
json.dump(data, f, ensure_ascii=False, indent=2)

⸻

結論與建議
• 這種拆法讓你後端每一部分都可以獨立擴充與調整，不怕複雜。
• 資料一致、分析與維護超省力。
• 你可以直接結合官方 gaze streaming sample，甚至未來換新裝置或 SDK 也能快速適配！

⸻

如要現成 code sample、單檔 code，或要針對實際 device/sdk 快速串接，也可以再直接說！
