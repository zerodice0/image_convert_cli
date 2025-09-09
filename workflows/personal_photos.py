#!/usr/bin/env python3
"""
개인 사진 처리 워크플로우
GUI와 CLI 사이의 브릿지 역할을 하는 간단한 도구
"""

import os
import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import argparse


class PersonalPhotoProcessor:
    """개인 사진 처리를 위한 간단한 GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("개인 사진 AI 변환기")
        self.root.geometry("600x500")
        
        # 변수들
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.style_var = tk.StringVar(value="artistic")
        
        # 스타일 옵션
        self.styles = {
            "artistic": "이 사진을 예술적이고 아름다운 작품으로 변환해주세요",
            "vintage": "이 사진을 따뜻한 빈티지 스타일로 변환해주세요",
            "dramatic": "이 사진을 드라마틱하고 영화 같은 분위기로 변환해주세요",
            "bright": "이 사진을 밝고 생동감 있게 변환해주세요",
            "portrait": "이 인물 사진을 전문적인 포트레이트로 변환해주세요",
            "landscape": "이 풍경을 숨막히도록 아름다운 장면으로 변환해주세요",
            "custom": ""  # 사용자 입력
        }
        
        self.custom_prompt = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 제목
        title_label = ttk.Label(main_frame, text="🍌 개인 사진 AI 변환기", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # 폴더 선택 섹션
        ttk.Label(main_frame, text="📁 폴더 선택", 
                 font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # 입력 폴더
        ttk.Label(main_frame, text="원본 사진 폴더:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=40).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="선택", 
                  command=self.select_input_folder).grid(row=row, column=2, pady=5)
        row += 1
        
        # 출력 폴더
        ttk.Label(main_frame, text="결과 저장 폴더:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=40).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="선택", 
                  command=self.select_output_folder).grid(row=row, column=2, pady=5)
        row += 1
        
        # 스타일 선택 섹션
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        ttk.Label(main_frame, text="🎨 스타일 선택", 
                 font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # 스타일 라디오 버튼들
        style_frame = ttk.Frame(main_frame)
        style_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        styles_info = [
            ("artistic", "🎨 예술적 (추천)"),
            ("vintage", "📸 빈티지"),
            ("dramatic", "🎬 드라마틱"),
            ("bright", "☀️ 밝고 생동감"),
            ("portrait", "👤 인물 포트레이트"),
            ("landscape", "🏞️ 풍경"),
            ("custom", "✏️ 직접 입력")
        ]
        
        for i, (value, text) in enumerate(styles_info):
            ttk.Radiobutton(style_frame, text=text, variable=self.style_var, 
                          value=value, command=self.on_style_change).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=10, pady=3)
        
        row += 1
        
        # 커스텀 프롬프트 (처음엔 숨김)
        self.custom_frame = ttk.Frame(main_frame)
        self.custom_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.custom_frame, text="직접 입력:").grid(row=0, column=0, sticky=tk.W)
        self.custom_entry = ttk.Entry(self.custom_frame, textvariable=self.custom_prompt, width=60)
        self.custom_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.custom_frame.columnconfigure(0, weight=1)
        
        self.custom_frame.grid_remove()  # 처음엔 숨김
        row += 1
        
        # 처리 옵션
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        ttk.Label(main_frame, text="⚙️ 처리 옵션", 
                 font=('TkDefaultFont', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.preview_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="미리보기 모드 (처음 3장만 처리)", 
                       variable=self.preview_mode).grid(row=0, column=0, sticky=tk.W)
        
        self.open_result = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="완료 후 결과 폴더 열기", 
                       variable=self.open_result).grid(row=1, column=0, sticky=tk.W)
        
        row += 1
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="🧪 테스트 실행", 
                  command=self.test_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚀 처리 시작", 
                  command=self.start_processing).pack(side=tk.LEFT, padx=5)
        
        # 상태 표시
        self.status_label = ttk.Label(main_frame, text="준비됨")
        self.status_label.grid(row=row+1, column=0, columnspan=3, pady=10)
    
    def select_input_folder(self):
        """입력 폴더 선택"""
        folder = filedialog.askdirectory(title="원본 사진 폴더 선택")
        if folder:
            self.input_folder.set(folder)
            # 자동으로 출력 폴더 제안
            if not self.output_folder.get():
                suggested = str(Path(folder).parent / f"{Path(folder).name}_AI변환")
                self.output_folder.set(suggested)
    
    def select_output_folder(self):
        """출력 폴더 선택"""
        folder = filedialog.askdirectory(title="결과 저장 폴더 선택")
        if folder:
            self.output_folder.set(folder)
    
    def on_style_change(self):
        """스타일 변경 시 호출"""
        if self.style_var.get() == "custom":
            self.custom_frame.grid()
            self.custom_entry.focus()
        else:
            self.custom_frame.grid_remove()
    
    def validate_inputs(self):
        """입력 검증"""
        if not self.input_folder.get():
            messagebox.showerror("오류", "원본 사진 폴더를 선택해주세요.")
            return False
        
        if not os.path.exists(self.input_folder.get()):
            messagebox.showerror("오류", "선택한 입력 폴더가 존재하지 않습니다.")
            return False
        
        if not self.output_folder.get():
            messagebox.showerror("오류", "결과 저장 폴더를 선택해주세요.")
            return False
        
        if self.style_var.get() == "custom" and not self.custom_prompt.get().strip():
            messagebox.showerror("오류", "직접 입력 모드에서는 프롬프트를 입력해주세요.")
            return False
        
        # API 키 확인
        if not os.getenv('GEMINI_API_KEY'):
            config_file = Path.home() / '.nanobanana' / 'config'
            if not config_file.exists():
                result = messagebox.askyesno(
                    "API 키 필요", 
                    "API 키가 설정되지 않았습니다.\n\n"
                    "환경변수 GEMINI_API_KEY를 설정하거나\n"
                    "~/.nanobanana/config 파일을 만들어주세요.\n\n"
                    "Google AI Studio에서 API 키를 발급받으시겠습니까?"
                )
                if result:
                    import webbrowser
                    webbrowser.open("https://aistudio.google.com/")
                return False
        
        return True
    
    def get_prompt(self):
        """선택된 스타일의 프롬프트 반환"""
        style = self.style_var.get()
        if style == "custom":
            return self.custom_prompt.get().strip()
        else:
            return self.styles[style]
    
    def count_images(self, folder):
        """폴더의 이미지 개수 세기"""
        extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        count = 0
        folder_path = Path(folder)
        for file_path in folder_path.iterdir():
            if file_path.suffix.lower() in extensions:
                count += 1
        return count
    
    def test_run(self):
        """테스트 실행 (dry-run)"""
        if not self.validate_inputs():
            return
        
        image_count = self.count_images(self.input_folder.get())
        if image_count == 0:
            messagebox.showwarning("경고", "선택한 폴더에 이미지 파일이 없습니다.")
            return
        
        prompt = self.get_prompt()
        
        result = messagebox.showinfo(
            "테스트 실행 결과",
            f"📁 입력 폴더: {self.input_folder.get()}\n"
            f"📁 출력 폴더: {self.output_folder.get()}\n"
            f"🖼️  이미지 수: {image_count}개\n"
            f"🎨 스타일: {self.style_var.get()}\n"
            f"💬 프롬프트: {prompt}\n\n"
            f"✅ 설정이 올바릅니다!"
        )
    
    def start_processing(self):
        """실제 처리 시작"""
        if not self.validate_inputs():
            return
        
        image_count = self.count_images(self.input_folder.get())
        if image_count == 0:
            messagebox.showwarning("경고", "선택한 폴더에 이미지 파일이 없습니다.")
            return
        
        prompt = self.get_prompt()
        
        # 미리보기 모드 확인
        if self.preview_mode.get() and image_count > 3:
            result = messagebox.askyesno(
                "미리보기 모드",
                f"미리보기 모드가 활성화되어 있습니다.\n"
                f"처음 3장만 처리됩니다 (전체 {image_count}장 중).\n\n"
                f"계속하시겠습니까?"
            )
            if not result:
                return
        
        # 처리 명령어 구성
        cmd = [
            sys.executable, "batch_nanobanana_cli.py",
            "--input-dir", self.input_folder.get(),
            "--output-dir", self.output_folder.get(),
            "--prompt", prompt,
            "--verbose"
        ]
        
        # 미리보기 모드면 dry-run (실제로는 첫 3장만 처리하는 로직이 필요하지만 여기서는 단순화)
        if self.preview_mode.get():
            # 임시 폴더 만들어서 첫 3장만 복사하고 처리
            import shutil
            import tempfile
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # 첫 3장 복사
                extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
                copied = 0
                for file_path in Path(self.input_folder.get()).iterdir():
                    if file_path.suffix.lower() in extensions and copied < 3:
                        shutil.copy2(file_path, temp_dir)
                        copied += 1
                
                # 임시 폴더로 처리
                cmd[2] = temp_dir  # input-dir 변경
        
        try:
            self.status_label.config(text="처리 중... (CLI 창을 확인하세요)")
            self.root.update()
            
            # CLI 실행
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            self.status_label.config(text="✅ 처리 완료!")
            
            messagebox.showinfo("완료", "이미지 처리가 완료되었습니다!")
            
            # 결과 폴더 열기
            if self.open_result.get():
                if sys.platform == "win32":
                    os.startfile(self.output_folder.get())
                elif sys.platform == "darwin":
                    subprocess.run(["open", self.output_folder.get()])
                else:
                    subprocess.run(["xdg-open", self.output_folder.get()])
            
        except subprocess.CalledProcessError as e:
            self.status_label.config(text="❌ 처리 실패")
            messagebox.showerror("오류", f"처리 중 오류가 발생했습니다:\n{e}")
        except Exception as e:
            self.status_label.config(text="❌ 오류 발생")
            messagebox.showerror("오류", f"예상치 못한 오류가 발생했습니다:\n{e}")
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="개인 사진 AI 변환기")
    parser.add_argument("--cli", action="store_true", help="CLI 모드로 실행")
    parser.add_argument("--input-dir", help="입력 폴더")
    parser.add_argument("--output-dir", help="출력 폴더")
    parser.add_argument("--style", choices=list(PersonalPhotoProcessor().styles.keys()), 
                       default="artistic", help="스타일 선택")
    parser.add_argument("--prompt", help="커스텀 프롬프트")
    
    args = parser.parse_args()
    
    if args.cli:
        # CLI 모드
        if not args.input_dir or not args.output_dir:
            print("❌ CLI 모드에서는 --input-dir과 --output-dir이 필요합니다.")
            return 1
        
        processor = PersonalPhotoProcessor()
        if args.style == "custom":
            if not args.prompt:
                print("❌ 커스텀 스타일에서는 --prompt가 필요합니다.")
                return 1
            prompt = args.prompt
        else:
            prompt = processor.styles[args.style]
        
        # CLI로 직접 실행
        cmd = [
            sys.executable, "batch_nanobanana_cli.py",
            "--input-dir", args.input_dir,
            "--output-dir", args.output_dir,
            "--prompt", prompt,
            "--verbose"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ 처리 완료!")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"❌ 처리 실패: {e}")
            return 1
    else:
        # GUI 모드
        app = PersonalPhotoProcessor()
        app.run()
        return 0


if __name__ == "__main__":
    sys.exit(main())