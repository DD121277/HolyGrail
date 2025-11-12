"""
HolyGrail - Next-Generation ComfyUI Interface
Phase 1: Text-to-Image with Auto-Dimensions
"""

import streamlit as st
import requests
import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import io
from PIL import Image

# Configuration
COMFYUI_URL = "http://127.0.0.1:8188"
DEFAULT_COMFYUI_PATH = os.path.expanduser("~/ComfyUI")


class ComfyUIClient:
    """Client for interacting with ComfyUI API"""

    def __init__(self, base_url: str = COMFYUI_URL):
        self.base_url = base_url
        self.client_id = "holygrail"

    def is_available(self) -> bool:
        """Check if ComfyUI is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=2)
            return response.status_code == 200
        except:
            return False

    def get_models(self, model_type: str) -> List[str]:
        """Get list of models from ComfyUI

        Args:
            model_type: 'checkpoints', 'loras', 'vae', etc.
        """
        try:
            response = requests.get(f"{self.base_url}/object_info")
            if response.status_code == 200:
                object_info = response.json()

                # Different model types are in different loader nodes
                if model_type == "checkpoints":
                    if "CheckpointLoaderSimple" in object_info:
                        return object_info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
                elif model_type == "loras":
                    if "LoraLoader" in object_info:
                        return object_info["LoraLoader"]["input"]["required"]["lora_name"][0]

            return []
        except Exception as e:
            st.error(f"Error fetching {model_type}: {str(e)}")
            return []

    def queue_prompt(self, workflow: Dict) -> Optional[str]:
        """Submit a workflow to ComfyUI queue

        Returns:
            prompt_id if successful, None otherwise
        """
        try:
            payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("prompt_id")
            else:
                st.error(f"Failed to queue prompt: {response.status_code}")
                return None

        except Exception as e:
            st.error(f"Error queuing prompt: {str(e)}")
            return None

    def get_history(self, prompt_id: str) -> Optional[Dict]:
        """Get execution history for a prompt"""
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """Download generated image from ComfyUI"""
        try:
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }
            url = f"{self.base_url}/view?{urllib.parse.urlencode(params)}"
            response = requests.get(url)

            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            st.error(f"Error downloading image: {str(e)}")
            return None

    def poll_for_completion(self, prompt_id: str, progress_bar, status_text, max_wait: int = 300) -> Optional[Dict]:
        """Poll for workflow completion

        Args:
            prompt_id: The prompt ID to poll for
            progress_bar: Streamlit progress bar
            status_text: Streamlit text element for status updates
            max_wait: Maximum seconds to wait

        Returns:
            History dict if completed, None if timeout/error
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            history = self.get_history(prompt_id)

            if history and prompt_id in history:
                prompt_history = history[prompt_id]

                # Check if completed
                if "outputs" in prompt_history:
                    progress_bar.progress(1.0)
                    status_text.text("✓ Generation complete!")
                    return prompt_history

                # Check for errors
                if prompt_history.get("status", {}).get("status_str") == "error":
                    error_msg = prompt_history.get("status", {}).get("messages", ["Unknown error"])
                    status_text.error(f"Generation failed: {error_msg}")
                    return None

            # Update progress (simple animation)
            progress = (time.time() - start_time) / max_wait
            progress_bar.progress(min(progress, 0.99))
            status_text.text(f"⏳ Generating... ({int(time.time() - start_time)}s)")

            time.sleep(0.5)

        status_text.error("⏱️ Generation timeout")
        return None


class DimensionDetector:
    """Auto-detect optimal dimensions based on checkpoint type"""

    # Model patterns and their default dimensions
    MODEL_PATTERNS = {
        "sd15": {
            "patterns": ["sd1.5", "sd-1.5", "sd_1.5", "v1-5", "v1_5"],
            "dimensions": [(512, 512), (512, 768), (768, 512), (512, 704), (704, 512)],
            "default": (512, 512)
        },
        "sdxl": {
            "patterns": ["sdxl", "xl"],
            "dimensions": [(1024, 1024), (1024, 1536), (1536, 1024), (1152, 896), (896, 1152)],
            "default": (1024, 1024)
        },
        "flux": {
            "patterns": ["flux"],
            "dimensions": [(1024, 1024), (1024, 1536), (1536, 1024), (768, 1344), (1344, 768)],
            "default": (1024, 1024)
        }
    }

    @classmethod
    def detect_model_type(cls, checkpoint_name: str) -> str:
        """Detect model type from checkpoint filename"""
        checkpoint_lower = checkpoint_name.lower()

        # Check patterns in order of specificity
        for model_type, config in cls.MODEL_PATTERNS.items():
            for pattern in config["patterns"]:
                if pattern in checkpoint_lower:
                    return model_type

        # Default to SD 1.5 if unknown
        return "sd15"

    @classmethod
    def get_dimensions(cls, checkpoint_name: str) -> Tuple[Tuple[int, int], List[Tuple[int, int]]]:
        """Get default dimension and available options for a checkpoint

        Returns:
            (default_dimension, available_dimensions)
        """
        model_type = cls.detect_model_type(checkpoint_name)
        config = cls.MODEL_PATTERNS[model_type]
        return config["default"], config["dimensions"]


