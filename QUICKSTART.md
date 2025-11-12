# 🚀 HolyGrail Quick Start Guide

## Step 1: Install ComfyUI

### Option A: Standard Installation (Recommended)

```bash
# Navigate to your home directory
cd ~

# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Alternative: Use pip3 if pip doesn't work
pip3 install -r requirements.txt
```

### Option B: Using Virtual Environment (Cleaner)

```bash
# Navigate to your home directory
cd ~

# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option C: Portable Version (Windows)

Download the portable version from:
https://github.com/comfyanonymous/ComfyUI/releases

Unzip and run `run_nvidia_gpu.bat` or `run_cpu.bat`

## Step 2: Start ComfyUI

```bash
cd ~/ComfyUI

# Standard start
python main.py

# Or with specific port/host
python main.py --port 8188 --listen 127.0.0.1

# If using virtual environment, activate it first
source venv/bin/activate  # On macOS/Linux
python main.py
```

**Wait for this message:**
```
To see the GUI go to: http://127.0.0.1:8188
```

You can test by opening http://127.0.0.1:8188 in your browser - you should see the ComfyUI interface.

## Step 3: Add Models

ComfyUI needs at least one checkpoint model to work. Here's where to place them:

### Checkpoint Location
```
~/ComfyUI/models/checkpoints/
```

### Recommended Models to Start

**SD 1.5 (Smaller, faster):**
- Download from: https://huggingface.co/runwayml/stable-diffusion-v1-5
- File: `v1-5-pruned-emaonly.safetensors`
- ~4GB

**SDXL (Higher quality):**
- Download from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- File: `sd_xl_base_1.0.safetensors`
- ~7GB

**Quick Download Example:**
```bash
cd ~/ComfyUI/models/checkpoints/

# Using wget
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors

# Or using curl
curl -L -o v1-5-pruned-emaonly.safetensors https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
```

**Popular Community Models:**
- Visit: https://civitai.com
- Download `.safetensors` files
- Place in `~/ComfyUI/models/checkpoints/`

### LoRA Location (Optional)
```
~/ComfyUI/models/loras/
```

## Step 4: Install HolyGrail

```bash
# Navigate to where you want to install
cd ~

# Clone HolyGrail
git clone <your-repo-url> HolyGrail
cd HolyGrail

# Install dependencies
pip install -r requirements.txt

# Or with pip3
pip3 install -r requirements.txt
```

## Step 5: Start HolyGrail

**Important: Keep ComfyUI running in one terminal!**

Open a **NEW terminal** and run:

```bash
cd ~/HolyGrail
streamlit run app.py
```

Your browser should automatically open to:
```
http://localhost:8501
```

## Troubleshooting

### Issue: "python: command not found"

**Solution:** Use `python3` instead:
```bash
python3 main.py
```

### Issue: "No module named 'torch'"

**Solution:** Install PyTorch:
```bash
# macOS (CPU only)
pip3 install torch torchvision

# macOS (Apple Silicon with MPS)
pip3 install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu

# Linux/Windows with NVIDIA GPU
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Issue: ComfyUI starts but crashes on generation

**Possible causes:**
1. **Out of RAM/VRAM** - Try smaller models or lower resolution
2. **Missing models** - Ensure checkpoint is in `models/checkpoints/`
3. **Corrupted model** - Re-download the checkpoint file

### Issue: "ComfyUI is not running" in HolyGrail

**Check:**
1. Is ComfyUI terminal still running?
2. Can you access http://127.0.0.1:8188 in browser?
3. Did ComfyUI start on a different port? Check the terminal output

**Fix:**
```bash
# In ComfyUI terminal, restart with explicit port
python main.py --port 8188 --listen 127.0.0.1
```

### Issue: "No checkpoints found" in HolyGrail

**Solution:**
1. Ensure at least one `.safetensors` or `.ckpt` file is in `~/ComfyUI/models/checkpoints/`
2. Click "🔄 Refresh Models" button in HolyGrail
3. Check ComfyUI terminal for model loading messages

### Issue: Generation is very slow

**Tips:**
1. **Use SD 1.5** instead of SDXL (faster)
2. **Reduce steps** to 15-20
3. **Lower resolution** (512x512 instead of 1024x1024)
4. **Enable GPU acceleration** if available
5. **Close other GPU-intensive apps**

## Verify Installation

### Check ComfyUI
```bash
cd ~/ComfyUI
ls models/checkpoints/  # Should show .safetensors files
python main.py          # Should start without errors
```

### Check HolyGrail
```bash
cd ~/HolyGrail
ls                      # Should show app.py, requirements.txt, etc.
streamlit run app.py    # Should open browser
```

## System Requirements

### Minimum
- **RAM:** 8GB (16GB recommended)
- **Storage:** 20GB free (for models)
- **GPU:** Not required (CPU works, just slower)

### Recommended
- **RAM:** 16GB+
- **Storage:** 50GB+ (for multiple models)
- **GPU:** NVIDIA with 6GB+ VRAM, or Apple Silicon M1/M2

### Supported Models by Hardware

| Hardware | Recommended Model | Resolution | Speed |
|----------|------------------|------------|-------|
| CPU only | SD 1.5 | 512×512 | Slow (2-5 min) |
| 4GB VRAM | SD 1.5 | 512×512 | Fast (10-30s) |
| 8GB+ VRAM | SDXL | 1024×1024 | Fast (20-60s) |
| 12GB+ VRAM | Flux | 1024×1024 | Fast (30-90s) |

## First Generation Test

1. **Start ComfyUI** (Terminal 1)
2. **Start HolyGrail** (Terminal 2)
3. **In HolyGrail browser:**
   - Select any checkpoint
   - Enter prompt: `"a beautiful sunset over mountains, highly detailed, 8k"`
   - Click **GENERATE**
   - Wait for progress bar
   - Image should appear below!

## Next Steps

Once you have a successful generation:
- ✅ Try different prompts
- ✅ Experiment with samplers
- ✅ Adjust CFG scale and steps
- ✅ Download additional models from CivitAI
- ✅ Add LoRAs for style modifications

## Getting Help

**If you're stuck:**
1. Check ComfyUI terminal for error messages
2. Check HolyGrail terminal for error messages
3. Verify models are in correct folders
4. Try with a fresh SD 1.5 model download
5. Check the main README.md for more details

**Common Error Messages:**

| Error | Cause | Solution |
|-------|-------|----------|
| "CUDA out of memory" | VRAM too low | Use smaller model or resolution |
| "No module named 'comfy'" | Wrong directory | Must be in ComfyUI folder |
| "Connection refused" | ComfyUI not running | Start ComfyUI first |
| "No checkpoints found" | Missing models | Add models to checkpoints folder |

---

**Ready to create amazing AI art! 🎨**
