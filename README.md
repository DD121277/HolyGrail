# 🏆 HolyGrail

**Next-Generation ComfyUI Interface** - Brain-dead simple image and video generation

HolyGrail is a streamlined interface for ComfyUI that eliminates complexity while supporting Text-to-Image (T2I), Text-to-Video (T2V), Image-to-Video (I2V), and Video-to-Video (V2V) generation.

## ✨ Core Philosophy

- **Brain-dead simple**: Pick models, enter prompt, hit generate
- **Zero dimension thinking**: App automatically detects optimal image dimensions
- **One unified interface**: All generation types in a single, clean UI
- **Progressive disclosure**: Advanced options hidden until needed

## 🚀 Phase 1: Text-to-Image (T2I)

**Status**: ✅ Complete

### Features

- ✅ **Auto-dimension detection** - Automatically detects optimal resolution based on checkpoint type
  - SD 1.5: 512×512 (and variants)
  - SDXL: 1024×1024 (and variants)
  - Flux: 1024×1024 (and variants)
- ✅ **Model scanning** - Auto-discovers checkpoints and LoRAs from ComfyUI
- ✅ **Programmatic workflows** - No JSON templates, pure Python
- ✅ **Real-time progress** - Live generation status and progress bars
- ✅ **Clean, minimal UI** - Lots of whitespace, intuitive controls
- ✅ **Smart defaults** - Pre-configured for best results out of the box

## 📋 Requirements

- **Python 3.8+**
- **ComfyUI** (running at `http://127.0.0.1:8188`)
- Model checkpoints in ComfyUI's `models/checkpoints/` folder

## 🔧 Installation

### 1. Install ComfyUI

If you haven't already, install ComfyUI:

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### 2. Install HolyGrail

```bash
git clone <this-repo>
cd HolyGrail
pip install -r requirements.txt
```

### 3. Add Models

Place your model checkpoints in ComfyUI's model folders:
- Checkpoints: `ComfyUI/models/checkpoints/`
- LoRAs: `ComfyUI/models/loras/`