class WorkflowBuilder:
    """Build ComfyUI workflows programmatically"""

    @staticmethod
    def build_t2i_workflow(
        checkpoint: str,
        positive_prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        cfg: float,
        steps: int,
        sampler: str,
        scheduler: str = "normal",
        seed: int = -1,
        lora: Optional[str] = None,
        lora_strength: float = 1.0
    ) -> Dict:
        """Build a Text-to-Image workflow

        Returns a ComfyUI workflow dictionary
        """
        # Generate random seed if needed
        if seed == -1:
            import random
            seed = random.randint(0, 2**32 - 1)

        workflow = {
            # Checkpoint Loader
            "1": {
                "inputs": {
                    "ckpt_name": checkpoint
                },
                "class_type": "CheckpointLoaderSimple"
            },
            # Positive Prompt
            "2": {
                "inputs": {
                    "text": positive_prompt,
                    "clip": ["1", 1]  # CLIP from checkpoint
                },
                "class_type": "CLIPTextEncode"
            },
            # Negative Prompt
            "3": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1]  # CLIP from checkpoint
                },
                "class_type": "CLIPTextEncode"
            },
            # Empty Latent Image
            "4": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            # KSampler
            "5": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler,
                    "scheduler": scheduler,
                    "denoise": 1.0,
                    "model": ["1", 0],  # Model from checkpoint
                    "positive": ["2", 0],  # Positive conditioning
                    "negative": ["3", 0],  # Negative conditioning
                    "latent_image": ["4", 0]  # Empty latent
                },
                "class_type": "KSampler"
            },
            # VAE Decode
            "6": {
                "inputs": {
                    "samples": ["5", 0],  # Latent from sampler
                    "vae": ["1", 2]  # VAE from checkpoint
                },
                "class_type": "VAEDecode"
            },
            # Save Image
            "7": {
                "inputs": {
                    "filename_prefix": "HolyGrail_T2I",
                    "images": ["6", 0]  # Decoded image
                },
                "class_type": "SaveImage"
            }
        }

        # Add LoRA if specified
        if lora and lora != "None":
            # Insert LoRA loader
            workflow["8"] = {
                "inputs": {
                    "lora_name": lora,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["1", 0],
                    "clip": ["1", 1]
                },
                "class_type": "LoraLoader"
            }

            # Update references to use LoRA output
            workflow["2"]["inputs"]["clip"] = ["8", 1]  # CLIP from LoRA
            workflow["3"]["inputs"]["clip"] = ["8", 1]  # CLIP from LoRA
            workflow["5"]["inputs"]["model"] = ["8", 0]  # Model from LoRA

        return workflow


def init_session_state():
    """Initialize Streamlit session state"""
    if "client" not in st.session_state:
        st.session_state.client = ComfyUIClient()

    if "checkpoints" not in st.session_state:
        st.session_state.checkpoints = []

    if "loras" not in st.session_state:
        st.session_state.loras = ["None"]

    if "models_loaded" not in st.session_state:
        st.session_state.models_loaded = False


def load_models():
    """Load available models from ComfyUI"""
    with st.spinner("🔍 Scanning models..."):
        st.session_state.checkpoints = st.session_state.client.get_models("checkpoints")
        loras = st.session_state.client.get_models("loras")
        st.session_state.loras = ["None"] + loras
        st.session_state.models_loaded = True


