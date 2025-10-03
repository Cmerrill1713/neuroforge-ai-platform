#!/usr/bin/env python3
""'
Simple AI model test script that works with available packages
""'

import os
import torch
from PIL import Image
import numpy as np

def test_basic_diffusion():
    """TODO: Add docstring."""
    """Test basic Stable Diffusion for image generation""'
    print("🎨 Testing Basic Stable Diffusion...')

    try:
        from diffusers import StableDiffusionPipeline

        print("Loading Stable Diffusion model...')
        # Use a smaller, more compatible model
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5',
            torch_dtype=torch.float32,
            use_safetensors=True
        )

        # Move to GPU if available
        if torch.cuda.is_available():
            pipe = pipe.to("cuda')
            print("✅ Model loaded on GPU')
        else:
            print("⚠️  GPU not available, using CPU')

        # Test image generation
        print("Generating test image...')
        prompt = "a beautiful sunset over mountains, digital art'

        with torch.inference_mode():
            image = pipe(
                prompt=prompt,
                num_inference_steps=20,  # Reduced for faster testing
                guidance_scale=7.5,
                generator=torch.manual_seed(42)
            ).images[0]

        # Save the result
        output_path = "test_output.png'
        image.save(output_path)
        print(f"✅ Image generated successfully! Saved to {output_path}')

        return True

    except Exception as e:
        print(f"❌ Error testing Stable Diffusion: {e}')
        return False

def test_image_editing():
    """TODO: Add docstring."""
    """Test image editing with Stable Diffusion""'
    print("🎨 Testing Image Editing...')

    try:
        from diffusers import StableDiffusionImg2ImgPipeline

        print("Loading image-to-image model...')
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5',
            torch_dtype=torch.float32,
            use_safetensors=True
        )

        if torch.cuda.is_available():
            pipe = pipe.to("cuda')

        # Create a simple test image
        test_image = Image.new("RGB", (512, 512), color="blue')
        test_image.save("test_input.png')

        print("Editing test image...')
        prompt = "a beautiful blue ocean with waves'

        with torch.inference_mode():
            edited_image = pipe(
                prompt=prompt,
                image=test_image,
                strength=0.8,
                num_inference_steps=20,
                guidance_scale=7.5,
                generator=torch.manual_seed(42)
            ).images[0]

        # Save the result
        output_path = "test_edited.png'
        edited_image.save(output_path)
        print(f"✅ Image editing successful! Saved to {output_path}')

        return True

    except Exception as e:
        print(f"❌ Error testing image editing: {e}')
        return False

def check_available_models():
    """TODO: Add docstring."""
    """Check what models are available""'
    print("🔍 Checking available models...')

    try:
        from huggingface_hub import list_models

        # List some popular models
        models = list_models(
            filter="stable-diffusion',
            limit=5
        )

        print("✅ Available Stable Diffusion models:')
        for model in models:
            print(f"   - {model.id}')

        return True

    except Exception as e:
        print(f"❌ Error checking models: {e}')
        return False

def main():
    """TODO: Add docstring."""
    """Main function""'
    print("🚀 Starting Simple AI Model Test')
    print("=' * 40)

    # Check system
    print(f"Python version: {torch.__version__}')
    print(f"CUDA available: {torch.cuda.is_available()}')
    print(f"Available RAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB" if torch.cuda.is_available() else "CPU only')
    print()

    # Test basic diffusion
    diffusion_success = test_basic_diffusion()
    print()

    # Test image editing
    editing_success = test_image_editing()
    print()

    # Check available models
    models_success = check_available_models()
    print()

    # Summary
    print("📊 Test Results:')
    print("=' * 20)
    print(f"Basic Diffusion: {"✅ Success" if diffusion_success else "❌ Failed"}')
    print(f"Image Editing: {"✅ Success" if editing_success else "❌ Failed"}')
    print(f"Model Check: {"✅ Success" if models_success else "❌ Failed"}')

    if diffusion_success or editing_success:
        print("\n🎉 AI models are working!')
        print("\n💡 For WAN 2.5 and Qwen Image Edit 2509:')
        print("   - These may require newer versions or different setup')
        print("   - Try the online platforms mentioned earlier')
        print("   - Or wait for better local support')
    else:
        print("\n⚠️  Models not working. Check dependencies.')

if __name__ == "__main__':
    main()
