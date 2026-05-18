import torch
import torch.nn as nn
import torch.nn.functional as F

NSQ = 0.63354460
TOM = 0.23252900

def initialize_ust_weights(model):
    for m in model.modules():
        if isinstance(m, (nn.Linear, nn.Conv2d)):
            nn.init.kaiming_uniform_(m.weight, a=NSQ)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0.01 * NSQ)

def calculate_ust_loss(pred, target, model, penalty_weight=1e-4):
    base_loss = F.mse_loss(pred, target)
    complexity = sum(p.pow(2).sum() for p in model.parameters())
    s_balance = torch.abs((base_loss + complexity) * NSQ)
    return base_loss + (penalty_weight * s_balance)

def apply_ust_pruning(model):
    with torch.no_grad():
        for name, param in model.named_parameters():
            if 'weight' in name:
                threshold = TOM * torch.std(param)
                param.mul_(torch.abs(param) > threshold)