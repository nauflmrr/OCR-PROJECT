"""
OCR APPLICATION GUI
Complete GUI with image preview and text extraction
No OpenCV required
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime

# Import our modules
try:
    from image_processor import ImageProcessor
    from ocr_engine import OCREngine
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    print(f"Import Error: {e}")
    print("Make sure image_processor.py and ocr_engine.py are in the same directory")

class OCRApplication:
    """Main GUI Application for OCR"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Application - Python 3.14 (No OpenCV)")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set icon (optional)
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Initialize modules
        self.image_processor = None
        self.ocr_engine = None
        
        if IMPORT_SUCCESS:
            self.image_processor = ImageProcessor()
            self.ocr_engine = OCREngine()
        else:
            messagebox.showerror("Import Error", 
                               "Required modules not found!\n"
                               "Make sure image_processor.py and ocr_engine.py\n"
                               "are in the same directory.")
            self.root.destroy()
            return
        
        # Application state
        self.current_image_path = None
        self.original_image = None
        self.processed_image = None
        self.current_result = None
        self.history = []
        
        # Setup UI
        self.setup_ui()
        
        # Status
        self.update_status("Ready")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Image processing
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Right panel - OCR results
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        # ===== LEFT PANEL: IMAGE PROCESSING =====
        # Image selection frame
        select_frame = ttk.LabelFrame(left_panel, text="Image Selection", padding=10)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(select_frame, text="📁 Open Image", 
                  command=self.open_image).pack(side=tk.LEFT, padx=5)
        
        self.image_label = ttk.Label(select_frame, text="No image selected")
        self.image_label.pack(side=tk.LEFT, padx=10)
        
        # Image display frame
        display_frame = ttk.LabelFrame(left_panel, text="Image Preview", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for original image
        self.original_canvas = tk.Canvas(display_frame, bg='gray', width=400, height=300)
        self.original_canvas.pack(pady=5)
        ttk.Label(display_frame, text="Original Image").pack()
        
        # Canvas for processed image
        self.processed_canvas = tk.Canvas(display_frame, bg='gray', width=400, height=300)
        self.processed_canvas.pack(pady=5)
        ttk.Label(display_frame, text="Processed Image").pack()
        
        # Processing controls
        process_frame = ttk.LabelFrame(left_panel, text="Processing Controls", padding=10)
        process_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(process_frame, text="🔄 Preprocess Image", 
                  command=self.preprocess_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(process_frame, text="👁️ Show Steps", 
                  command=self.show_processing_steps).pack(side=tk.LEFT, padx=5)
        
        # ===== RIGHT PANEL: OCR CONTROLS =====
        # Language selection
        lang_frame = ttk.LabelFrame(right_panel, text="OCR Settings", padding=10)
        lang_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(lang_frame, text="Language:").grid(row=0, column=0, padx=5, pady=5)
        
        self.language_var = tk.StringVar(value="indonesian")
        languages = ['indonesian', 'english', 'french', 'spanish', 'german', 'ind+eng']
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                      values=languages, state="readonly", width=15)
        self.lang_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(lang_frame, text="🌐 Check Languages", 
                  command=self.check_languages).grid(row=0, column=2, padx=10)
        
        # OCR buttons
        ocr_frame = ttk.Frame(right_panel)
        ocr_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(ocr_frame, text="🔍 Extract Text", 
                  command=self.extract_text).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(ocr_frame, text="📊 View Stats", 
                  command=self.show_stats).pack(side=tk.LEFT, padx=5)
        
        # Results display
        result_frame = ttk.LabelFrame(right_panel, text="OCR Results", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                    font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Result info
        info_frame = ttk.Frame(right_panel)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.pack()
        
        # Bottom buttons
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="💾 Save Text", 
                  command=self.save_text).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📈 Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Clear", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu bar
        self.setup_menu()
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Text", command=self.save_text, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Process menu
        process_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Process", menu=process_menu)
        process_menu.add_command(label="Preprocess Image", command=self.preprocess_image)
        process_menu.add_command(label="Extract Text", command=self.extract_text)
        process_menu.add_separator()
        process_menu.add_command(label="Batch Process Folder", command=self.batch_process)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Check Tesseract", command=self.check_tesseract)
        tools_menu.add_command(label="Performance Stats", command=self.show_stats)
        tools_menu.add_command(label="Processing Report", command=self.show_report)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_text())
    
    def update_status(self, message):
        """Update status bar"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"{timestamp} | {message}")
        self.root.update_idletasks()
    
    def open_image(self):
        """Open image file dialog"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if filename:
            self.current_image_path = filename
            self.image_label.config(text=os.path.basename(filename))
            
            try:
                # Load and display original image
                self.original_image = Image.open(filename)
                self.display_image(self.original_image, self.original_canvas)
                
                # Reset processed image
                self.processed_image = None
                self.processed_canvas.delete("all")
                self.processed_canvas.create_text(200, 150, 
                                                 text="Click 'Preprocess Image'", 
                                                 fill="white")
                
                self.update_status(f"Loaded: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open image:\n{str(e)}")
    
    def display_image(self, image, canvas):
        """Display image on canvas"""
        canvas.delete("all")
        
        # Resize image to fit canvas
        canvas_width = canvas.winfo_width() or 400
        canvas_height = canvas.winfo_height() or 300
        
        img_width, img_height = image.size
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        if ratio < 1:
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Store reference to prevent garbage collection
        canvas.image = photo
        
        # Display centered
        x = (canvas_width - image.size[0]) // 2
        y = (canvas_height - image.size[1]) // 2
        canvas.create_image(x, y, anchor=tk.NW, image=photo)
    
    def preprocess_image(self):
        """Preprocess the current image"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please open an image first!")
            return
        
        self.update_status("Preprocessing image...")
        
        try:
            # Process image
            self.processed_image = self.image_processor.full_preprocessing_pipeline(
                self.current_image_path,
                show_steps=False
            )
            
            # Display processed image
            self.display_image(self.processed_image, self.processed_canvas)
            
            # Show processing report
            report = self.image_processor.get_processing_report()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, report)
            
            self.update_status("Image preprocessing completed")
            messagebox.showinfo("Success", "Image preprocessing completed!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Preprocessing failed:\n{str(e)}")
            self.update_status("Preprocessing failed")
    
    def show_processing_steps(self):
        """Show image processing steps"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please open an image first!")
            return
        
        try:
            # Reprocess with visualization
            self.image_processor.full_preprocessing_pipeline(
                self.current_image_path,
                show_steps=True
            )
        except Exception as e:
            messagebox.showerror("Error", f"Cannot show steps:\n{str(e)}")
    
    def extract_text(self):
        """Extract text from image"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please open an image first!")
            return
        
        # Use processed image if available, otherwise original
        image_to_ocr = self.processed_image if self.processed_image else self.original_image
        
        if image_to_ocr is None:
            messagebox.showerror("Error", "No image to process!")
            return
        
        self.update_status("Extracting text...")
        
        try:
            # Get selected language
            language = self.language_var.get()
            
            # Perform OCR
            result = self.ocr_engine.extract_text(image_to_ocr, language)
            
            # Store result
            self.current_result = result
            self.history.append(result)
            
            # Display results
            self.display_results(result)
            
            self.update_status(f"Text extraction completed ({result['confidence']:.1f}% confidence)")
            
        except Exception as e:
            messagebox.showerror("Error", f"OCR failed:\n{str(e)}")
            self.update_status("Text extraction failed")
    
    def display_results(self, result):
        """Display OCR results"""
        self.result_text.delete(1.0, tk.END)
        
        if result['success']:
            # Display extracted text
            self.result_text.insert(1.0, result['text'])
            
            # Update info label
            info_text = (f"Language: {result['language']} | "
                        f"Confidence: {result['confidence']:.1f}% | "
                        f"Words: {result['word_count']} | "
                        f"Characters: {result['char_count']}")
            self.info_label.config(text=info_text)
        else:
            self.result_text.insert(1.0, f"Error: {result['error']}")
            self.info_label.config(text="Extraction failed")
    
    def save_text(self):
        """Save extracted text to file"""
        if not self.current_result or not self.current_result.get('text'):
            messagebox.showwarning("Warning", "No text to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"ocr_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Add metadata header
                    if self.current_result['success']:
                        f.write(f"OCR Result - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"File: {os.path.basename(self.current_image_path)}\n")
                        f.write(f"Language: {self.current_result['language']}\n")
                        f.write(f"Confidence: {self.current_result['confidence']:.1f}%\n")
                        f.write("="*50 + "\n\n")
                    
                    f.write(self.current_result['text'])
                
                self.update_status(f"Saved to: {filename}")
                messagebox.showinfo("Success", f"Text saved to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file:\n{str(e)}")
    
    def export_results(self):
        """Export results in different formats"""
        if not self.ocr_engine.ocr_results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        # Create export dialog
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Results")
        export_window.geometry("400x300")
        export_window.transient(self.root)
        export_window.grab_set()
        
        ttk.Label(export_window, text="Select Export Format:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        format_var = tk.StringVar(value="txt")
        
        ttk.Radiobutton(export_window, text="Text File (.txt)", 
                       variable=format_var, value="txt").pack(pady=5)
        ttk.Radiobutton(export_window, text="JSON File (.json)", 
                       variable=format_var, value="json").pack(pady=5)
        ttk.Radiobutton(export_window, text="CSV File (.csv)", 
                       variable=format_var, value="csv").pack(pady=5)
        
        def do_export():
            format_type = format_var.get()
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")],
                initialfile=f"ocr_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            )
            
            if filename:
                try:
                    export_path = self.ocr_engine.export_results(format_type, filename[:-4])
                    messagebox.showinfo("Success", f"Exported to:\n{export_path}")
                    export_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed:\n{str(e)}")
        
        ttk.Button(export_window, text="Export", command=do_export).pack(pady=20)
        ttk.Button(export_window, text="Cancel", command=export_window.destroy).pack()
    
    def copy_to_clipboard(self):
        """Copy text to clipboard"""
        if not self.current_result or not self.current_result.get('text'):
            messagebox.showwarning("Warning", "No text to copy!")
            return
        
        text = self.current_result['text']
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.update_status("Text copied to clipboard")
    
    def clear_all(self):
        """Clear all data"""
        if messagebox.askyesno("Confirm", "Clear all data?"):
            self.current_image_path = None
            self.original_image = None
            self.processed_image = None
            self.current_result = None
            
            self.image_label.config(text="No image selected")
            self.original_canvas.delete("all")
            self.processed_canvas.delete("all")
            self.result_text.delete(1.0, tk.END)
            self.info_label.config(text="")
            
            self.update_status("Cleared all data")
    
    def batch_process(self):
        """Process multiple images"""
        folder = filedialog.askdirectory(title="Select folder with images")
        
        if folder:
            # Get image files
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
            image_files = []
            
            for file in os.listdir(folder):
                if any(file.lower().endswith(ext) for ext in extensions):
                    image_files.append(os.path.join(folder, file))
            
            if not image_files:
                messagebox.showwarning("Warning", "No image files found in folder!")
                return
            
            # Ask for output directory
            output_dir = filedialog.askdirectory(title="Select output directory")
            if not output_dir:
                return
            
            # Process in background
            self.update_status(f"Processing {len(image_files)} images...")
            
            try:
                results = self.ocr_engine.batch_process(
                    image_files,
                    language=self.language_var.get(),
                    save_results=True,
                    output_dir=output_dir
                )
                
                # Show summary
                successful = sum(1 for r in results if r['success'])
                messagebox.showinfo("Batch Complete", 
                                  f"Processed {len(image_files)} images\n"
                                  f"Successful: {successful}\n"
                                  f"Failed: {len(image_files) - successful}\n"
                                  f"Results saved to: {output_dir}")
                
                self.update_status(f"Batch processing completed")
                
            except Exception as e:
                messagebox.showerror("Error", f"Batch processing failed:\n{str(e)}")
    
    def check_languages(self):
        """Check available Tesseract languages"""
        try:
            langs = self.ocr_engine.get_available_languages()
            if langs:
                messagebox.showinfo("Available Languages", 
                                  f"Found {len(langs)} languages:\n\n" + 
                                  ", ".join(langs))
            else:
                messagebox.showwarning("Warning", "No languages found!")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot check languages:\n{str(e)}")
    
    def check_tesseract(self):
        """Check Tesseract installation"""
        try:
            import pytesseract
            import subprocess
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            cmd = [tesseract_path, "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Tesseract Info", 
                                  f"Tesseract installed:\n\n{result.stdout}")
            else:
                messagebox.showerror("Error", f"Tesseract check failed:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot check Tesseract:\n{str(e)}")
    
    def show_stats(self):
        """Show performance statistics"""
        if not self.ocr_engine.ocr_results:
            messagebox.showwarning("Warning", "No results to show statistics!")
            return
        
        stats = self.ocr_engine.get_performance_report()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, stats)
        self.update_status("Displaying statistics")
    
    def show_report(self):
        """Show processing report"""
        if not self.image_processor.processing_steps:
            messagebox.showwarning("Warning", "No processing steps to report!")
            return
        
        report = self.image_processor.get_processing_report()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, report)
        self.update_status("Displaying processing report")
    
    def show_about(self):
        """Show about dialog"""
        about_text = (
            "OCR Application\n"
            "Version 1.0\n\n"
            "Developed with Python 3.14\n"
            "No OpenCV required\n\n"
            "Features:\n"
            "• Image preprocessing with PIL\n"
            "• Text extraction with Tesseract\n"
            "• Multiple language support\n"
            "• Batch processing\n"
            "• Export to various formats\n\n"
            "© 2024 OCR Application"
        )
        messagebox.showinfo("About", about_text)
    
    def show_docs(self):
        """Show documentation"""
        docs_text = (
            "HOW TO USE:\n\n"
            "1. Open an image (File > Open Image)\n"
            "2. Preprocess the image if needed\n"
            "3. Select language for OCR\n"
            "4. Click 'Extract Text'\n"
            "5. Save or export results\n\n"
            "TIPS:\n"
            "• For better results, preprocess images first\n"
            "• Use high-quality images with clear text\n"
            "• Adjust language based on text content\n"
            "• Batch process for multiple images\n\n"
            "SHORTCUTS:\n"
            "Ctrl+O: Open image\n"
            "Ctrl+S: Save text"
        )
        messagebox.showinfo("Documentation", docs_text)

# ===== MAIN FUNCTION =====
def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set style
    try:
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme
    except:
        pass
    
    app = OCRApplication(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()