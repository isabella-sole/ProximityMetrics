# Interaction Zones Analysis
# 1. ProximityMetrics
This repository contains a Python script to analyze physical proximity between adult and infant during interaction tasks using 3D keypoints extracted from video recordings.

The analysis is based on 3D full-body pose estimations stored in `.npz` files for each frame and each participant.  
The goal is to classify the physical distance between participants into behavioral proximity zones: **Intimate, Personal, and Social**.

---

## 📦 Dataset Structure

The input folder must contain multiple `.npz` files with the following structure:

- Each `.npz` file represents one frame for one participant.
- Filenames must follow this convention:

```
{FRAME_NUMBER}_{PARTICIPANT}.npz
```

- Example:

```
00001_adult.npz
00001_kid.npz
00002_adult.npz
00003_kid.npz
00004_adult.npz
...
```

- The dataset may contain missing files: some frames may have only adult or only kid files.  
  These gaps are automatically handled by the script.

---

## 🔎 What the Code Does

### 1️⃣ Frame Synchronization

- The script automatically detects valid frames where both adult and kid files are available.
- Frames where either participant is missing are excluded from the analysis.

### 2️⃣ 3D Keypoint Processing

- The script loads the `3D_coor_world` array from each `.npz` file (absolute world coordinates).
- It extracts 3 keypoints:
  - **Pelvis** (index `0`)
  - **Left Shoulder** (index `8`)
  - **Right Shoulder** (index `9`)
- The sternum position is approximated as the midpoint between Left and Right Shoulder:

```
Sternum = (LeftShoulder + RightShoulder) / 2
```

- The participant’s "center of mass" (CM) is then estimated as:

```
CM = (Pelvis + Sternum) / 2
```

### 3️⃣ Distance Calculation

- For each valid frame, the 3D Euclidean distance between adult and kid CM points is computed:

```
D_CM = sqrt((x_adult - x_kid)^2 + (y_adult - y_kid)^2 + (z_adult - z_kid)^2)
```

- This fully takes into account all 3 spatial dimensions.

### 4️⃣ Behavioral Zone Classification

- The computed distance is classified into 4 proximity zones based on user-defined thresholds:

| Zone       | Distance (meters)   |
|------------|---------------------|
| Intimate   | 0 – INTIMATE_THRESHOLD |
| Personal   | INTIMATE_THRESHOLD – PERSONAL_THRESHOLD |
| Social     | PERSONAL_THRESHOLD – SOCIAL_THRESHOLD |
| Out of Range | Greater than SOCIAL_THRESHOLD |

- The default thresholds are based on literature, but can be adjusted when running the script.

---

## 🚀 How to Use

### 1️⃣ Requirements

- Python 3.8+
- Install dependencies:

```bash
pip install numpy pandas
```

### 2️⃣ Running the script

Basic usage (with default thresholds):

```bash
python interaction_zones.py /path/to/your/data/folder
```

Example:

```bash
python interaction_zones.py ./dataset/session_01/
```

### 3️⃣ Optional: Customize thresholds

You can override the default thresholds directly from terminal:

```bash
python interaction_zones.py /path/to/your/data/folder --intimate 0.5 --personal 1.0 --social 2.5
```

- `--intimate` → upper bound for Intimate zone
- `--personal` → upper bound for Personal zone
- `--social` → upper bound for Social zone

### 4️⃣ Output

- The script prints out:
  - Total valid frames analyzed
  - The computed distances and zones for each frame

- A full CSV report `interaction_zones.csv` is saved inside the input folder:

| frame | distance_m | zone |
|-------|------------|------|
| 15    | 0.203      | Intimate |
| 16    | 0.745      | Personal |
| 17    | 1.985      | Social |

---

## ⚠ Notes

- Only frames where both `adult` and `kid` files are present are analyzed.
- Make sure your filenames strictly follow the `{frame}_{participant}.npz` convention.
- This script works directly on 3D absolute world coordinates (`3D_coor_world`).

---

## 📈 Why Use World Coordinates?

- Using `3D_coor_world` eliminates scaling and camera biases.
- Full 3D Euclidean distances allow accurate real-world proximity estimation, even when participants are at different heights or orientations.

---

## ✅ Ready for extension

This code is fully ready for:

- Adding reciprocal facing alignment features (coming next step).
- Integration into longitudinal studies.
- Batch processing across sessions.

---

## 👩‍💻 Author
Isabella-Sole Bisio

---
