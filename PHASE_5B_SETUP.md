# Phase 5B – MedSAM Integration Setup

This guide helps you enable the MedSAM model for local medical image analysis.

Phase 5B is fully wired into the backend. You only need to add the model weights and (optionally) install the SAM predictor to enable interactive-quality masks.

## 1) Prerequisites

- Python environment already set up (backend/venv)
- Torch installed (already pinned in `backend/requirements.txt`)
- Optional (recommended): `segment_anything` package for the official SAM predictor

Install (optional) SAM predictor:

```powershell
# CPU-only install of segment-anything directly from GitHub (recommended)
pip install git+https://github.com/facebookresearch/segment-anything.git
```

If you prefer, you can proceed without the predictor; the system will fall back to a heuristic mask.

## 2) Get MedSAM Checkpoint

Obtain a MedSAM (SAM fine-tuned for medical images) checkpoint file (e.g., `sam_vit_b_medsam.pth`).

- Place it on disk, for example: `C:\models\medsam\sam_vit_b_medsam.pth`
- Note the absolute path

## 3) Configure Environment

Use the helper script to set environment variables in `backend/.env`:

```powershell
cd backend\scripts
# Update checkpoint path, device, and model variant (vit_b|vit_l|vit_h)
./configure_phase5.ps1 -CheckpointPath "C:\\models\\medsam\\sam_vit_b_medsam.pth" -Device "cpu" -Model "vit_b"
```

This adds/updates the following entries in `backend/.env`:

```
PHASE5_MEDSAM_CHECKPOINT=C:\\models\\medsam\\sam_vit_b_medsam.pth
PHASE5_DEVICE=cpu
PHASE5_MEDSAM_MODEL=vit_b
```

> Tip: If you have a compatible NVIDIA GPU, set `-Device "cuda:0"`.

## 4) Start the backend

```powershell
# From repository root
./start-backend.ps1
```

## 5) Switch to MedSAM

Use the API to activate the MedSAM model:

```powershell
# PowerShell
Invoke-WebRequest -Method Post -Uri "http://127.0.0.1:8000/api/phase-5/models/switch?model_id=medsam_v1"
```

If successful, `/api/phase-5/health` will show `phase: 5B - MedSAM active` and analyzer stats will report `model_version: medsam_v1`.

## 6) Validate with Hybrid Mode

Upload an image and compare local MedSAM vs Claude Vision to build confidence:

- POST `/api/phase-5/image/analyze-hybrid` (form-data: `image`, `image_type`, `clinical_context`)

The response includes:
- Both analyses
- Confidence delta
- Speed comparison
- Cost difference (local = $0.00)

## Notes

- If you see `Missing or invalid PHASE5_MEDSAM_CHECKPOINT`, re-check the file path in `.env`.
- If `segment_anything` isn’t installed, the system gracefully uses an intensity-based fallback mask.
- You can switch back anytime:

```powershell
Invoke-WebRequest -Method Post -Uri "http://127.0.0.1:8000/api/phase-5/models/switch?model_id=rule_based_v1"
```

## What’s Next (Phase 5C)

- Collect labeled cases and fine-tune on your dataset
- Target 90%+ accuracy with domain-specific adaptation
- Keep hybrid mode for continuous validation
