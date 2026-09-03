import torch
from torch.utils.data import Dataset, DataLoader
import h5py
import numpy as np

def wind_to_imd_class(knots):
    """
    Maps wind speed (knots) to official IMD categories:
    0: Low Pressure Area / Depression (< 34 kt)
    1: Cyclonic Storm (34 - 47 kt)
    2: Severe Cyclonic Storm (48 - 63 kt)
    3: Very Severe Cyclonic Storm (64 - 89 kt)
    4: Extremely Severe Cyclonic Storm (90 - 119 kt)
    5: Super Cyclonic Storm (>= 120 kt)
    """
    if knots < 34:
        return 0
    elif knots <= 47:
        return 1
    elif knots <= 63:
        return 2
    elif knots <= 89:
        return 3
    elif knots <= 119:
        return 4
    else:
        return 5

class TCIRDataset(Dataset):
    def __init__(self, h5_path="data/Cyclone_Images.h5", npy_path="data/Cyclone_Labels h5.npy", split="train", split_ratio=0.85):
        self.h5_path = h5_path
        
        # Load labels into memory
        labels_raw = np.load(npy_path, allow_pickle=True)
        self.winds = labels_raw[:, 5].astype(np.float32)
        self.pressures = labels_raw[:, 7].astype(np.float32)
        
        total_len = len(self.winds)
        split_point = int(total_len * split_ratio)
        
        # Deterministic train/test split
        np.random.seed(42)
        indices = np.random.permutation(total_len)
        self.indices = indices[:split_point] if split == "train" else indices[split_point:]
        
        self.h5_file = None  # Lazy loading for multi-processing compatibility

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        if self.h5_file is None:
            self.h5_file = h5py.File(self.h5_path, 'r')
            
        real_idx = self.indices[idx]
        
        # Load 4-channel image (128, 128, 4)
        img = self.h5_file['Images'][real_idx]
        
        # Transpose from (H, W, C) -> (C, H, W) for PyTorch
        img = np.transpose(img, (2, 0, 1))
        
        # Handle missing / invalid sensor readings
        img = np.nan_to_num(img, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Min-Max normalisation across channels
        img = np.clip(img, 0.0, 1.0) if img.max() <= 1.0 else img / 255.0

        wind = self.winds[real_idx]
        imd_class = wind_to_imd_class(wind)

        return (
            torch.tensor(img, dtype=torch.float32),
            torch.tensor(wind, dtype=torch.float32),
            torch.tensor(imd_class, dtype=torch.long)
        )

if __name__ == "__main__":
    train_ds = TCIRDataset(split="train")
    train_loader = DataLoader(train_ds, batch_size=8, shuffle=True)
    images, winds, classes = next(iter(train_loader))
    
    print(f"Images batch shape: {images.shape}")    # [8, 4, 128, 128]
    print(f"Wind target shape:  {winds.shape}")     # [8]
    print(f"Sample wind speeds: {winds.tolist()}")
    print(f"Sample IMD classes: {classes.tolist()}")