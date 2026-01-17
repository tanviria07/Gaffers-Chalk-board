
import base64
from PIL import Image
import io
from typing import Optional


def compress_image(base64_image: str, max_size: int = 384, quality: int = 50) -> str:
    
    try:

        if "base64," in base64_image:
            base64_image = base64_image.split("base64,")[1]
        

        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        

        if image.mode in ('RGBA', 'LA', 'P'):

            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        

        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        

        compressed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return compressed_base64
        
    except Exception as e:
        print(f"Image compression error: {e}")

        if "base64," in base64_image:
            return base64_image.split("base64,")[1]
        return base64_image


def validate_image(base64_image: str) -> bool:
    
    try:
        if "base64," in base64_image:
            base64_image = base64_image.split("base64,")[1]
        
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        return True
    except Exception:
        return False
