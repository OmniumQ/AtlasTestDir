# ⚙️ OX-1 Hardware: Engineering Bill of Materials (BOM)

## 1. Computational Core (OPU - Omnium Processing Unit)
- **Node:** 3nm Custom ASIC.
- **Transistor Logic:** Gallium Nitride (GaN) for high-frequency $N_{s,q}$ switching.
- **Frequency:** Phase-locked at $1.990339$ GHz ($\pi \cdot N_{s,q}$).
- **Function:** Real-time execution of the Seeley-DeWitt $a_2$ corrective operator.

## 2. Memory Architecture (Channel C Emulation)
- **Type:** HBM3 (8-high Stack).
- **Capacity:** 64 GB.
- **Addressing:** Non-linear memory mapping to simulate inter-channel tunneling (T10).
- **Integrity:** ECC (Error Correction Code) tuned to $S=0$ action balance.

## 3. Electromagnetic Shielding
- **Material:** 1.5mm Mu-Metal / Copper composite.
- **Design:** Internal Faraday Cage to protect Q-resonant circuits from ambient EMI noise.

## 4. Power Delivery (VRM)
- **Phase Array:** 24-phase digital control.
- **Inductors:** High-permeability alloy coils to minimize magnetic flux leakage into the OPU.

## 5. Thermal Management
- **Type:** Liquid-to-Vapor active cooling.
- **Objective:** Maintain core temperature within $\pm 0.01^\circ C$ to prevent $a_2$ invariant drift.

## 6. Bus Interface
- **Standard:** PCIe Gen4 x16 (Forward compatible with Gen5).
- **Sync:** Asynchronous data from Host PC is buffered and re-clocked to the internal $1.99...$ GHz standard via the NEFİ phase.

**Lead Engineer:** Niyazi OCAL
**Status:** PRODUCTION SPECIFICATION SEALED
