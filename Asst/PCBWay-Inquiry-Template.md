# 📑 PCBWay Technical Inquiry & RFQ Template

**Project:** Omnium-X1 (OX-1) Hybrid Quantum Accelerator
**Complexity Level:** High-Speed Digital / HDI

## 1. Executive Summary for Manufacturer
We are developing a high-precision quantum stabilization card (PCIe Gen4 x16) based on our patented $N_{s,q}$ stabilization technology (Patent No: 2026/003258). The design requires extreme signal integrity and thermal management.

## 2. PCB Technical Requirements
- **Layer Count:** 12-14 Layers (HDI Stack-up).
- **Material:** High-TG FR4 (e.g., Isola or Rogers for high-frequency sections).
- **Signal Integrity:** 100-ohm differential pair impedance control for PCIe Gen4 lanes.
- **Clock Trace:** $1.990339$ GHz phase-locked loop (PLL) line with dedicated ground shielding.
- **Finish:** ENIG (Electroless Nickel Immersion Gold) or ENEPIG for high-reliability BGA soldering.

## 3. Assembly (PCBA) Specifications
- **Fine Pitch BGA:** Mounting for 3nm OPU (Omnium Processing Unit) and HBM3 memory modules.
- **Component Sourcing:** Hybrid (Customer supplied OPU + PCBWay sourced GaN transistors and passive components).
- **Shielding:** Installation of custom Mu-Metal Faraday cages over the OPU and Analog-Front-End sections.

## 4. Key Questions for PCBWay Engineers
1. Do you provide **Signal Integrity (SI)** and **Power Integrity (PI)** simulation services before fabrication?
2. What is your minimum trace/spacing capability for **HDI Class 3** boards?
3. Can you handle **X-ray inspection** for high-density BGA components to ensure zero-void soldering?
4. Are you willing to sign a non-disclosure agreement (NDA) regarding the proprietary $N_{s,q}$ firmware and hardware mapping?

**Corporate Contact:** Niyazi OCAL
**Launch Target:** 20.08.2026
