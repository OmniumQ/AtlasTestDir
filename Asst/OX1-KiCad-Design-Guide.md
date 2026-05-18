# 📐 OX-1 Hardware: KiCad Design & Prototyping Guide

## 1. Project Initialization
- **Tool:** KiCad 8.0+ (Open Source EDA).
- **PCB Class:** High-Density Interconnect (HDI) - Class 3.
- **Grid Setting:** $0.6335$ mm (Nsq-derived routing grid for harmonic alignment).

## 2. Schematic Hierarchy
- **UST-Sync Block:** The $1.990339$ GHz PLL clock generator.
- **Power Delivery (VRM):** GaN-based 24-phase regulation to ensure $S=0$ stability.
- **Omnium Bridge:** The physical interface between Host PCIe and the OPU core.

## 3. PCB Layout Rules (The Auditor's Rules)
1. **Differential Pairs:** PCIe Gen4 lanes must be length-matched within 0.05mm.
2. **Ground Planes (Channel C):** Continuous copper pours under high-speed traces to minimize EMI.
3. **Guard Traces:** $N_{s,q}$ clock lines must be "nested" with analog ground traces.

## 4. Component Sourcing Checklist
| Category | Component | Sourcing |
| :--- | :--- | :--- |
| Brain | 3nm OPU ASIC | Omnium A.Ş. (In-House) |
| Memory | 64GB HBM3 | Partner Supply (SK Hynix/Samsung) |
| Power | GaN Transistors | PCBWay Turnkey |
| Passive | Resistors/Caps | PCBWay Turnkey |

## 5. First Boot Sequence Logic (Firmware-Level)
1. Power-on Self Test (POST).
2. Check $N_{s,q}$ clock resonance.
3. Synchronize Channel Q buffer with Channel C archive.
4. Open the Omnium Bridge for host communication.

**Lead Architect:** Niyazi OCAL
**Status:** DESIGN WORKFLOW SEALED
