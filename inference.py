import torch
import numpy as np
import h5py
from model import CycloneIntensityNet

# IMD Official Classification Scale
def get_imd_category(wind_kts):
    if wind_kts < 34:
        return "Depression / Deep Depression (< 34 kts)"
    elif wind_kts <= 47:
        return "Cyclonic Storm (34 - 47 kts)"
    elif wind_kts <= 63:
        return "Severe Cyclonic Storm (48 - 63 kts)"
    elif wind_kts <= 89:
        return "Very Severe Cyclonic Storm (64 - 89 kts)"
    elif wind_kts <= 119:
        return "Extremely Severe Cyclonic Storm (90 - 119 kts)"
    else:
        return "Super Cyclonic Storm (>= 120 kts)"

device = torch.device("cpu")

# Load model weights
model = CycloneIntensityNet(in_channels=4, num_classes=6, pretrained=False)
model.load_state_dict(torch.load("models/cyclone_model.pth", map_location=device))
model.eval()
print("Model loaded successfully from models/cyclone_model.pth!")

# Load sample index 15 from local HDF5 dataset
with h5py.File("data/Cyclone_Images.h5", 'r') as f:
    sample_img = f['Images'][15]

# Preprocess: (H, W, C) -> (1, C, H, W)
sample_tensor = np.transpose(sample_img, (2, 0, 1))
sample_tensor = np.nan_to_num(sample_tensor, nan=0.0)
sample_tensor = np.clip(sample_tensor, 0.0, 1.0) if sample_tensor.max() <= 1.0 else sample_tensor / 255.0
input_tensor = torch.tensor(sample_tensor, dtype=torch.float32).unsqueeze(0)

# Run Inference
with torch.no_grad():
    pred_wind, _ = model(input_tensor)
    wind_kts = pred_wind.item()

category = get_imd_category(wind_kts)

print("\n==========================================")
print("       CYCLONE INTENSITY REPORT           ")
print("==========================================")
print(f"Estimated Wind Speed: {wind_kts:.1f} knots ({wind_kts * 1.852:.1f} km/h)")
print(f"IMD Intensity Stage: {category}")
print("==========================================\n")