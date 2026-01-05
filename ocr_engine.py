"""
OCR ENGINE USING TESSERACT
With multilingual support and text cleaning
"""

import pytesseract
from PIL import Image
import re
import os
from typing import Dict, List, Tuple, Optional, Any
import json

class OCREngine:
    """OCR Engine with Tesseract"""
    
    # Language mapping
    LANGUAGE_MAP = {
        'indonesian': 'ind',
        'english': 'eng',
        'french': 'fra',
        'spanish': 'spa',
        'german': 'deu',
        'chinese': 'chi_sim',
        'japanese': 'jpn',
        'korean': 'kor',
        'arabic': 'ara',
        'ind+eng': 'ind+eng',
        'eng+ind': 'eng+ind',
    }
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize OCR Engine
        
        Args:
            tesseract_path: Path to tesseract.exe (auto-detected if None)
        """
        self.tesseract_path = tesseract_path
        self._configure_tesseract()
        self.ocr_results = []
        self.performance_stats = {
            'total_images': 0,
            'successful': 0,
            'failed': 0,
            'total_chars': 0
        }
    
    def _configure_tesseract(self):
        """Configure Tesseract path"""
        if self.tesseract_path and os.path.exists(self.tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        else:
            # Auto-detect for Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(
                    os.getlogin()
                ),
                '/usr/local/bin/tesseract',  # Mac
                '/usr/bin/tesseract',        # Linux
            ]
            
            for path in possible_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    pytesseract.pytesseract.tesseract_cmd = expanded_path
                    self.tesseract_path = expanded_path
                    print(f"✅ Tesseract found at: {expanded_path}")
                    break
            else:
                print("⚠️ Tesseract not found in common locations")
                print("   Please set tesseract_path manually")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        try:
            import subprocess
            cmd = [pytesseract.pytesseract.tesseract_cmd, '--list-langs']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse output (first line is "Languages:")
                lines = result.stdout.strip().split('\n')[1:]
                return [lang.strip() for lang in lines if lang.strip()]
            return []
        except:
            return list(self.LANGUAGE_MAP.keys())
    
    def extract_text(self, image: Image.Image, 
                    language: str = 'indonesian',
                    config: str = '--oem 3 --psm 6',
                    timeout: int = 30) -> Dict[str, Any]:
        """
        Extract text from image
        
        Args:
            image: PIL Image object
            language: Language code or name
            config: Tesseract configuration
            timeout: Timeout in seconds
        
        Returns:
            Dictionary with results
        """
        try:
            # Convert language name to code
            lang_code = self.LANGUAGE_MAP.get(language.lower(), language)
            
            # Ensure image is in correct mode
            if image.mode not in ['L', 'RGB', 'RGBA']:
                image = image.convert('RGB')
            
            # Extract text with Tesseract
            text = pytesseract.image_to_string(
                image, 
                lang=lang_code,
                config=config,
                timeout=timeout
            )
            
            # Get additional data
            data = pytesseract.image_to_data(
                image,
                lang=lang_code,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate confidence
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Clean text
            cleaned_text = self._clean_text(text)
            
            result = {
                'success': True,
                'text': cleaned_text,
                'raw_text': text,
                'language': language,
                'language_code': lang_code,
                'confidence': avg_confidence,
                'word_count': len(cleaned_text.split()),
                'char_count': len(cleaned_text),
                'image_size': image.size,
                'config': config,
                'word_boxes': self._extract_word_boxes(data),
                'error': None
            }
            
            # Update stats
            self.performance_stats['total_images'] += 1
            self.performance_stats['successful'] += 1
            self.performance_stats['total_chars'] += len(cleaned_text)
            
            # Store result
            self.ocr_results.append(result)
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'text': '',
                'raw_text': '',
                'language': language,
                'confidence': 0,
                'word_count': 0,
                'char_count': 0,
                'error': str(e),
                'image_size': image.size if 'image' in locals() else (0, 0)
            }
            
            self.performance_stats['total_images'] += 1
            self.performance_stats['failed'] += 1
            self.ocr_results.append(error_result)
            
            return error_result
    
    def _extract_word_boxes(self, data: Dict) -> List[Dict]:
        """Extract word bounding boxes"""
        words = []
        n_boxes = len(data['level'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0 and data['text'][i].strip():
                words.append({
                    'text': data['text'][i],
                    'confidence': int(data['conf'][i]),
                    'bbox': (
                        data['left'][i],
                        data['top'][i],
                        data['left'][i] + data['width'][i],
                        data['top'][i] + data['height'][i]
                    ),
                    'line_num': data['line_num'][i],
                    'block_num': data['block_num'][i]
                })
        
        return words
    
    def _clean_text(self, text: str) -> str:
        """Clean and format OCR text"""
        if not text:
            return ""
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,!?;:\-\'\"\n()\[\]{}]', '', text)
        
        # Fix multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Fix multiple newlines
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        # Trim each line
        cleaned = '\n'.join([line.strip() for line in cleaned.split('\n')])
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def batch_process(self, image_paths: List[str], 
                     language: str = 'indonesian',
                     save_results: bool = True,
                     output_dir: str = 'ocr_results') -> List[Dict]:
        """
        Process multiple images
        
        Args:
            image_paths: List of image paths
            language: OCR language
            save_results: Save results to files
            output_dir: Output directory for results
        
        Returns:
            List of OCR results
        """
        results = []
        
        if save_results and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for i, image_path in enumerate(image_paths):
            print(f"Processing {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            try:
                # Load image
                image = Image.open(image_path)
                
                # Process
                result = self.extract_text(image, language)
                result['filename'] = os.path.basename(image_path)
                result['filepath'] = image_path
                
                results.append(result)
                
                # Save individual result
                if save_results:
                    self._save_single_result(result, output_dir)
                
                # Print preview
                if result['success']:
                    preview = result['text'][:100].replace('\n', ' ')
                    print(f"  ✅ {preview}...")
                    print(f"  Confidence: {result['confidence']:.1f}%")
                else:
                    print(f"  ❌ Error: {result['error']}")
                    
            except Exception as e:
                error_result = {
                    'success': False,
                    'filename': os.path.basename(image_path),
                    'error': str(e),
                    'text': ''
                }
                results.append(error_result)
                print(f"  ❌ Failed: {str(e)}")
        
        # Save batch report
        if save_results:
            self._save_batch_report(results, output_dir)
        
        return results
    
    def _save_single_result(self, result: Dict, output_dir: str):
        """Save single OCR result"""
        if not result['success']:
            return
        
        base_name = os.path.splitext(result['filename'])[0]
        
        # Save text
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        # Save JSON with metadata
        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            # Remove image object if present
            result_copy = result.copy()
            if 'image' in result_copy:
                del result_copy['image']
            json.dump(result_copy, f, indent=2, ensure_ascii=False)
    
    def _save_batch_report(self, results: List[Dict], output_dir: str):
        """Save batch processing report"""
        report_path = os.path.join(output_dir, "batch_report.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("OCR BATCH PROCESSING REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            f.write(f"SUMMARY:\n")
            f.write(f"  Total files: {len(results)}\n")
            f.write(f"  Successful: {len(successful)}\n")
            f.write(f"  Failed: {len(failed)}\n")
            
            if successful:
                avg_conf = sum(r['confidence'] for r in successful) / len(successful)
                total_chars = sum(r['char_count'] for r in successful)
                f.write(f"  Average confidence: {avg_conf:.1f}%\n")
                f.write(f"  Total characters: {total_chars}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("DETAILED RESULTS:\n")
            f.write("=" * 60 + "\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"File {i}: {result.get('filename', 'N/A')}\n")
                f.write(f"  Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}\n")
                
                if result['success']:
                    f.write(f"  Confidence: {result['confidence']:.1f}%\n")
                    f.write(f"  Characters: {result['char_count']}\n")
                    f.write(f"  Words: {result['word_count']}\n")
                    preview = result['text'][:200].replace('\n', ' ')
                    f.write(f"  Preview: {preview}...\n")
                else:
                    f.write(f"  Error: {result.get('error', 'Unknown error')}\n")
                
                f.write("\n")
    
    def get_performance_report(self) -> str:
        """Get performance statistics"""
        report = "OCR PERFORMANCE REPORT\n"
        report += "=" * 50 + "\n"
        report += f"Total images processed: {self.performance_stats['total_images']}\n"
        report += f"Successful: {self.performance_stats['successful']}\n"
        report += f"Failed: {self.performance_stats['failed']}\n"
        
        if self.performance_stats['successful'] > 0:
            success_rate = (self.performance_stats['successful'] / 
                          self.performance_stats['total_images'] * 100)
            report += f"Success rate: {success_rate:.1f}%\n"
            report += f"Total characters: {self.performance_stats['total_chars']}\n"
            
            # Calculate average confidence
            confidences = [r['confidence'] for r in self.ocr_results if r['success']]
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                report += f"Average confidence: {avg_conf:.1f}%\n"
        
        report += "=" * 50
        return report
    
    def export_results(self, format: str = 'txt', 
                      output_file: str = 'ocr_export') -> str:
        """
        Export OCR results
        
        Args:
            format: Export format (txt, json, csv)
            output_file: Output file path (without extension)
        
        Returns:
            Path to exported file
        """
        if not self.ocr_results:
            return "No results to export"
        
        if format == 'json':
            file_path = f"{output_file}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                # Remove PIL images if present
                export_data = []
                for result in self.ocr_results:
                    result_copy = result.copy()
                    if 'image' in result_copy:
                        del result_copy['image']
                    export_data.append(result_copy)
                
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            file_path = f"{output_file}.csv"
            import csv
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Filename', 'Success', 'Language', 
                               'Confidence', 'Characters', 'Words', 'Text_Preview'])
                
                for result in self.ocr_results:
                    preview = result.get('text', '')[:100].replace('\n', ' ')
                    writer.writerow([
                        result.get('filename', 'N/A'),
                        result.get('success', False),
                        result.get('language', 'N/A'),
                        f"{result.get('confidence', 0):.1f}",
                        result.get('char_count', 0),
                        result.get('word_count', 0),
                        preview
                    ])
        
        else:  # txt format (default)
            file_path = f"{output_file}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                for result in self.ocr_results:
                    f.write("=" * 60 + "\n")
                    f.write(f"File: {result.get('filename', 'N/A')}\n")
                    f.write(f"Success: {result.get('success', False)}\n")
                    
                    if result.get('success'):
                        f.write(f"Language: {result.get('language', 'N/A')}\n")
                        f.write(f"Confidence: {result.get('confidence', 0):.1f}%\n")
                        f.write(f"Characters: {result.get('char_count', 0)}\n")
                        f.write(f"Words: {result.get('word_count', 0)}\n")
                        f.write("\n" + result.get('text', '') + "\n")
                    else:
                        f.write(f"Error: {result.get('error', 'Unknown')}\n")
                    
                    f.write("\n")
        
        return file_path

# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    print("Testing OCR Engine")
    
    # Initialize
    ocr = OCREngine()
    
    # Check available languages
    langs = ocr.get_available_languages()
    print(f"Available languages: {', '.join(langs[:5])}..." if langs else "No languages found")
    
    # Create a test image
    from PIL import Image, ImageDraw, ImageFont
    test_img = Image.new('RGB', (500, 200), color='white')
    draw = ImageDraw.Draw(test_img)
    
    try:
        # Try to use a font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Use default font
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Hello OCR Engine!", fill='black', font=font)
    draw.text((50, 100), "Testing with Python 3.14", fill='black', font=font)
    draw.text((50, 150), "No OpenCV required!", fill='black', font=font)
    
    # Save test image
    test_img.save("ocr_test_image.png")
    
    # Process the image
    print("\nProcessing test image...")
    result = ocr.extract_text(test_img, language='english')
    
    if result['success']:
        print(f"✅ OCR Successful!")
        print(f"   Confidence: {result['confidence']:.1f}%")
        print(f"   Characters: {result['char_count']}")
        print(f"   Words: {result['word_count']}")
        print(f"\nExtracted Text:\n{'-'*40}")
        print(result['text'])
        print('-'*40)
    else:
        print(f"❌ OCR Failed: {result['error']}")
    
    # Clean up
    import os
    if os.path.exists("ocr_test_image.png"):
        os.remove("ocr_test_image.png")
    
    print("\n" + ocr.get_performance_report())