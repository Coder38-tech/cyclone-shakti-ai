import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import os
import time

from dataset import TCIRDataset
from model import CycloneIntensityNet

# Hardware configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Hyperparameters
BATCH_SIZE = 32 if torch.cuda.is_available() else 16
LEARNING_RATE = 1e-4
EPOCHS = 5  # Quick baseline run for the prototype
CHECKPOINT_DIR = "models"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# Datasets & Loaders
print("Loading train and validation datasets...")
train_dataset = TCIRDataset(split="train", split_ratio=0.85)
val_dataset = TCIRDataset(split="val", split_ratio=0.85)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
print(f"Total training samples: {len(train_dataset)} | Validation samples: {len(val_dataset)}")

# Initialize Multi-Task Network (4 input channels: IR, WV, VIS, PMW; 6 IMD categories)
model = CycloneIntensityNet(in_channels=4, num_classes=6, pretrained=True).to(device)

# Loss functions: Smooth L1 for wind speed regression, Cross-Entropy for IMD category
criterion_reg = nn.SmoothL1Loss()
criterion_cls = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-2)

best_val_mae = float("inf")

# Training Loop
for epoch in range(1, EPOCHS + 1):
    start_time = time.time()
    model.train()
    running_loss = 0.0
    total_samples = 0
    
    for batch_idx, (images, true_winds, true_classes) in enumerate(train_loader):
        images = images.to(device)
        true_winds = true_winds.to(device)
        true_classes = true_classes.to(device)
        
        optimizer.zero_grad()
        
        pred_winds, pred_logits = model(images)
        
        # Combined multi-task loss
        loss_reg = criterion_reg(pred_winds, true_winds)
        loss_cls = criterion_cls(pred_logits, true_classes)
        total_loss = loss_reg + 0.5 * loss_cls
        
        total_loss.backward()
        optimizer.step()
        
        running_loss += total_loss.item() * images.size(0)
        total_samples += images.size(0)
        
        if (batch_idx + 1) % 25 == 0 or (batch_idx + 1) == len(train_loader):
            print(f"Epoch [{epoch}/{EPOCHS}] | Step [{batch_idx+1}/{len(train_loader)}] | Batch Loss: {total_loss.item():.4f}")

    train_loss = running_loss / total_samples

    # Validation Loop
    model.eval()
    val_mae_sum = 0.0
    val_correct_classes = 0
    total_val_samples = 0
    
    with torch.no_grad():
        for images, true_winds, true_classes in val_loader:
            images = images.to(device)
            true_winds = true_winds.to(device)
            true_classes = true_classes.to(device)
            
            pred_winds, pred_logits = model(images)
            
            # MAE in knots
            val_mae_sum += torch.sum(torch.abs(pred_winds - true_winds)).item()
            
            # Accuracy on IMD category
            preds = torch.argmax(pred_logits, dim=1)
            val_correct_classes += torch.sum(preds == true_classes).item()
            total_val_samples += images.size(0)

    val_mae = val_mae_sum / total_val_samples
    val_acc = (val_correct_classes / total_val_samples) * 100
    elapsed = time.time() - start_time

    print(f"\n--- Epoch {epoch} Finished ({elapsed:.1f}s) ---")
    print(f"Train Loss: {train_loss:.4f} | Val Wind MAE: {val_mae:.2f} knots | Val Category Acc: {val_acc:.2f}%\n")
    
    # Save checkpoint if it improves validation MAE
    if val_mae < best_val_mae:
        best_val_mae = val_mae
        torch.save(model.state_dict(), os.path.join(CHECKPOINT_DIR, "best_cyclone_model.pth"))
        print(f"Saved new best model checkpoint with MAE: {best_val_mae:.2f} kt\n")

print("Training cycle complete. Check 'models/best_cyclone_model.pth'.")