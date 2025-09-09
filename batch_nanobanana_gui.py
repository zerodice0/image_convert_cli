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
    from PIL import Image, ImageTk
    from io import BytesIO
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install google-genai Pillow")
    exit(1)

# Import the new image variation functionality
from batch_nanobanana_core import ImageVariationProcessor


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
        
        # Variation mode state
        self.selected_variation_image = None
        self.selected_variation_dir = None
        
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
        """Create and layout all GUI widgets with tabbed interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="NanoBanana Image Generator", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # API Key section (shared across all tabs)
        api_frame = ttk.Frame(main_frame)
        api_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=50)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create frames for each tab
        self.batch_frame = ttk.Frame(self.notebook)
        self.variation_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.batch_frame, text="배치 처리")
        self.notebook.add(self.variation_frame, text="이미지 변형")
        
        # Create batch processing tab (original functionality)
        self.create_batch_tab()
        
        # Create image variation tab (new functionality)
        self.create_variation_tab()
    
    def create_batch_tab(self):
        """Create the original batch processing tab"""
        # Configure grid weights
        self.batch_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Folder selection section
        ttk.Label(self.batch_frame, text="폴더 선택", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Input folder
        ttk.Label(self.batch_frame, text="입력 폴더:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(self.batch_frame, textvariable=self.input_folder, width=50)
        self.input_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(self.batch_frame, text="찾아보기", 
                  command=self.browse_input_folder).grid(row=row, column=2, pady=5)
        row += 1
        
        # Output folder
        ttk.Label(self.batch_frame, text="출력 폴더:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(self.batch_frame, textvariable=self.output_folder, width=50)
        self.output_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(self.batch_frame, text="찾아보기", 
                  command=self.browse_output_folder).grid(row=row, column=2, pady=5)
        row += 1
        
        # Prompt section
        ttk.Separator(self.batch_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, 
                                                           sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(self.batch_frame, text="프롬프트", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Prompt text area
        prompt_frame = ttk.Frame(self.batch_frame)
        prompt_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        
        self.prompt_text_widget = scrolledtext.ScrolledText(prompt_frame, height=4, wrap=tk.WORD)
        self.prompt_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.prompt_text_widget.insert(tk.END, self.prompt_text.get())
        row += 1
        
        # Progress section
        ttk.Separator(self.batch_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, 
                                                           sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(self.batch_frame, text="진행 상황", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.batch_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Status label
        self.status_label = ttk.Label(self.batch_frame, text="준비됨")
        self.status_label.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        
        # Control buttons
        button_frame = ttk.Frame(self.batch_frame)
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
        ttk.Label(self.batch_frame, text="로그", font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        row += 1
        
        # Log text area
        log_frame = ttk.Frame(self.batch_frame)
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.batch_frame.rowconfigure(row, weight=1)
    
    def create_variation_tab(self):
        """Create the image variation tab"""
        # Initialize variation-specific variables
        self.variation_selected_image = None
        self.variation_count = tk.IntVar(value=5)
        self.variation_type = tk.StringVar(value="random")
        self.variation_output_dir = tk.StringVar()
        self.variation_progress = tk.DoubleVar()
        self.variation_status = tk.StringVar(value="이미지를 선택하세요")
        self.variation_processing = False
        self.variation_results = []
        
        # Configure grid weights
        self.variation_frame.columnconfigure(1, weight=1)
        self.variation_frame.rowconfigure(7, weight=1)  # Gallery row should expand
        
        row = 0
        
        # Image selection section
        image_section = ttk.LabelFrame(self.variation_frame, text="📷 원본 이미지 선택")
        image_section.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        image_section.columnconfigure(1, weight=1)
        row += 1
        
        # Image preview
        self.image_preview = tk.Label(image_section, text="이미지를 선택하세요", 
                                      relief="sunken", width=40, height=15,
                                      background="white", anchor="center")
        self.image_preview.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Image selection button
        ttk.Button(image_section, text="이미지 선택", 
                  command=self.select_variation_image).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Selected image info
        self.image_info_label = ttk.Label(image_section, text="")
        self.image_info_label.grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Variation settings section
        settings_section = ttk.LabelFrame(self.variation_frame, text="⚙️ 변형 설정")
        settings_section.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        settings_section.columnconfigure(1, weight=1)
        row += 1
        
        # Count setting
        ttk.Label(settings_section, text="변형 개수:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        count_spinbox = ttk.Spinbox(settings_section, from_=1, to=20, textvariable=self.variation_count, width=10)
        count_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Type setting
        ttk.Label(settings_section, text="변형 타입:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        type_combo = ttk.Combobox(settings_section, textvariable=self.variation_type, width=20, state="readonly")
        type_combo['values'] = ("랜덤 변형", "객체 재배치", "객체 추가", "객체 제거", "스타일 변경", "구도 변경")
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Output directory setting
        ttk.Label(settings_section, text="출력 폴더:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        output_frame = ttk.Frame(settings_section)
        output_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.variation_output_entry = ttk.Entry(output_frame, textvariable=self.variation_output_dir, width=30)
        self.variation_output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="찾아보기", 
                  command=self.select_variation_output_folder).grid(row=0, column=1)
        
        # Start button
        start_frame = ttk.Frame(self.variation_frame)
        start_frame.grid(row=row, column=0, columnspan=3, pady=20)
        row += 1
        
        self.variation_start_button = ttk.Button(start_frame, text="변형 생성 시작", 
                                               command=self.start_variation_generation)
        self.variation_start_button.pack()
        
        # Progress section
        progress_section = ttk.Frame(self.variation_frame)
        progress_section.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        progress_section.columnconfigure(0, weight=1)
        row += 1
        
        ttk.Label(progress_section, text="📊 진행률", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        self.variation_progress_bar = ttk.Progressbar(progress_section, variable=self.variation_progress, 
                                                    maximum=100, length=400)
        self.variation_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.variation_status_label = ttk.Label(progress_section, textvariable=self.variation_status)
        self.variation_status_label.grid(row=2, column=0, pady=5)
        
        # Results gallery section
        gallery_section = ttk.LabelFrame(self.variation_frame, text="🖼️ 결과 갤러리")
        gallery_section.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=5)
        gallery_section.columnconfigure(0, weight=1)
        gallery_section.rowconfigure(0, weight=1)
        row += 1
        
        # Scrollable gallery
        gallery_canvas = tk.Canvas(gallery_section, height=200, background="white")
        gallery_scrollbar = ttk.Scrollbar(gallery_section, orient="horizontal", command=gallery_canvas.xview)
        self.gallery_frame = ttk.Frame(gallery_canvas)
        
        gallery_canvas.configure(xscrollcommand=gallery_scrollbar.set)
        gallery_canvas.create_window((0, 0), window=self.gallery_frame, anchor="nw")
        
        gallery_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        gallery_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Update scroll region when frame changes
        def configure_scroll(event):
            gallery_canvas.configure(scrollregion=gallery_canvas.bbox("all"))
        
        self.gallery_frame.bind("<Configure>", configure_scroll)
    
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
    
    # =========================
    # Image Variation Methods
    # =========================
    
    def select_variation_image(self):
        """이미지 파일 선택 대화상자"""
        filetypes = [
            ("이미지 파일", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff"),
            ("모든 파일", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="변형할 이미지 선택",
            filetypes=filetypes
        )
        
        if filepath:
            self.selected_variation_image = filepath
            self.variation_image_path.set(os.path.basename(filepath))
            self.update_image_preview(filepath)
    
    def update_image_preview(self, filepath):
        """이미지 미리보기 업데이트"""
        try:
            from PIL import Image, ImageTk
            
            # PIL로 이미지 로드 및 리사이즈
            img = Image.open(filepath)
            img.thumbnail((300, 200), Image.Resampling.LANCZOS)
            
            # Tkinter PhotoImage로 변환
            photo = ImageTk.PhotoImage(img)
            self.image_preview.configure(image=photo, text="")
            self.image_preview.image = photo  # 참조 유지
            
        except Exception as e:
            messagebox.showerror("오류", f"이미지 로드 실패: {e}")
    
    def select_variation_output_folder(self):
        """변형 출력 폴더 선택"""
        folder = filedialog.askdirectory(title="변형 결과 저장 폴더 선택")
        if folder:
            self.variation_output_dir.set(folder)
    
    def start_variation_generation(self):
        """변형 생성 시작"""
        if not self.validate_variation_inputs():
            return
        
        # UI 상태 변경
        self.set_variation_processing_state(True)
        
        # 갤러리 초기화
        self.clear_variation_gallery()
        
        # 백그라운드 스레드에서 처리
        self.variation_processing_thread = threading.Thread(
            target=self.process_variations_background,
            daemon=True
        )
        self.variation_processing_thread.start()
    
    def validate_variation_inputs(self) -> bool:
        """변형 입력값 검증"""
        if not self.api_key.get().strip():
            messagebox.showerror("오류", "API Key를 입력해주세요.")
            return False
        
        # Source validation based on mode
        if hasattr(self, 'source_mode') and self.source_mode.get() == "multiple":
            if not hasattr(self, 'selected_variation_dir') or not self.selected_variation_dir:
                messagebox.showerror("오류", "변형할 이미지들이 있는 디렉토리를 선택해주세요.")
                return False
            
            if not os.path.exists(self.selected_variation_dir):
                messagebox.showerror("오류", "선택한 디렉토리가 존재하지 않습니다.")
                return False
        else:
            # Single image mode (fallback for backward compatibility)
            if not hasattr(self, 'selected_variation_image') or not self.selected_variation_image:
                messagebox.showerror("오류", "변형할 이미지를 선택해주세요.")
                return False
            
            if not os.path.exists(self.selected_variation_image):
                messagebox.showerror("오류", "선택한 이미지 파일이 존재하지 않습니다.")
                return False
        
        if not self.variation_output_dir.get():
            messagebox.showerror("오류", "출력 폴더를 선택해주세요.")
            return False
        
        try:
            count = int(self.variation_count.get())
            if count < 1 or count > 20:
                messagebox.showerror("오류", "변형 개수는 1~20 사이여야 합니다.")
                return False
        except ValueError:
            messagebox.showerror("오류", "올바른 변형 개수를 입력해주세요.")
            return False
        
        return True
    
    def process_variations_background(self):
        """백그라운드에서 변형 처리"""
        try:
            # ImageVariationProcessor 생성
            processor = ImageVariationProcessor(
                api_key=self.api_key.get(),
                model="gemini-2.5-flash-image-preview"
            )
            
            # 변형 설정
            count = int(self.variation_count.get())
            variation_type = self.get_variation_type()
            output_dir = Path(self.variation_output_dir.get())
            
            # 변형 생성
            results = processor.generate_variations(
                image_path=Path(self.selected_variation_image),
                count=count,
                variation_type=variation_type,
                output_dir=output_dir,
                progress_callback=self.update_variation_progress,
                result_callback=self.add_result_to_gallery
            )
            
            # 완료 후 UI 업데이트
            self.root.after(0, lambda: self.on_variation_processing_complete(results))
            
        except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: self.on_variation_processing_error(error_message))
    
    def get_variation_type(self):
        """현재 선택된 변형 타입 반환"""
        type_mapping = {
            "랜덤 변형": "random",
            "객체 재배치": "object_rearrange", 
            "객체 추가": "object_add",
            "객체 제거": "object_remove",
            "스타일 변경": "style_change",
            "구도 변경": "composition"
        }
        return type_mapping.get(self.variation_type.get(), "random")
    
    def update_variation_progress(self, current, total, message=""):
        """변형 진행률 업데이트"""
        def update_ui():
            percentage = (current / total) * 100
            self.variation_progress.set(percentage)
            self.variation_status.set(f"{message} ({current}/{total} 완료)")
            
        self.root.after(0, update_ui)
    
    def add_result_to_gallery(self, image_path, index):
        """갤러리에 결과 이미지 추가"""
        def update_gallery():
            try:
                from PIL import Image, ImageTk
                
                # 썸네일 생성
                img = Image.open(image_path)
                img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # 이미지 버튼 생성 (클릭 시 전체 크기로 보기)
                btn = ttk.Button(
                    self.gallery_frame,
                    image=photo,
                    command=lambda: self.view_full_variation_image(image_path)
                )
                btn.image = photo  # 참조 유지
                btn.grid(row=0, column=index, padx=5, pady=5)
                
                # 인덱스 라벨
                ttk.Label(
                    self.gallery_frame, 
                    text=f"{index+1}"
                ).grid(row=1, column=index)
                
            except Exception as e:
                self.log_message(f"갤러리 이미지 추가 실패: {e}")
        
        self.root.after(0, update_gallery)
    
    def view_full_variation_image(self, image_path):
        """전체 크기 이미지 뷰어 창 열기"""
        try:
            from PIL import Image, ImageTk
            
            viewer_window = tk.Toplevel(self.root)
            viewer_window.title(f"결과 이미지: {os.path.basename(image_path)}")
            
            img = Image.open(image_path)
            # 화면 크기에 맞게 조정
            screen_width = viewer_window.winfo_screenwidth()
            screen_height = viewer_window.winfo_screenheight()
            max_size = (int(screen_width * 0.8), int(screen_height * 0.8))
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(viewer_window, image=photo)
            label.image = photo
            label.pack(padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("오류", f"이미지 뷰어 오류: {e}")
    
    def clear_variation_gallery(self):
        """변형 갤러리 초기화"""
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
    
    def set_variation_processing_state(self, processing: bool):
        """변형 처리 상태에 따른 UI 업데이트"""
        state = "disabled" if processing else "normal"
        
        # 버튼들 상태 변경 (실제로는 필요시 나중에 구현)
        self.variation_start_button.config(state=state)
        
        # 진행률 표시
        if processing:
            self.variation_progress.set(0)
            self.variation_status.set("변형 생성 시작...")
        else:
            self.variation_status.set("대기 중...")
    
    def on_variation_processing_complete(self, results):
        """변형 처리 완료 시 호출"""
        self.set_variation_processing_state(False)
        
        success_count = results.get("successful", 0)
        failed_count = results.get("failed", 0)
        total_count = results.get("total", 0)
        
        message = f"변형 생성 완료: 성공 {success_count}개, 실패 {failed_count}개 (총 {total_count}개)"
        self.log_message(message)
        
        if failed_count > 0:
            messagebox.showwarning("완료", f"{message}\n\n일부 변형 생성에 실패했습니다.")
        else:
            messagebox.showinfo("완료", message)
    
    def on_variation_processing_error(self, error_message):
        """변형 처리 오류 시 호출"""
        self.set_variation_processing_state(False)
        self.log_message(f"변형 생성 오류: {error_message}")
        messagebox.showerror("오류", f"변형 생성 중 오류가 발생했습니다:\n{error_message}")


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