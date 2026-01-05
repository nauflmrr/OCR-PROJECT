"""
TESTING SCRIPT FOR OCR APPLICATION
Run this to verify everything works
"""

import os
import sys
from PIL import Image, ImageDraw

def test_all():
    """Run all tests"""
    print("🧪 OCR APPLICATION TEST SUITE")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check Python version
    print("\n1. Testing Python version...")
    try:
        version = sys.version_info
        print(f"   Python {version.major}.{version.minor}.{version.micro}")
        if version.major == 3 and version.minor >= 7:
            print("   ✅ Python version OK")
            tests_passed += 1
        else:
            print("   ⚠ Python version might have compatibility issues")
            tests_passed += 1
    except:
        print("   ❌ Cannot determine Python version")
        tests_failed += 1
    
    # Test 2: Check required modules
    print("\n2. Testing required modules...")
    modules = ['pytesseract', 'PIL', 'tkinter']
    
    for module in modules:
        try:
            if module == 'PIL':
                import PIL
                print(f"   ✅ {module} (Pillow) installed")
            elif module == 'tkinter':
                import tkinter
                print(f"   ✅ {module} installed")
            else:
                __import__(module)
                print(f"   ✅ {module} installed")
            tests_passed += 1
        except ImportError:
            print(f"   ❌ {module} not installed")
            tests_failed += 1
    
    # Test 3: Create test image
    print("\n3. Creating test image...")
    try:
        test_img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([50, 50, 350, 80], fill='black')
        draw.rectangle([50, 120, 350, 150], fill='black')
        
        if not os.path.exists('test_data'):
            os.makedirs('test_data')
        
        test_img.save('test_data/test_image.png')
        print("   ✅ Test image created: test_data/test_image.png")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Cannot create test image: {e}")
        tests_failed += 1
    
    # Test 4: Test image processor
    print("\n4. Testing image processor...")
    try:
        from image_processor import ImageProcessor
        processor = ImageProcessor()
        processor.enable_debug(False)
        
        # Create a simple image for testing
        img = Image.new('RGB', (100, 100), color='white')
        img_array = processor.preprocess_image(img)
        
        print(f"   ✅ ImageProcessor initialized")
        print(f"   ✅ Image processed: shape {img_array.shape}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ ImageProcessor test failed: {e}")
        tests_failed += 1
    
    # Test 5: Test OCR engine
    print("\n5. Testing OCR engine...")
    try:
        from ocr_engine import OCREngine
        ocr = OCREngine()
        print(f"   ✅ OCREngine initialized")
        
        # Test with simple image
        test_img = Image.new('RGB', (300, 100), color='white')
        result = ocr.extract_text(test_img, 'english')
        
        if isinstance(result, dict):
            print(f"   ✅ OCR test completed")
            tests_passed += 1
        else:
            print(f"   ❌ OCR returned unexpected result")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ OCREngine test failed: {e}")
        tests_failed += 1
    
    # Test 6: Test Tesseract installation
    print("\n6. Testing Tesseract installation...")
    try:
        import pytesseract
        import subprocess
        
        cmd = [pytesseract.pytesseract.tesseract_cmd, '--version']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"   ✅ Tesseract found: {version}")
            tests_passed += 1
        else:
            print(f"   ❌ Tesseract check failed")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Tesseract test failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! Application is ready to use.")
        print("\nNext steps:")
        print("1. Run GUI: python main.py")
        print("2. Run CLI: python cli_app.py --help")
        print("3. Add your own images to 'test_data/' folder")
    else:
        print(f"\n⚠ {tests_failed} test(s) failed. Check above for errors.")
    
    # Cleanup
    if os.path.exists('test_data/test_image.png'):
        os.remove('test_data/test_image.png')
        if not os.listdir('test_data'):
            os.rmdir('test_data')
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)