"""
OCR COMMAND LINE INTERFACE
For batch processing and automation
"""

import argparse
import os
import sys
from datetime import datetime

from image_processor import ImageProcessor
from ocr_engine import OCREngine

def main():
    parser = argparse.ArgumentParser(description='OCR Application - Command Line Interface')
    
    # Input options
    parser.add_argument('input', help='Input image file or directory')
    
    # Processing options
    parser.add_argument('-l', '--language', default='indonesian',
                       help='OCR language (default: indonesian)')
    parser.add_argument('-o', '--output', default='ocr_results',
                       help='Output directory (default: ocr_results)')
    parser.add_argument('--preprocess', action='store_true',
                       help='Enable image preprocessing')
    parser.add_argument('--no-preprocess', action='store_false', dest='preprocess',
                       help='Disable image preprocessing')
    parser.set_defaults(preprocess=True)
    
    # Output options
    parser.add_argument('--format', choices=['txt', 'json', 'csv'], default='txt',
                       help='Output format (default: txt)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("="*60)
    print("OCR APPLICATION - COMMAND LINE MODE")
    print("="*60)
    
    # Initialize
    image_processor = ImageProcessor()
    ocr_engine = OCREngine()
    
    if args.verbose:
        image_processor.enable_debug(True)
        print(f"Language: {args.language}")
        print(f"Preprocessing: {'Enabled' if args.preprocess else 'Disabled'}")
    
    # Check if input is file or directory
    if os.path.isfile(args.input):
        process_single(args.input, image_processor, ocr_engine, args)
    elif os.path.isdir(args.input):
        process_directory(args.input, image_processor, ocr_engine, args)
    else:
        print(f"Error: Input not found: {args.input}")
        sys.exit(1)

def process_single(image_path, image_processor, ocr_engine, args):
    """Process single image file"""
    print(f"\nProcessing: {os.path.basename(image_path)}")
    
    try:
        # Load image
        image = Image.open(image_path)
        
        # Preprocess if enabled
        if args.preprocess:
            print("  Preprocessing image...")
            processed_array = image_processor.full_preprocessing_pipeline(
                image_path,
                show_steps=False
            )
            from PIL import Image
            processed_image = Image.fromarray(processed_array)
        else:
            processed_image = image
        
        # Perform OCR
        print(f"  Extracting text ({args.language})...")
        result = ocr_engine.extract_text(processed_image, args.language)
        
        if result['success']:
            # Create output directory
            os.makedirs(args.output, exist_ok=True)
            
            # Save results
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_file = os.path.join(args.output, base_name)
            
            # Save text
            txt_file = f"{output_file}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            # Save metadata
            json_file = f"{output_file}.json"
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                metadata = {
                    'filename': os.path.basename(image_path),
                    'language': result['language'],
                    'confidence': result['confidence'],
                    'characters': result['char_count'],
                    'words': result['word_count'],
                    'timestamp': datetime.now().isoformat()
                }
                json.dump(metadata, f, indent=2)
            
            print(f"  ✅ Success! Confidence: {result['confidence']:.1f}%")
            print(f"  📁 Results saved to: {txt_file}")
            
            if args.verbose:
                print(f"\nExtracted text (first 500 chars):")
                print("-"*60)
                print(result['text'][:500])
                if len(result['text']) > 500:
                    print("...")
                print("-"*60)
        else:
            print(f"  ❌ Failed: {result['error']}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

def process_directory(directory, image_processor, ocr_engine, args):
    """Process all images in directory"""
    # Get all image files
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    image_files = []
    
    for file in os.listdir(directory):
        if any(file.lower().endswith(ext) for ext in extensions):
            image_files.append(os.path.join(directory, file))
    
    if not image_files:
        print(f"No image files found in: {directory}")
        return
    
    print(f"\nFound {len(image_files)} image(s) in directory")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Process each file
    results = []
    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] {os.path.basename(image_path)}")
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess if enabled
            if args.preprocess:
                processed_array = image_processor.full_preprocessing_pipeline(
                    image_path,
                    show_steps=False
                )
                from PIL import Image
                processed_image = Image.fromarray(processed_array)
            else:
                processed_image = image
            
            # Perform OCR
            result = ocr_engine.extract_text(processed_image, args.language)
            result['filename'] = os.path.basename(image_path)
            results.append(result)
            
            if result['success']:
                print(f"  ✅ {result['confidence']:.1f}% confidence")
            else:
                print(f"  ❌ {result['error']}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    # Generate summary report
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    if successful:
        avg_conf = sum(r['confidence'] for r in successful) / len(successful)
        total_chars = sum(r['char_count'] for r in successful)
        
        print(f"Processed: {len(image_files)} files")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(image_files) - len(successful)}")
        print(f"Average confidence: {avg_conf:.1f}%")
        print(f"Total characters: {total_chars}")
    else:
        print("No successful OCR results")
    
    # Export combined results
    if args.format == 'csv':
        export_csv(results, args.output)
    elif args.format == 'json':
        export_json(results, args.output)
    else:
        export_txt(results, args.output)
    
    print(f"\nResults saved to: {args.output}/")

def export_csv(results, output_dir):
    """Export results to CSV"""
    import csv
    
    csv_file = os.path.join(output_dir, "ocr_results.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename', 'Success', 'Language', 'Confidence', 
                        'Characters', 'Words', 'Text_Preview'])
        
        for result in results:
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
    
    print(f"CSV report: {csv_file}")

def export_json(results, output_dir):
    """Export results to JSON"""
    import json
    
    json_file = os.path.join(output_dir, "ocr_results.json")
    
    # Prepare data for JSON
    export_data = []
    for result in results:
        result_copy = result.copy()
        export_data.append(result_copy)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"JSON report: {json_file}")

def export_txt(results, output_dir):
    """Export results to text file"""
    txt_file = os.path.join(output_dir, "ocr_results.txt")
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("OCR BATCH PROCESSING RESULTS\n")
        f.write("="*60 + "\n\n")
        
        for result in results:
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
            
            f.write("\n" + "-"*60 + "\n\n")
    
    print(f"Text report: {txt_file}")

if __name__ == "__main__":
    main()