def main():
    st.set_page_config(
        page_title="HolyGrail - ComfyUI Interface",
        page_icon="🏆",
        layout="wide"
    )

    # Custom CSS for clean, minimal design
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            height: 3em;
            font-size: 1.2em;
            font-weight: bold;
        }
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted black;
        }
        h1 {
            margin-bottom: 2rem;
        }
        .dimensions-info {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🏆 HolyGrail")
    st.markdown("*Next-generation ComfyUI interface - Brain-dead simple image generation*")

    # Initialize
    init_session_state()

    # Check ComfyUI connection
    if not st.session_state.client.is_available():
        st.error("❌ **ComfyUI is not running!**")
        st.info(f"👉 Please start ComfyUI at {COMFYUI_URL}")
        st.markdown("""
        **Quick start:**
        1. Navigate to your ComfyUI folder
        2. Run: `python main.py`
        3. Refresh this page
        """)
        st.stop()

    st.success("✓ Connected to ComfyUI")

    # Load models button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Models"):
            load_models()
            st.success("Models refreshed!")

    # Auto-load models on first run
    if not st.session_state.models_loaded:
        load_models()

    # Check if models are available
    if not st.session_state.checkpoints:
        st.warning("⚠️ No checkpoints found!")
        st.info("Please add model checkpoints to your ComfyUI models/checkpoints/ folder")
        st.stop()

    st.markdown("---")

    # Mode selector (Phase 1: T2I only)
    st.subheader("📋 Generation Mode")
    mode = st.radio(
        "Select generation type:",
        ["Text → Image (T2I)"],
        help="More modes (T2V, I2V, V2V) coming in Phase 2!"
    )

    st.markdown("---")

    # UNIVERSAL INPUTS
    st.subheader("🎨 Model & Prompts")

    # Checkpoint selection
    checkpoint = st.selectbox(
        "Checkpoint",
        st.session_state.checkpoints,
        help="Select your AI model checkpoint"
    )

    # Auto-detect dimensions
    default_dim, available_dims = DimensionDetector.get_dimensions(checkpoint)
    model_type = DimensionDetector.detect_model_type(checkpoint)

    # Show detected model info
    st.markdown(f"""
    <div class="dimensions-info">
        <strong>📐 Detected Model:</strong> {model_type.upper()}<br>
        <strong>🎯 Optimal Resolution:</strong> {default_dim[0]}×{default_dim[1]}
    </div>
    """, unsafe_allow_html=True)

    # LoRA selection
    lora = st.selectbox(
        "LoRA (Optional)",
        st.session_state.loras,
        help="Select a LoRA to modify the style/content"
    )

    if lora != "None":
        lora_strength = st.slider(
            "LoRA Strength",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="How strongly to apply the LoRA"
        )
    else:
        lora_strength = 1.0

    # Prompts
    positive_prompt = st.text_area(
        "Positive Prompt",
        height=100,
        placeholder="Describe what you want to generate...",
        help="Describe the image you want to create"
    )

    negative_prompt = st.text_area(
        "Negative Prompt",
        height=80,
        value="ugly, blurry, low quality, distorted",
        help="Describe what you want to avoid"
    )

    st.markdown("---")

    # ADVANCED SETTINGS
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)

        with col1:
            cfg = st.slider(
                "CFG Scale",
                min_value=1.0,
                max_value=20.0,
                value=7.0,
                step=0.5,
                help="How closely to follow the prompt (higher = stricter)"
            )

            steps = st.slider(
                "Steps",
                min_value=1,
                max_value=50,
                value=20,
                help="Number of denoising steps (higher = better quality, slower)"
            )

            sampler = st.selectbox(
                "Sampler",
                ["euler", "euler_a", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_3m_sde"],
                index=2,
                help="Sampling algorithm to use"
            )

        with col2:
            # Dimension override
            dim_options = [f"{w}×{h}" for w, h in available_dims]
            default_idx = available_dims.index(default_dim)

            selected_dim = st.selectbox(
                "Resolution",
                dim_options,
                index=default_idx,
                help="Image dimensions (auto-detected based on model)"
            )

            # Parse selected dimension
            width, height = map(int, selected_dim.split("×"))

            seed = st.number_input(
                "Seed",
                min_value=-1,
                max_value=2**32 - 1,
                value=-1,
                help="Random seed (-1 for random)"
            )

    st.markdown("---")

    # GENERATE BUTTON
    if not positive_prompt.strip():
        st.warning("⚠️ Please enter a positive prompt")
    else:
        if st.button("🚀 GENERATE", type="primary"):
            # Build workflow
            with st.spinner("🔨 Building workflow..."):
                workflow = WorkflowBuilder.build_t2i_workflow(
                    checkpoint=checkpoint,
                    positive_prompt=positive_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    cfg=cfg,
                    steps=steps,
                    sampler=sampler,
                    seed=int(seed),
                    lora=lora if lora != "None" else None,
                    lora_strength=lora_strength
                )

            # Queue prompt
            prompt_id = st.session_state.client.queue_prompt(workflow)

            if prompt_id:
                st.info(f"✓ Queued with ID: {prompt_id}")

                # Poll for completion
                progress_bar = st.progress(0)
                status_text = st.empty()

                result = st.session_state.client.poll_for_completion(
                    prompt_id,
                    progress_bar,
                    status_text
                )

                if result and "outputs" in result:
                    # Find the SaveImage node output
                    for node_id, node_output in result["outputs"].items():
                        if "images" in node_output:
                            images = node_output["images"]

                            for img_info in images:
                                filename = img_info["filename"]
                                subfolder = img_info.get("subfolder", "")

                                # Download image
                                image_data = st.session_state.client.get_image(
                                    filename,
                                    subfolder
                                )

                                if image_data:
                                    # Display image
                                    st.markdown("---")
                                    st.subheader("✨ Generated Image")

                                    image = Image.open(io.BytesIO(image_data))
                                    st.image(image, use_container_width=True)

                                    # Download button
                                    st.download_button(
                                        label="⬇️ Download Image",
                                        data=image_data,
                                        file_name=filename,
                                        mime="image/png"
                                    )

                                    # Show generation parameters
                                    with st.expander("📊 Generation Parameters"):
                                        st.json({
                                            "checkpoint": checkpoint,
                                            "lora": lora,
                                            "resolution": f"{width}×{height}",
                                            "cfg_scale": cfg,
                                            "steps": steps,
                                            "sampler": sampler,
                                            "seed": seed if seed != -1 else "random",
                                            "positive_prompt": positive_prompt,
                                            "negative_prompt": negative_prompt
                                        })

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <strong>HolyGrail</strong> - Phase 1: Text-to-Image<br>
        <em>Coming soon: T2V, I2V, V2V support</em>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
