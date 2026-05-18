import torch
import torch.nn as nn

# Unified Source Theory (UST) v0 - Sealed Constants
NSQ = 0.63354460

class UST_Layer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.init_weights()

    def init_weights(self):
        # Weight initialization scaled by the Nsq stabilization constant
        nn.init.kaiming_uniform_(self.linear.weight, a=NSQ)
        if self.linear.bias is not None:
            nn.init.constant_(self.linear.bias, 0.01 * NSQ)

def calculate_ust_loss(outputs, targets, model, lambda_s=1e-4):
    """
    Implements Theorem 12: S = 0 (Global Action Balance)
    Stabilizes the manifold by penalizing informational leakage (noise).
    """
    mse = nn.functional.mse_loss(outputs, targets)
    
    # Audit Layer: Balancing Energy (Loss) and Geometry (Parameters)
    complexity = sum(p.pow(2).sum() for p in model.parameters())
    s_audit = torch.abs((mse + complexity) * NSQ)
    
    return mse + (lambda_s * s_audit)

# Usage Example
# model = nn.Sequential(UST_Layer(128, 64), nn.ReLU(), UST_Layer(64, 1))
# loss = calculate_ust_loss(outputs, targets, model)