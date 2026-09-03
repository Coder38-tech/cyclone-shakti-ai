import os
import glob
import h5py
import numpy as np

data_dir = "data"
print("Contents of 'data/':", os.listdir(data_dir))

# ── HDF5 images ──────────────────────────────────────────────────────────────
h5_files = glob.glob(os.path.join(data_dir, "**/*.h5"), recursive=True)
if h5_files:
    print(f"\nFound HDF5 file: {h5_files[0]}")
    with h5py.File(h5_files[0], 'r') as f:
        print("Keys available in H5:")
        for key in f.keys():
            item = f[key]
            if hasattr(item, 'shape'):
                print(f"  - {key}: shape={item.shape}, dtype={item.dtype}")
            else:
                print(f"  - Group: {key}")
else:
    print("\nNo HDF5 files found.")

# ── NumPy labels ──────────────────────────────────────────────────────────────
npy_files = glob.glob(os.path.join(data_dir, "**/*.npy"), recursive=True)
if npy_files:
    print(f"\nFound NumPy file: {npy_files[0]}")
    data = np.load(npy_files[0], allow_pickle=True)  # allow_pickle required for object/structured arrays

    if isinstance(data, np.lib.npyio.NpzFile):
        print("Keys inside NPZ:", data.files)
        for k in data.files:
            arr = data[k]
            print(f"  - {k}: shape={arr.shape}, dtype={arr.dtype}")
            print(f"    First 5 values: {arr[:5]}")
    else:
        print(f"  Shape : {data.shape}")
        print(f"  dtype : {data.dtype}")
        print(f"  First 5 values: {data[:5]}")
else:
    print("\nNo NumPy (.npy) files found.")
