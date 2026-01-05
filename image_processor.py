"""
IMAGE PROCESSOR FOR OCR
Using only PIL (Pillow) - No OpenCV required
Compatible with Python 3.14+
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np
from typing import Tuple, Optional, List
import os

class ImageProcessor:
    """Image preprocessing for OCR without OpenCV"""
    
    def __init__(self):
        self.processing_steps = []
        self.debug_mode = False
    
    def enable_debug(self, enable: bool = True):
        """Enable/disable debug messages"""
        self.debug_mode = enable
    
    def log(self, message: str):
        """Log processing steps"""
        self.processing_steps.append(message)
        if self.debug_mode:
            print(f"[PROCESS] {message}")
    
    def load_image(self, image_path: str) -> Image.Image:
        """Load image from file path"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            img = Image.open(image_path)
            self.log(f"Loaded image: {os.path.basename(image_path)}")
            self.log(f"  Size: {img.size}, Mode: {img.mode}, Format: {img.format}")
            return img
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    def convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert image to grayscale"""
        if image.mode != 'L':
            gray = image.convert('L')
            self.log("Converted to grayscale")
            return gray
        return image
    
    def adjust_brightness_contrast(self, image: Image.Image, 
                                  brightness: float = 1.0, 
                                  contrast: float = 1.5) -> Image.Image:
        """Adjust brightness and contrast"""
        # Brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
            self.log(f"Adjusted brightness: {brightness}")
        
        # Contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
            self.log(f"Adjusted contrast: {contrast}")
        
        return image
    
    def apply_threshold(self, image: Image.Image, 
                       threshold: int = 150) -> Image.Image:
        """Apply binary thresholding"""
        # Method 1: Simple threshold
        binary = image.point(lambda x: 0 if x < threshold else 255, '1')
        
        # Convert back to 'L' for consistency
        binary = binary.convert('L')
        self.log(f"Applied threshold: {threshold}")
        return binary
    
    def remove_noise(self, image: Image.Image, 
                    method: str = 'median', 
                    size: int = 3) -> Image.Image:
        """Remove noise from image"""
        if method == 'median':
            denoised = image.filter(ImageFilter.MedianFilter(size=size))
            self.log(f"Applied median filter (size={size})")
        elif method == 'gaussian':
            denoised = image.filter(ImageFilter.GaussianBlur(radius=size//2))
            self.log(f"Applied gaussian blur (radius={size//2})")
        elif method == 'min':
            denoised = image.filter(ImageFilter.MinFilter(size=size))
            self.log(f"Applied min filter (size={size})")
        elif method == 'max':
            denoised = image.filter(ImageFilter.MaxFilter(size=size))
            self.log(f"Applied max filter (size={size})")
        else:
            denoised = image
        
        return denoised
    
    def sharpen_image(self, image: Image.Image, 
                     strength: float = 1.5) -> Image.Image:
        """Sharpen image"""
        enhancer = ImageEnhance.Sharpness(image)
        sharpened = enhancer.enhance(strength)
        self.log(f"Sharpened image (strength={strength})")
        return sharpened
    
    def deskew_image(self, image: Image.Image) -> Image.Image:
        """Simple deskew using autocontrast"""
        try:
            # Auto contrast can help with some skew
            deskewed = ImageOps.autocontrast(image, cutoff=2)
            self.log("Applied auto-contrast for deskewing")
            return deskewed
        except:
            self.log("Deskewing not applied")
            return image
    
    def resize_image(self, image: Image.Image, 
                    scale_factor: float = None,
                    max_size: Tuple[int, int] = None) -> Image.Image:
        """Resize image for better OCR"""
        original_size = image.size
        
        if scale_factor and 0 < scale_factor != 1.0:
            new_size = (int(original_size[0] * scale_factor), 
                       int(original_size[1] * scale_factor))
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            self.log(f"Resized: {original_size} -> {new_size} (scale={scale_factor})")
            return resized
        
        elif max_size:
            # Maintain aspect ratio
            ratio = min(max_size[0]/original_size[0], max_size[1]/original_size[1])
            if ratio < 1:
                new_size = (int(original_size[0] * ratio), 
                           int(original_size[1] * ratio))
                resized = image.resize(new_size, Image.Resampling.LANCZOS)
                self.log(f"Resized to max {max_size}: {original_size} -> {new_size}")
                return resized
        
        return image
    
    def full_preprocessing_pipeline(self, image_path: str, 
                                   output_path: Optional[str] = None,
                                   show_steps: bool = False) -> Image.Image:
        """
        Complete preprocessing pipeline for OCR
        
        Args:
            image_path: Path to input image
            output_path: Path to save processed image (optional)
            show_steps: Show intermediate steps (requires matplotlib)
        
        Returns:
            Processed PIL Image
        """
        # Reset steps
        self.processing_steps = []
        
        self.log("=" * 50)
        self.log("STARTING OCR PREPROCESSING PIPELINE")
        self.log("=" * 50)
        
        # 1. Load image
        original = self.load_image(image_path)
        
        # Store intermediate steps for display
        intermediate_images = [("Original", original)]
        
        # 2. Convert to grayscale
        gray = self.convert_to_grayscale(original)
        intermediate_images.append(("Grayscale", gray))
        
        # 3. Resize if too large (better for OCR)
        if max(gray.size) > 2000:
            resized = self.resize_image(gray, max_size=(1500, 1500))
            intermediate_images.append(("Resized", resized))
        else:
            resized = gray
        
        # 4. Enhance contrast and brightness
        enhanced = self.adjust_brightness_contrast(resized, 
                                                  brightness=1.1, 
                                                  contrast=1.8)
        intermediate_images.append(("Enhanced", enhanced))
        
        # 5. Remove noise
        denoised = self.remove_noise(enhanced, method='median', size=3)
        intermediate_images.append(("Denoised", denoised))
        
        # 6. Sharpen slightly
        sharpened = self.sharpen_image(denoised, strength=1.3)
        intermediate_images.append(("Sharpened", sharpened))
        
        # 7. Apply threshold
        thresholded = self.apply_threshold(sharpened, threshold=160)
        intermediate_images.append(("Thresholded", thresholded))
        
        # 8. Final deskew
        final = self.deskew_image(thresholded)
        intermediate_images.append(("Final", final))
        
        # Save if output path provided
        if output_path:
            final.save(output_path)
            self.log(f"Saved processed image to: {output_path}")
        
        # Show steps if requested
        if show_steps and len(intermediate_images) > 1:
            self._display_processing_steps(intermediate_images)
        
        self.log("=" * 50)
        self.log(f"PREPROCESSING COMPLETE ({len(self.processing_steps)} steps)")
        self.log("=" * 50)
        
        return final
    
    def _display_processing_steps(self, images: List[Tuple[str, Image.Image]]):
        """Display processing steps (requires matplotlib)"""
        try:
            import matplotlib.pyplot as plt
            
            n_steps = len(images)
            cols = min(3, n_steps)
            rows = (n_steps + cols - 1) // cols
            
            fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
            if rows == 1 and cols == 1:
                axes = [[axes]]
            elif rows == 1:
                axes = [axes]
            elif cols == 1:
                axes = [[ax] for ax in axes]
            
            for idx, (title, img) in enumerate(images):
                row = idx // cols
                col = idx % cols
                
                ax = axes[row][col]
                ax.imshow(img, cmap='gray' if img.mode == 'L' else None)
                ax.set_title(title)
                ax.axis('off')
            
            # Hide empty subplots
            for idx in range(len(images), rows*cols):
                row = idx // cols
                col = idx % cols
                axes[row][col].axis('off')
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            self.log("Matplotlib not available for visualization")
        except Exception as e:
            self.log(f"Failed to display steps: {str(e)}")
    
    def get_processing_report(self) -> str:
        """Get a report of all processing steps"""
        report = "IMAGE PROCESSING REPORT\n"
        report += "=" * 50 + "\n"
        for i, step in enumerate(self.processing_steps, 1):
            report += f"{i:2d}. {step}\n"
        report += "=" * 50
        return report

# ===== USAGE EXAMPLES =====
if __name__ == "__main__":
    print("Testing Image Processor (No OpenCV)")
    
    # Create a simple test image
    test_img = Image.new('RGB', (400, 200), color='white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_img)
    draw.rectangle([50, 50, 350, 80], fill='black')  # Simulate text line 1
    draw.rectangle([50, 100, 350, 130], fill='black')  # Simulate text line 2
    
    # Save test image
    test_img.save("test_image.png")
    
    # Test processor
    processor = ImageProcessor()
    processor.enable_debug(True)
    
    # Process the test image
    processed = processor.full_preprocessing_pipeline(
        "test_image.png", 
        "test_processed.png",
        show_steps=False  # Set to True if matplotlib installed
    )
    
    print("\n" + processor.get_processing_report())
    print(f"\n✅ Original size: {test_img.size}")
    print(f"✅ Processed size: {processed.size}")
    
    # Clean up
    import os
    if os.path.exists("test_image.png"):
        os.remove("test_image.png")
    if os.path.exists("test_processed.png"):
        os.remove("test_processed.png")