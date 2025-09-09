# Phase 2: GUI 인터페이스 확장

## 📋 개요
기존 GUI 애플리케이션에 이미지 변형 생성 기능을 추가하여, 사용자가 직관적으로 이미지 변형을 생성할 수 있도록 하는 단계입니다.

## 🎯 목표
- GUI에 이미지 변형 전용 탭 추가
- 단일 이미지 선택 및 미리보기 기능 구현
- 변형 개수 설정 및 스타일 옵션 UI 개발
- 실시간 진행률 표시 및 결과 갤러리 기능

## 🖥️ GUI 설계

### 1. 탭 구조 변경
```python
# batch_nanobanana_gui.py 확장
class BatchNanoBananaGUI:
    def create_widgets(self):
        # 기존 메인 프레임을 탭 컨테이너로 변경
        self.notebook = ttk.Notebook(self.root)
        
        # 기존 배치 처리 탭
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="배치 처리")
        
        # 새로운 이미지 변형 탭
        self.variation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.variation_frame, text="이미지 변형")
        
        self.notebook.pack(expand=True, fill='both')
```

### 2. 이미지 변형 탭 레이아웃
```
┌─────────────────────────────────────────────────────────┐
│ [배치 처리] [이미지 변형]                                    │
├─────────────────────────────────────────────────────────┤
│ 📷 원본 이미지 선택                                         │
│ ┌─────────────────┐  [이미지 선택 버튼]                     │
│ │   이미지 미리보기    │                                      │
│ │      영역          │                                      │
│ └─────────────────┘                                      │
│                                                         │
│ ⚙️ 변형 설정                                              │
│ 변형 개수: [5     ] 개                                    │
│ 변형 타입: [랜덤 변형    ▼]                                │
│ 출력 폴더: [/path/to/output] [폴더 선택]                    │
│                                                         │
│ 🎨 스타일 옵션                                             │
│ ☐ 객체 재배치  ☐ 객체 추가  ☐ 객체 제거                      │
│ ☐ 스타일 변경  ☐ 구도 변경                                  │
│                                                         │
│                            [변형 생성 시작]                 │
│ ─────────────────────────────────────────────────────── │
│ 📊 진행률: ████████░░ 80% (4/5 완료)                      │
│                                                         │
│ 🖼️ 결과 갤러리                                            │
│ ┌───┐ ┌───┐ ┌───┐ ┌───┐                                │
│ │ 1 │ │ 2 │ │ 3 │ │ 4 │                                │
│ └───┘ └───┘ └───┘ └───┘                                │
└─────────────────────────────────────────────────────────┘
```

## 🔧 구현 세부사항

### 1. 이미지 선택 및 미리보기
```python
class ImageVariationTab:
    def __init__(self, parent):
        self.parent = parent
        self.selected_image = None
        self.create_image_selection_area()
    
    def create_image_selection_area(self):
        """이미지 선택 및 미리보기 영역 생성"""
        # 이미지 선택 버튼
        self.select_button = ttk.Button(
            self.parent, 
            text="이미지 선택",
            command=self.select_image
        )
        
        # 미리보기 라벨
        self.preview_label = ttk.Label(
            self.parent,
            text="이미지를 선택하세요",
            relief="sunken",
            width=40, height=20
        )
    
    def select_image(self):
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
            self.selected_image = filepath
            self.update_preview(filepath)
    
    def update_preview(self, filepath):
        """이미지 미리보기 업데이트"""
        try:
            # PIL로 이미지 로드 및 리사이즈
            img = Image.open(filepath)
            img.thumbnail((300, 200), Image.Resampling.LANCZOS)
            
            # Tkinter PhotoImage로 변환
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # 참조 유지
            
        except Exception as e:
            messagebox.showerror("오류", f"이미지 로드 실패: {e}")
```

### 2. 변형 설정 UI
```python
def create_variation_settings(self):
    """변형 설정 UI 생성"""
    settings_frame = ttk.LabelFrame(self.parent, text="변형 설정")
    
    # 변형 개수 설정
    ttk.Label(settings_frame, text="변형 개수:").grid(row=0, column=0)
    self.count_var = tk.IntVar(value=5)
    count_spinbox = ttk.Spinbox(
        settings_frame, 
        from_=1, to=20, 
        textvariable=self.count_var,
        width=10
    )
    count_spinbox.grid(row=0, column=1)
    
    # 변형 타입 선택
    ttk.Label(settings_frame, text="변형 타입:").grid(row=1, column=0)
    self.type_var = tk.StringVar(value="random")
    type_combo = ttk.Combobox(
        settings_frame,
        textvariable=self.type_var,
        values=["랜덤 변형", "객체 재배치", "객체 추가", "객체 제거", "스타일 변경"],
        state="readonly"
    )
    type_combo.grid(row=1, column=1)
    
    # 출력 폴더 설정
    ttk.Label(settings_frame, text="출력 폴더:").grid(row=2, column=0)
    self.output_var = tk.StringVar()
    ttk.Entry(settings_frame, textvariable=self.output_var, width=30).grid(row=2, column=1)
    ttk.Button(settings_frame, text="찾아보기", command=self.select_output_folder).grid(row=2, column=2)
```

