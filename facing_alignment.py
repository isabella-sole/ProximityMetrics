import os
import re
import argparse
import numpy as np
import pandas as pd

# Keypoint indices for 2D_coor (pixel positions)
NOSE_IDX = 24
LEFT_EYE_IDX = 22
RIGHT_EYE_IDX = 23
LEFT_EAR_IDX = 20
RIGHT_EAR_IDX = 21

# Valid frame selector (reused from part 1)
def find_valid_frames(folder_path):
    pattern = re.compile(r"(\d+)_([a-zA-Z]+)\.npz")
    adult_frames, kid_frames = set(), set()
    
    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            frame_num, participant = match.groups()
            frame_num = int(frame_num)
            if participant.lower() == 'adult':
                adult_frames.add(frame_num)
            elif participant.lower() == 'kid':
                kid_frames.add(frame_num)
                
    valid_frames = sorted(adult_frames.intersection(kid_frames))
    return valid_frames

# Function to load 2D facial keypoints and calculate head direction vectors
def extract_facing_features(filepath):
    data = np.load(filepath)
    coor_2d = data['2D_coor']

    nose = coor_2d[NOSE_IDX]
    left_eye = coor_2d[LEFT_EYE_IDX]
    right_eye = coor_2d[RIGHT_EYE_IDX]
    left_ear = coor_2d[LEFT_EAR_IDX]
    right_ear = coor_2d[RIGHT_EAR_IDX]

    # 1️⃣ Compute ear midpoint
    ear_midpoint = (left_ear + right_ear) / 2

    # 2️⃣ Facing vector = nose - ear_midpoint
    facing_vector = nose - ear_midpoint

    # 3️⃣ Head center = average of 5 facial landmarks
    head_center = (nose + left_eye + right_eye + left_ear + right_ear) / 5

    return facing_vector, head_center

# Cosine similarity calculation (with small epsilon for safety)
def compute_cosine(facing_vector, to_other_vector):
    norm_facing = np.linalg.norm(facing_vector) + 1e-8
    norm_other = np.linalg.norm(to_other_vector) + 1e-8
    cos_theta = np.dot(facing_vector, to_other_vector) / (norm_facing * norm_other)
    return cos_theta

# Categorize cosine similarity into head facing categories
def categorize_cosine(cos_theta):
    if cos_theta >= 0.7:
        return "Facing"
    elif cos_theta >= 0.3:
        return "Partial"
    elif cos_theta >= -0.3:
        return "Perpendicular"
    else:
        return "Facing Away"

# Main pipeline
def main(folder_path):
    valid_frames = find_valid_frames(folder_path)
    print(f"Found {len(valid_frames)} valid frames.")

    results = []

    for frame_num in valid_frames:
        adult_file = os.path.join(folder_path, f"{frame_num:05d}_adult.npz")
        kid_file = os.path.join(folder_path, f"{frame_num:05d}_kid.npz")

        try:
            # Load adult
            adult_facing_vector, adult_head_center = extract_facing_features(adult_file)
            # Load kid
            kid_facing_vector, kid_head_center = extract_facing_features(kid_file)

            # Compute cosine similarity for adult
            to_kid_vector = kid_head_center - adult_head_center
            adult_cosine = compute_cosine(adult_facing_vector, to_kid_vector)
            adult_category = categorize_cosine(adult_cosine)

            # Compute cosine similarity for kid
            to_adult_vector = adult_head_center - kid_head_center
            kid_cosine = compute_cosine(kid_facing_vector, to_adult_vector)
            kid_category = categorize_cosine(kid_cosine)

            both_facing = (adult_cosine >= 0.7) and (kid_cosine >= 0.7)

            results.append({
                'frame': frame_num,
                'adult_cosine': round(adult_cosine, 3),
                'adult_category': adult_category,
                'kid_cosine': round(kid_cosine, 3),
                'kid_category': kid_category,
                'both_facing': both_facing
            })

        except Exception as e:
            print(f"Error processing frame {frame_num}: {e}")

    df = pd.DataFrame(results)
    print(df)

    output_path = os.path.join(folder_path, "reciprocal_facing.csv")
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reciprocal Facing Alignment Analysis")
    parser.add_argument("folder_path", type=str, help="Path to folder containing .npz files")
    args = parser.parse_args()

    main(args.folder_path)
