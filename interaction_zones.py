import os
import re
import argparse
import numpy as np
import pandas as pd

# Keypoint indices
PELVIS_IDX = 0
LSHOULDER_IDX = 8
RSHOULDER_IDX = 9

# Distance classification function
def classify_distance(distance, intimate_th, personal_th, social_th):
    if distance <= intimate_th:
        return "Intimate"
    elif distance <= personal_th:
        return "Personal"
    elif distance <= social_th:
        return "Social"
    else:
        return "Out of Range"

# Find valid frames
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

# Load 3D_coor_world for a given file
def load_coor_world(filepath):
    data = np.load(filepath)
    coor_world = data['3D_coor_world']
    pelvis = coor_world[PELVIS_IDX]
    lshoulder = coor_world[LSHOULDER_IDX]
    rshoulder = coor_world[RSHOULDER_IDX]
    sternum = (lshoulder + rshoulder) / 2
    cm = (pelvis + sternum) / 2
    return cm

def main(folder_path, intimate_th, personal_th, social_th):
    valid_frames = find_valid_frames(folder_path)
    print(f"Found {len(valid_frames)} valid frames.")

    results = []
    
    for frame_num in valid_frames:
        adult_file = os.path.join(folder_path, f"{frame_num:05d}_adult.npz")
        kid_file = os.path.join(folder_path, f"{frame_num:05d}_kid.npz")
        
        try:
            cm_adult = load_coor_world(adult_file)
            cm_kid = load_coor_world(kid_file)
            distance = np.linalg.norm(cm_adult - cm_kid)
            zone = classify_distance(distance, intimate_th, personal_th, social_th)
            
            results.append({
                'frame': frame_num,
                'distance_m': distance,
                'zone': zone
            })
        except Exception as e:
            print(f"Error processing frame {frame_num}: {e}")
    
    df = pd.DataFrame(results)
    print(df)
    
    # Optionally save to CSV
    output_path = os.path.join(folder_path, "interaction_zones.csv")
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interaction Zones Analysis")
    parser.add_argument("folder_path", type=str, help="Path to folder containing .npz files")
    parser.add_argument("--intimate", type=float, default=0.45, help="Threshold for intimate distance (default: 0.45 m)")
    parser.add_argument("--personal", type=float, default=1.2, help="Threshold for personal distance (default: 1.2 m)")
    parser.add_argument("--social", type=float, default=3.0, help="Threshold for social distance (default: 3.0 m)")
    args = parser.parse_args()
    
    main(args.folder_path, args.intimate, args.personal, args.social)