### 3. 스타일 옵션 체크박스
```python
def create_style_options(self):
    """스타일 옵션 체크박스 생성"""
    options_frame = ttk.LabelFrame(self.parent, text="스타일 옵션")
    
    self.style_options = {
        'rearrange': tk.BooleanVar(),
        'add': tk.BooleanVar(),
        'remove': tk.BooleanVar(),
        'style': tk.BooleanVar(),
        'composition': tk.BooleanVar()
    }
    
    option_texts = {
        'rearrange': '객체 재배치',
        'add': '객체 추가',
        'remove': '객체 제거',
        'style': '스타일 변경',
        'composition': '구도 변경'
    }
    
    for i, (key, var) in enumerate(self.style_options.items()):
        ttk.Checkbutton(
            options_frame,
            text=option_texts[key],
            variable=var
        ).grid(row=i//3, column=i%3, padx=10, pady=5, sticky='w')
```

### 4. 진행률 표시
```python
def create_progress_area(self):
    """진행률 표시 영역 생성"""
    progress_frame = ttk.Frame(self.parent)
    
    # 진행률 바
    self.progress_var = tk.DoubleVar()
    self.progress_bar = ttk.Progressbar(
        progress_frame,
        variable=self.progress_var,
        maximum=100,
        length=400
    )
    self.progress_bar.pack(fill='x', pady=5)
    
    # 진행률 텍스트
    self.progress_text = tk.StringVar(value="대기 중...")
    ttk.Label(progress_frame, textvariable=self.progress_text).pack()
    
    return progress_frame

def update_progress(self, current, total, message=""):
    """진행률 업데이트"""
    percentage = (current / total) * 100
    self.progress_var.set(percentage)
    self.progress_text.set(f"{message} ({current}/{total} 완료)")
    self.root.update_idletasks()
```

### 5. 결과 갤러리
```python
def create_result_gallery(self):
    """결과 갤러리 생성"""
    gallery_frame = ttk.LabelFrame(self.parent, text="결과 갤러리")
    
    # 스크롤 가능한 프레임
    canvas = tk.Canvas(gallery_frame, height=200)
    scrollbar = ttk.Scrollbar(gallery_frame, orient="horizontal", command=canvas.xview)
    scrollable_frame = ttk.Frame(canvas)
    
    canvas.configure(xscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    canvas.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="bottom", fill="x")
    
    self.gallery_frame = scrollable_frame
    return gallery_frame

def add_result_to_gallery(self, image_path, index):
    """갤러리에 결과 이미지 추가"""
    try:
        # 썸네일 생성
        img = Image.open(image_path)
        img.thumbnail((120, 120), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # 이미지 버튼 생성 (클릭 시 전체 크기로 보기)
        btn = ttk.Button(
            self.gallery_frame,
            image=photo,
            command=lambda: self.view_full_image(image_path)
        )
        btn.image = photo  # 참조 유지
        btn.grid(row=0, column=index, padx=5, pady=5)
        
        # 인덱스 라벨
        ttk.Label(self.gallery_frame, text=f"{index+1}").grid(row=1, column=index)
        
    except Exception as e:
        self.logger.error(f"갤러리 이미지 추가 실패: {e}")

def view_full_image(self, image_path):
    """전체 크기 이미지 뷰어 창 열기"""
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
```

## 🔧 이벤트 처리

### 1. 변형 생성 시작
```python
def start_variation_generation(self):
    """변형 생성 시작"""
    if not self.validate_inputs():
        return
    
    # UI 상태 변경
    self.set_processing_state(True)
    
    # 백그라운드 스레드에서 처리
    self.processing_thread = threading.Thread(
        target=self.process_variations,
        daemon=True
    )
    self.processing_thread.start()

def process_variations(self):
    """백그라운드에서 변형 처리"""
    try:
        processor = ImageVariationProcessor(
            api_key=self.api_key.get(),
            model="gemini-2.5-flash-image-preview"
        )
        
        results = processor.generate_variations(
            image_path=Path(self.selected_image),
            count=self.count_var.get(),
            variation_type=self.get_variation_type(),
            output_dir=Path(self.output_var.get()),
            progress_callback=self.update_progress,
            result_callback=self.add_result_to_gallery
        )
        
        # 완료 후 UI 업데이트
        self.root.after(0, lambda: self.on_processing_complete(results))
        
    except Exception as e:
        self.root.after(0, lambda: self.on_processing_error(str(e)))
```

## 🎨 UI/UX 고려사항

### 1. 사용자 경험
- 직관적인 워크플로우: 이미지 선택 → 설정 → 생성 → 결과 확인
- 실시간 피드백: 진행률 표시 및 중간 결과 미리보기
- 에러 처리: 명확한 에러 메시지 및 해결 방안 제시

### 2. 성능 최적화
- 백그라운드 처리로 UI 블로킹 방지
- 이미지 썸네일 생성으로 메모리 사용량 최적화
- 결과 갤러리 스크롤 최적화

### 3. 접근성
- 키보드 네비게이션 지원
- 툴팁 및 도움말 제공
- 다국어 지원 (한국어 기본)

## ✅ 완료 기준
- [ ] 이미지 변형 탭 UI 구현 완료
- [ ] 이미지 선택 및 미리보기 기능 동작
- [ ] 변형 설정 UI 정상 작동
- [ ] 진행률 표시 및 결과 갤러리 구현
- [ ] 백그라운드 처리 및 스레드 안전성 확보
- [ ] 에러 처리 및 사용자 피드백 구현

## 🔄 다음 단계
Phase 3에서는 CLI 인터페이스에도 동일한 변형 기능을 추가하여 자동화 및 스크립팅을 지원합니다.