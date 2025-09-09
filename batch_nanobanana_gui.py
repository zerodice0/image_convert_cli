#!/usr/bin/env python3
"""
Batch NanoBanana Image Generator - GUI Application
Generate images using Google's Gemini API with batch processing capabilities
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

# Third-party imports
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    from io import BytesIO
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install google-genai Pillow")
    exit(1)


class BatchNanoBananaGUI:
    """Main GUI application for batch image generation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Batch NanoBanana Image Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Application state
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.prompt_text = tk.StringVar(value="Create a picture of my cat eating a nano-banana in a fancy restaurant under the Gemini constellation")
        self.api_key = tk.StringVar()
        self.is_processing = False
        self.processing_thread = None
        
        # Supported image formats
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI components
        self.create_widgets()
        
        # Load settings if they exist
        self.load_settings()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_nanobanana.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="Batch NanoBanana Image Generator", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # API Key section
        ttk.Label(main_frame, text="API Key:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key, show="*", width=50)
        self.api_key_entry.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Folder selection section
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, 
                                                           sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="폴더 선택", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Input folder
        ttk.Label(main_frame, text="입력 폴더:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_folder, width=50)
        self.input_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="찾아보기", 
                  command=self.browse_input_folder).grid(row=row, column=2, pady=5)
        row += 1
        
        # Output folder
        ttk.Label(main_frame, text="출력 폴더:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_folder, width=50)
        self.output_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="찾아보기", 
                  command=self.browse_output_folder).grid(row=row, column=2, pady=5)
        row += 1
        
        # Prompt section
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, 
                                                           sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="프롬프트", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Prompt text area
        prompt_frame = ttk.Frame(main_frame)
        prompt_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        
        self.prompt_text_widget = scrolledtext.ScrolledText(prompt_frame, height=4, wrap=tk.WORD)
        self.prompt_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.prompt_text_widget.insert(tk.END, self.prompt_text.get())
        row += 1
        
        # Progress section
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, 
                                                           sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="진행 상황", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="준비됨")
        self.status_label.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="처리 시작", 
                                      command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", 
                                     command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = ttk.Button(button_frame, text="로그 지우기", 
                                          command=self.clear_log)
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Log section
        ttk.Label(main_frame, text="로그", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        row += 1
        
        # Log text area
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(row, weight=1)
    
    def browse_input_folder(self):
        """Open dialog to select input folder"""
        folder = filedialog.askdirectory(title="입력 이미지 폴더 선택")
        if folder:
            self.input_folder.set(folder)
            self.log_message(f"입력 폴더 선택: {folder}")
    
    def browse_output_folder(self):
        """Open dialog to select output folder"""
        folder = filedialog.askdirectory(title="출력 이미지 폴더 선택")
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"출력 폴더 선택: {folder}")
    
    def log_message(self, message: str):
        """Add message to log text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.logger.info(message)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def validate_inputs(self) -> bool:
        """Validate user inputs before processing"""
        if not self.api_key.get().strip():
            messagebox.showerror("오류", "API Key를 입력해주세요.")
            return False
        
        if not self.input_folder.get() or not os.path.exists(self.input_folder.get()):
            messagebox.showerror("오류", "올바른 입력 폴더를 선택해주세요.")
            return False
        
        if not self.output_folder.get():
            messagebox.showerror("오류", "출력 폴더를 선택해주세요.")
            return False
        
        prompt = self.prompt_text_widget.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showerror("오류", "프롬프트를 입력해주세요.")
            return False
        
        return True
    
    def get_image_files(self) -> List[Path]:
        """Get list of supported image files from input folder"""
        input_path = Path(self.input_folder.get())
        image_files = []
        
        for file_path in input_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        
        return sorted(image_files)
    
    def start_processing(self):
        """Start batch processing in a separate thread"""
        if not self.validate_inputs():
            return
        
        image_files = self.get_image_files()
        if not image_files:
            messagebox.showwarning("경고", "입력 폴더에 지원되는 이미지 파일이 없습니다.")
            return
        
        # Create output folder if it doesn't exist
        os.makedirs(self.output_folder.get(), exist_ok=True)
        
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.log_message(f"처리 시작: {len(image_files)}개 이미지")
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(
            target=self.process_images,
            args=(image_files,),
            daemon=True
        )
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the processing"""
        self.is_processing = False
        self.log_message("처리 중지 요청됨...")
    
    def process_images(self, image_files: List[Path]):
        """Process all images in the list"""
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=self.api_key.get())
            prompt = self.prompt_text_widget.get(1.0, tk.END).strip()
            
            total_files = len(image_files)
            successful = 0
            failed = 0
            
            for i, image_file in enumerate(image_files):
                if not self.is_processing:
                    self.log_message("처리가 중단되었습니다.")
                    break
                
                # Update status
                self.root.after(0, lambda f=image_file.name: 
                               self.status_label.config(text=f"처리 중: {f}"))
                
                try:
                    # Load and process image
                    self.log_message(f"처리 중: {image_file.name}")
                    
                    # Open image
                    with Image.open(image_file) as img:
                        # Generate image using Gemini
                        response = client.models.generate_content(
                            model="gemini-2.5-flash-image-preview",
                            contents=[prompt, img],
                        )
                        
                        # Process response
                        output_saved = False
                        for part in response.candidates[0].content.parts:
                            if part.inline_data is not None:
                                generated_image = Image.open(BytesIO(part.inline_data.data))
                                
                                # Save generated image
                                output_filename = f"{image_file.stem}_generated.png"
                                output_path = Path(self.output_folder.get()) / output_filename
                                
                                generated_image.save(output_path)
                                self.log_message(f"완료: {output_filename}")
                                successful += 1
                                output_saved = True
                                break
                        
                        if not output_saved:
                            self.log_message(f"생성된 이미지가 없음: {image_file.name}")
                            failed += 1
                
                except Exception as e:
                    self.log_message(f"오류 - {image_file.name}: {str(e)}")
                    failed += 1
                
                # Update progress bar
                progress = ((i + 1) / total_files) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
            
            # Final status update
            self.root.after(0, lambda: self.status_label.config(
                text=f"완료: 성공 {successful}, 실패 {failed}"))
            self.log_message(f"모든 처리 완료 - 성공: {successful}, 실패: {failed}")
            
        except Exception as e:
            self.log_message(f"치명적 오류: {str(e)}")
        finally:
            # Reset UI state
            self.root.after(0, self.processing_finished)
    
    def processing_finished(self):
        """Reset UI after processing is finished"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
    
    def load_settings(self):
        """Load settings from file if exists"""
        # This could be implemented to save/load user preferences
        pass
    
    def save_settings(self):
        """Save current settings to file"""
        # This could be implemented to save/load user preferences
        pass


def main():
    """Main entry point"""
    root = tk.Tk()
    app = BatchNanoBananaGUI(root)
    
    # Handle window close
    def on_closing():
        if app.is_processing:
            if messagebox.askokcancel("종료", "처리가 진행 중입니다. 정말 종료하시겠습니까?"):
                app.is_processing = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()