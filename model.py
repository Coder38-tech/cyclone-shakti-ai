import torch
import torch.nn as nn
from torchvision import models

class CycloneIntensityNet(nn.Module):
    def __init__(self, in_channels=4, num_classes=6, pretrained=False):
        super(CycloneIntensityNet, self).__init__()
        weights = models.ResNet34_Weights.DEFAULT if pretrained else None
        self.backbone = models.resnet34(weights=weights)
        
        # Modify conv1 to accept 4-channel satellite inputs (IR, WV, VIS, PMW)
        if in_channels != 3:
            original_conv = self.backbone.conv1
            self.backbone.conv1 = nn.Conv2d(
                in_channels=in_channels,
                out_channels=original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding,
                bias=False
            )
            with torch.no_grad():
                self.backbone.conv1.weight[:, :min(3, in_channels)] = original_conv.weight[:, :min(3, in_channels)]
        
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        # Shared representations
        self.shared_dense = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        
        # Dual-head outputs
        self.regressor = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self.classifier = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        features = self.backbone(x)
        latent = self.shared_dense(features)
        return self.regressor(latent).squeeze(-1), self.classifier(latent)

if __name__ == "__main__":
    test_model = CycloneIntensityNet(in_channels=4, num_classes=6)
    dummy_input = torch.randn(2, 4, 128, 128)
    w, c = test_model(dummy_input)
    print("Model initialized successfully. Output shapes:", w.shape, c.shape)