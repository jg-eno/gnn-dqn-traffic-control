#!/usr/bin/env python3
"""
Image processing script to remove white backgrounds from vehicle and road images.
"""

import os
from PIL import Image
import numpy as np


def remove_white_background(image_path, output_path, threshold=240):
    """
    Remove white background from an image and make it transparent.
    
    Args:
        image_path: Path to input image
        output_path: Path to save processed image
        threshold: White threshold (0-255, higher = more white removed)
    """
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array for processing
        data = np.array(img)
        
        # Create mask for white/light pixels
        # Check if all RGB channels are above threshold
        white_mask = (data[:, :, 0] > threshold) & \
                    (data[:, :, 1] > threshold) & \
                    (data[:, :, 2] > threshold)
        
        # Set alpha channel to 0 (transparent) for white pixels
        data[white_mask, 3] = 0
        
        # Convert back to PIL Image
        processed_img = Image.fromarray(data, 'RGBA')
        
        # Save the processed image
        processed_img.save(output_path, 'PNG')
        
        print(f"✅ Processed {image_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return False


def process_all_images():
    """Process all images in the Images directory."""
    input_dir = "Images"
    output_dir = "static/images"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # List of images to process
    images = ["Car.png", "Ambulance.png", "Road.png"]
    
    print("🖼️  Processing images to remove white backgrounds...")
    print("=" * 50)
    
    success_count = 0
    for image_name in images:
        input_path = os.path.join(input_dir, image_name)
        output_path = os.path.join(output_dir, image_name)
        
        if os.path.exists(input_path):
            if remove_white_background(input_path, output_path):
                success_count += 1
        else:
            print(f"⚠️  Image not found: {input_path}")
    
    print("=" * 50)
    print(f"🎉 Successfully processed {success_count}/{len(images)} images")
    
    if success_count == len(images):
        print("✅ All images processed successfully!")
        print("🚀 Ready to run the traffic simulator with transparent backgrounds")
    else:
        print("⚠️  Some images failed to process")


def main():
    """Main function."""
    print("🚦 Traffic Light Simulator - Image Processor")
    print("Removing white backgrounds from vehicle and road images")
    print()
    
    process_all_images()


if __name__ == "__main__":
    main()