**Recommended models:**
- SD 1.5: [Realistic Vision](https://civitai.com/models/4201/realistic-vision-v20)
- SDXL: [Juggernaut XL](https://civitai.com/models/133005/juggernaut-xl)
- Flux: [Flux.1 Dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)

## 🎯 Usage

### Start ComfyUI

In one terminal:

```bash
cd ComfyUI
python main.py
```

Wait for ComfyUI to start (you should see "To see the GUI go to: http://127.0.0.1:8188")

### Start HolyGrail

In another terminal:

```bash
cd HolyGrail
streamlit run app.py
```

Your browser should automatically open to `http://localhost:8501`

### Generate Your First Image

1. **Select a checkpoint** - Choose your AI model
2. **Enter a prompt** - Describe what you want
3. **Click GENERATE** - That's it!

The app will:
- ✅ Auto-detect optimal dimensions for your model
- ✅ Build the ComfyUI workflow
- ✅ Show real-time progress
- ✅ Display the result with download button

### Advanced Options

Click "⚙️ Advanced Settings" to customize:
- **CFG Scale** (1-20, default 7) - How closely to follow the prompt
- **Steps** (1-50, default 20) - Quality vs speed tradeoff
- **Sampler** - Algorithm for generation (euler, euler_a, dpmpp_2m, etc.)
- **Resolution** - Override auto-detected dimensions
- **Seed** - Set specific seed for reproducibility (-1 for random)
- **LoRA** - Add style modifications
- **LoRA Strength** - Control LoRA influence (0-2)

## 🎨 Auto-Dimension Detection

HolyGrail automatically detects the optimal resolution based on your checkpoint:

| Model Type | Detected From | Default Resolution | Variants |
|------------|---------------|-------------------|----------|
| **SD 1.5** | Filename contains: `sd1.5`, `v1-5`, etc. | 512×512 | 512×768, 768×512, 512×704, 704×512 |
| **SDXL** | Filename contains: `sdxl`, `xl` | 1024×1024 | 1024×1536, 1536×1024, 1152×896, 896×1152 |
| **Flux** | Filename contains: `flux` | 1024×1024 | 1024×1536, 1536×1024, 768×1344, 1344×768 |

The detected resolution is shown above the LoRA selector. You can override it in Advanced Settings if needed.

## 🏗️ Architecture

### Components

**`ComfyUIClient`** - Handles all API communication
- Connection checking
- Model discovery
- Workflow submission
- Progress polling
- Image retrieval

**`DimensionDetector`** - Auto-detects optimal dimensions
- Pattern matching on checkpoint names
- Returns default + available resolutions
- Extensible for new model types

**`WorkflowBuilder`** - Programmatic workflow generation
- No JSON templates
- Type-safe Python dictionaries
- Supports LoRA injection
- Easy to extend for video modes

### Workflow Structure (T2I)

```
CheckpointLoader → CLIPTextEncode (positive)
                 → CLIPTextEncode (negative)
                 → EmptyLatentImage (auto-sized)
                 → KSampler
                 → VAEDecode
                 → SaveImage

Optional: LoraLoader (injected between checkpoint and samplers)
```

## 🐛 Troubleshooting

### "ComfyUI is not running"

**Solution**: Start ComfyUI first
```bash
cd ComfyUI
python main.py
```

### "No checkpoints found"

**Solution**: Add models to ComfyUI's checkpoint folder
```bash
# Place .safetensors or .ckpt files in:
ComfyUI/models/checkpoints/
```

Then click "🔄 Refresh Models" in HolyGrail

### Generation fails with error

**Common causes**:
1. **Out of VRAM** - Reduce resolution or use a smaller model
2. **Incompatible checkpoint** - Ensure checkpoint format is supported
3. **Missing dependencies** - Update ComfyUI to latest version

**Debug steps**:
1. Check ComfyUI terminal for error messages
2. Try the same settings in native ComfyUI interface
3. Reduce steps/resolution to test if it's a resource issue

### Images not displaying

**Solution**: Check ComfyUI output folder permissions
```bash
# Verify images are being saved
ls -la ComfyUI/output/
```

## 🗺️ Roadmap

### Phase 1: Text-to-Image ✅
- [x] Basic T2I workflow
- [x] Auto-dimension detection
- [x] Model scanning
- [x] LoRA support
- [x] Progress tracking
- [x] Image display and download

### Phase 2: Video Support 🚧
- [ ] Text-to-Video (T2V)
- [ ] Image-to-Video (I2V)
- [ ] Video-to-Video (V2V)
- [ ] Video model detection (SVD, AnimateDiff, etc.)
- [ ] Frame count and FPS controls
- [ ] Video preview and download

### Phase 3: Polish ✨
- [ ] Settings persistence (remember last used settings)
- [ ] Generation history (browse previous generations)
- [ ] Preset prompts/styles (one-click style templates)
- [ ] Batch generation
- [ ] Advanced prompt features (emphasis, scheduling)
- [ ] Image-to-Image mode
- [ ] Upscaling integration

## 🤝 Contributing

Contributions welcome! Focus areas:
- Video mode implementation (Phase 2)
- Additional model type detection
- UI/UX improvements
- Bug fixes and error handling

## 📝 Technical Notes

### Why Streamlit?

- **Rapid prototyping** - Get UI up in minutes
- **Built-in widgets** - Sliders, dropdowns, file uploads
- **Live reload** - Changes reflect immediately
- **Python-native** - No separate frontend build

Could be ported to Gradio, Flask, or FastAPI if needed.

### Why programmatic workflows?

- **Type safety** - Catch errors before submission
- **Maintainability** - Easy to modify and extend
- **No JSON debugging** - Pure Python logic
- **Dynamic injection** - Conditionally add nodes (e.g., LoRA)

### Performance optimizations

- **Async polling** - Non-blocking progress checks
- **Model caching** - Load model list once, refresh on demand
- **Lazy loading** - Only fetch what's needed when needed

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Credits

- **ComfyUI** - The powerful backend that makes this possible
- **Streamlit** - For the incredible web framework
- **Stability AI, Black Forest Labs** - For the amazing diffusion models

---

**Built with ❤️ for the AI art community**

*Making ComfyUI accessible to everyone, one phase at a time*
