"""
Image processing utilities for frame compression and optimization
"""
import base64
from PIL import Image
import io
from typing import Optional


def compress_image(base64_image: str, max_size: int = 384, quality: int = 50) -> str:
    """
    Compress base64 image to reduce API costs and improve performance
    
    Args:
        base64_image: Base64 encoded image string (with or without data URL prefix)
        max_size: Maximum width/height in pixels
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed base64 image string
    """
    try:
        # Remove data URL prefix if present
        if "base64," in base64_image:
            base64_image = base64_image.split("base64,")[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to max_size x max_size (maintains aspect ratio)
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Compress to JPEG
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        
        # Encode back to base64
        compressed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return compressed_base64
        
    except Exception as e:
        print(f"Image compression error: {e}")
        # Return original if compression fails
        if "base64," in base64_image:
            return base64_image.split("base64,")[1]
        return base64_image


def validate_image(base64_image: str) -> bool:
    """
    Validate that the base64 string is a valid image
    
    Args:
        base64_image: Base64 encoded image string
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if "base64," in base64_image:
            base64_image = base64_image.split("base64,")[1]
        
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        return True
    except Exception:
        return False
