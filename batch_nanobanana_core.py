#!/usr/bin/env python3
"""
Batch NanoBanana Core - Shared Processing Logic
Core image processing functionality shared between GUI and CLI versions
"""

import os
import random
import json
from pathlib import Path
from typing import List, Optional, Dict, Callable, Union, Any
import logging
from datetime import datetime
from io import BytesIO

# Third-party imports
try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Missing required package: {e}. Install with: pip install google-genai Pillow")


class ImageProcessor:
    """Core image processing functionality"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image-preview"):
        """
        Initialize image processor
        
        Args:
            api_key: Google Gemini API key
            model: Gemini model to use for generation
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
        self.logger = logging.getLogger(__name__)
        
        # Initialize client
        self._init_client()
    
    def _init_client(self):
        """Initialize Gemini client"""
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info("Gemini client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def validate_image_file(self, file_path: Path) -> bool:
        """
        Validate if file is a supported image format
        
        Args:
            file_path: Path to image file
            
        Returns:
            bool: True if file is supported image format
        """
        if not file_path.is_file():
            return False
        
        if file_path.suffix.lower() not in self.supported_formats:
            return False
        
        try:
            with Image.open(file_path) as img:
                # Try to load image to verify it's valid
                img.verify()
            return True
        except Exception:
            return False
    
    def get_image_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """
        Get list of supported image files from directory
        
        Args:
            directory: Directory to search for images
            recursive: Whether to search recursively in subdirectories
            
        Returns:
            List of Path objects for valid image files
        """
        image_files = []
        
        if recursive:
            pattern = "**/*"
            files = directory.glob(pattern)
        else:
            files = directory.iterdir()
        
        for file_path in files:
            if self.validate_image_file(file_path):
                image_files.append(file_path)
        
        return sorted(image_files)
    
    def process_single_image(self, image_path: Path, prompt: str, 
                           output_path: Path, output_format: str = "png") -> Dict[str, any]:
        """
        Process a single image
        
        Args:
            image_path: Path to input image
            prompt: Text prompt for generation
            output_path: Path for output image
            output_format: Format for output image
            
        Returns:
            Dict with processing result information
        """
        result = {
            "success": False,
            "input_file": str(image_path),
            "output_file": str(output_path),
            "error": None,
            "processing_time": None
        }
        
        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Processing image: {image_path}")
            
            # Load image
            with Image.open(image_path) as img:
                # Generate content using Gemini
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt, img],
                )
                
                # Process response
                output_saved = False
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        generated_image = Image.open(BytesIO(part.inline_data.data))
                        
                        # Ensure output directory exists
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Save generated image
                        generated_image.save(output_path)
                        result["success"] = True
                        result["processing_time"] = (datetime.now() - start_time).total_seconds()
                        output_saved = True
                        
                        self.logger.info(f"Successfully processed: {image_path.name}")
                        break
                
                if not output_saved:
                    result["error"] = "No image data in response"
                    self.logger.warning(f"No image generated for: {image_path.name}")
        
        except Exception as e:
            result["error"] = str(e)
            result["processing_time"] = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Error processing {image_path.name}: {e}")
        
        return result
    
    def process_batch(self, image_files: List[Path], prompt: str, 
                     output_dir: Path, output_format: str = "png",
                     name_template: str = "{stem}_generated.{ext}",
                     progress_callback: Optional[Callable] = None,
                     error_callback: Optional[Callable] = None,
                     stop_check: Optional[Callable] = None) -> Dict[str, any]:
        """
        Process multiple images in batch
        
        Args:
            image_files: List of image file paths to process
            prompt: Text prompt for generation
            output_dir: Directory for output images
            output_format: Format for output images
            name_template: Template for output filenames
            progress_callback: Optional callback for progress updates
            error_callback: Optional callback for error handling
            stop_check: Optional callback to check if processing should stop
            
        Returns:
            Dict with batch processing results
        """
        results = {
            "total": len(image_files),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None,
            "details": []
        }
        
        self.logger.info(f"Starting batch processing of {len(image_files)} images")
        
        for i, image_file in enumerate(image_files):
            # Check if processing should stop
            if stop_check and stop_check():
                self.logger.info("Batch processing stopped by user request")
                break
            
            # Generate output filename
            output_filename = name_template.format(
                stem=image_file.stem,
                name=image_file.name,
                ext=output_format
            )
            output_path = output_dir / output_filename
            
            # Skip if output file already exists
            if output_path.exists():
                results["skipped"] += 1
                self.logger.warning(f"Output file exists, skipping: {output_filename}")
                if progress_callback:
                    progress_callback(i + 1, len(image_files), f"Skipped: {image_file.name}")
                continue
            
            # Process single image
            if progress_callback:
                progress_callback(i + 1, len(image_files), f"Processing: {image_file.name}")
            
            result = self.process_single_image(
                image_path=image_file,
                prompt=prompt,
                output_path=output_path,
                output_format=output_format
            )
            
            results["details"].append(result)
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                if error_callback:
                    error_callback(image_file, result["error"])
        
        # Finalize results
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        self.logger.info(
            f"Batch processing completed: {results['successful']} successful, "
            f"{results['failed']} failed, {results['skipped']} skipped in "
            f"{results['duration']:.2f} seconds"
        )
        
        return results


class ConfigManager:
    """Configuration management for batch processing"""
    
    @staticmethod
    def load_config_file(config_path: Path) -> Dict[str, str]:
        """
        Load configuration from file
        
        Args:
            config_path: Path to config file
            
        Returns:
            Dict with configuration values
        """
        config = {}
        
        if not config_path.exists():
            return config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
                    else:
                        logging.warning(f"Invalid config line {line_num}: {line}")
        
        except Exception as e:
            logging.error(f"Error reading config file {config_path}: {e}")
        
        return config
    
    @staticmethod
    def save_config_file(config_path: Path, config: Dict[str, str], 
                        mode: int = 0o600):
        """
        Save configuration to file with secure permissions
        
        Args:
            config_path: Path to config file
            config: Configuration dict to save
            mode: File permissions (default: 0o600 - owner read/write only)
        """
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write config file
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("# Batch NanoBanana Configuration\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                
                for key, value in config.items():
                    f.write(f"{key}={value}\n")
            
            # Set secure permissions
            os.chmod(config_path, mode)
            
        except Exception as e:
            logging.error(f"Error saving config file {config_path}: {e}")
            raise


class BatchValidator:
    """Validation utilities for batch processing"""
    
    @staticmethod
    def validate_directories(input_dir: str, output_dir: str) -> tuple[Path, Path]:
        """
        Validate and prepare input/output directories
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            
        Returns:
            Tuple of (input_path, output_path) as Path objects
            
        Raises:
            ValueError: If validation fails
        """
        # Validate input directory
        input_path = Path(input_dir).expanduser().resolve()
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_path}")
        
        if not input_path.is_dir():
            raise ValueError(f"Input path is not a directory: {input_path}")
        
        # Check read permissions
        if not os.access(input_path, os.R_OK):
            raise ValueError(f"No read permission for input directory: {input_path}")
        
        # Prepare output directory
        output_path = Path(output_dir).expanduser().resolve()
        
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise ValueError(f"Permission denied creating output directory: {output_path}")
        except Exception as e:
            raise ValueError(f"Error creating output directory: {e}")
        
        # Check write permissions
        if not os.access(output_path, os.W_OK):
            raise ValueError(f"No write permission for output directory: {output_path}")
        
        return input_path, output_path
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Basic validation of API key format
        
        Args:
            api_key: API key to validate
            
        Returns:
            bool: True if key appears valid
        """
        if not api_key or not api_key.strip():
            return False
        
        # Basic length and format check
        key = api_key.strip()
        if len(key) < 10:  # Minimum reasonable length
            return False
        
        # Check for common placeholder values
        invalid_keys = {'your-api-key', 'api-key-here', 'test', 'demo', 'example'}
        if key.lower() in invalid_keys:
            return False
        
        return True
    
    @staticmethod
    def validate_prompt(prompt: str) -> bool:
        """
        Validate prompt text
        
        Args:
            prompt: Prompt text to validate
            
        Returns:
            bool: True if prompt is valid
        """
        if not prompt or not prompt.strip():
            return False
        
        # Check minimum length
        if len(prompt.strip()) < 3:
            return False
        
        return True


class VariationPromptGenerator:
    """변형 프롬프트 생성 전문 클래스"""
    
    def __init__(self):
        """프롬프트 생성기 초기화"""
        self.object_templates = self._load_object_templates()
        self.style_templates = self._load_style_templates()
        self.composition_templates = self._load_composition_templates()
        self.logger = logging.getLogger(__name__)
    
    def _load_object_templates(self) -> Dict[str, List[str]]:
        """객체 조작 템플릿 로드"""
        return {
            'object_rearrange': [
                "Rearrange the objects in this image: move the {object1} to the {position1} and place the {object2} {position2}",
                "Reorganize the composition by repositioning the {object1} and {object2} while keeping the same style",
                "Change the layout by moving {object1} to {direction} and adjusting other elements accordingly",
                "Reposition the elements in this scene to create a different but natural composition",
                "Alter the spatial arrangement of objects while maintaining visual balance"
            ],
            'object_add': [
                "Add a {new_object} to this scene in a natural way that fits the composition",
                "Include additional {object_type} elements to enhance the scene",
                "Insert {count} {objects} into the image while maintaining the original atmosphere",
                "Enhance this image by adding complementary objects or elements",
                "Introduce new elements that would naturally belong in this setting"
            ],
            'object_remove': [
                "Remove the {target_object} from this image and fill the space naturally",
                "Take out {object_list} while preserving the overall composition",
                "Clean up the image by removing {unwanted_elements}",
                "Simplify this scene by removing some elements while keeping it natural",
                "Edit out certain objects to create a cleaner composition"
            ]
        }
    
    def _load_style_templates(self) -> Dict[str, List[str]]:
        """스타일 변형 템플릿 로드"""
        return {
            'style_change': [
                "Transform this image into a {art_style} artistic style while keeping the same composition",
                "Recreate this scene in a {mood} and {color_palette} aesthetic",
                "Apply a {artistic_technique} treatment to this image",
                "Convert this to a {style_period} art style interpretation",
                "Reimagine this scene with a {visual_style} approach"
            ],
            'lighting_change': [
                "Change the lighting in this scene to {time_of_day} lighting",
                "Apply {lighting_type} lighting effects to create a different mood",
                "Modify the lighting to be more {lighting_quality}",
                "Transform the illumination to create a {mood} atmosphere"
            ]
        }
    
    def _load_composition_templates(self) -> Dict[str, List[str]]:
        """구도 변형 템플릿 로드"""
        return {
            'composition': [
                "Change the camera angle to a {angle_type} perspective of this scene",
                "Reframe this image with a {framing_type} composition",
                "Alter the viewpoint to show this scene from a {perspective} angle",
                "Modify the framing to emphasize {focus_element} in the composition",
                "Adjust the perspective to create a more {composition_style} arrangement"
            ],
            'crop_reframe': [
                "Reframe this image to focus more on {subject}",
                "Change the aspect ratio and composition to {format} format",
                "Zoom in/out to create a different compositional emphasis",
                "Adjust the framing to highlight different elements"
            ]
        }
    
    def _get_random_objects(self) -> List[str]:
        """일반적인 객체 목록"""
        return [
            'car', 'person', 'tree', 'building', 'cloud', 'mountain', 'flower', 'animal',
            'bird', 'cat', 'dog', 'chair', 'table', 'window', 'door', 'sign', 'light',
            'shadow', 'reflection', 'path', 'road', 'bridge', 'water', 'grass', 'rock'
        ]
    
    def _get_random_positions(self) -> List[str]:
        """위치 관련 표현"""
        return [
            'left side', 'right side', 'center', 'background', 'foreground',
            'top area', 'bottom area', 'corner', 'edge', 'middle distance'
        ]
    
    def _get_random_directions(self) -> List[str]:
        """방향 관련 표현"""
        return [
            'left', 'right', 'up', 'down', 'forward', 'backward',
            'closer', 'further away', 'to the side', 'diagonally'
        ]
    
    def _get_art_styles(self) -> List[str]:
        """예술 스타일 목록"""
        return [
            'impressionist', 'abstract', 'minimalist', 'vintage', 'modern',
            'watercolor', 'oil painting', 'sketch', 'digital art', 'photorealistic',
            'surreal', 'pop art', 'cubist', 'expressionist'
        ]
    
    def _get_lighting_types(self) -> List[str]:
        """조명 타입 목록"""
        return [
            'golden hour', 'blue hour', 'dramatic', 'soft', 'harsh',
            'backlit', 'side-lit', 'natural', 'artificial', 'moody'
        ]
    
    def generate_prompt(self, variation_type: str, seed: Optional[int] = None) -> str:
        """
        변형 타입과 시드에 따른 프롬프트 생성
        
        Args:
            variation_type: 변형 타입 ('random', 'object_rearrange', 'object_add', 
                           'object_remove', 'style_change', 'composition')
            seed: 재현 가능한 결과를 위한 시드값
            
        Returns:
            str: 생성된 프롬프트
        """
        if seed is not None:
            random.seed(seed)
        
        try:
            if variation_type == 'random':
                # 랜덤하게 다른 타입 중 하나 선택
                available_types = ['object_rearrange', 'object_add', 'object_remove', 
                                 'style_change', 'composition']
                variation_type = random.choice(available_types)
            
            if variation_type == 'object_rearrange':
                template = random.choice(self.object_templates['object_rearrange'])
                return template.format(
                    object1=random.choice(self._get_random_objects()),
                    object2=random.choice(self._get_random_objects()),
                    position1=random.choice(self._get_random_positions()),
                    position2=random.choice(self._get_random_positions()),
                    direction=random.choice(self._get_random_directions())
                )
            
            elif variation_type == 'object_add':
                template = random.choice(self.object_templates['object_add'])
                objects = self._get_random_objects()
                return template.format(
                    new_object=random.choice(objects),
                    object_type=random.choice(['decorative', 'functional', 'natural']),
                    count=random.choice(['one', 'two', 'several']),
                    objects=random.choice(objects)
                )
            
            elif variation_type == 'object_remove':
                template = random.choice(self.object_templates['object_remove'])
                objects = self._get_random_objects()
                return template.format(
                    target_object=random.choice(objects),
                    object_list=', '.join(random.sample(objects, 2)),
                    unwanted_elements=random.choice(['background elements', 'distracting objects'])
                )
            
            elif variation_type == 'style_change':
                template = random.choice(self.style_templates['style_change'])
                return template.format(
                    art_style=random.choice(self._get_art_styles()),
                    mood=random.choice(['dreamy', 'dramatic', 'serene', 'vibrant', 'mysterious']),
                    color_palette=random.choice(['warm', 'cool', 'monochromatic', 'vibrant']),
                    artistic_technique=random.choice(['painterly', 'sketchy', 'detailed']),
                    style_period=random.choice(['Renaissance', 'Baroque', 'Impressionist', 'Modern']),
                    visual_style=random.choice(['cinematic', 'documentary', 'artistic'])
                )
            
            elif variation_type == 'composition':
                template = random.choice(self.composition_templates['composition'])
                return template.format(
                    angle_type=random.choice(['low', 'high', 'bird\'s eye', 'worm\'s eye']),
                    framing_type=random.choice(['tight', 'wide', 'medium', 'close-up']),
                    perspective=random.choice(['different', 'unique', 'interesting']),
                    focus_element=random.choice(['the main subject', 'background elements']),
                    composition_style=random.choice(['dynamic', 'balanced', 'asymmetric'])
                )
            
            else:
                # 기본 일반적인 변형 프롬프트
                return "Create an interesting variation of this image with different elements or composition"
                
        except Exception as e:
            self.logger.error(f"프롬프트 생성 중 오류: {e}")
            return "Create a creative variation of this image"


class VariationEngine:
    """변형 로직의 핵심 엔진"""
    
    VARIATION_TYPES = {
        'random': '임의 변형',
        'object_rearrange': '객체 재배치',
        'object_add': '객체 추가',
        'object_remove': '객체 제거',
        'style_change': '스타일 변경',
        'composition': '구도 변경'
    }
    
    def __init__(self):
        """변형 엔진 초기화"""
        self.prompt_generator = VariationPromptGenerator()
        self.logger = logging.getLogger(__name__)
    
    def create_variation_prompt(self, base_image: Image.Image, variation_id: int, 
                              variation_type: str = "random", seed: Optional[int] = None) -> str:
        """
        변형별 고유 프롬프트 생성
        
        Args:
            base_image: 기본 이미지 (현재는 참조용)
            variation_id: 변형 식별자
            variation_type: 변형 타입
            seed: 시드값
            
        Returns:
            str: 생성된 프롬프트
        """
        try:
            # 변형 ID를 시드에 추가하여 각 변형마다 다른 결과 보장
            variation_seed = seed + variation_id if seed is not None else None
            
            # 프롬프트 생성
            prompt = self.prompt_generator.generate_prompt(variation_type, variation_seed)
            
            self.logger.debug(f"변형 {variation_id} ({variation_type}) 프롬프트 생성: {prompt[:50]}...")
            return prompt
            
        except Exception as e:
            self.logger.error(f"변형 프롬프트 생성 실패: {e}")
            return f"Create variation {variation_id} of this image with creative changes"
    
    def validate_variation_type(self, variation_type: str) -> bool:
        """변형 타입 유효성 검증"""
        return variation_type in self.VARIATION_TYPES
    
    def get_available_types(self) -> Dict[str, str]:
        """사용 가능한 변형 타입 반환"""
        return self.VARIATION_TYPES.copy()


class ImageVariationProcessor(ImageProcessor):
    """이미지 변형 생성을 위한 전문 프로세서"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image-preview"):
        """
        이미지 변형 프로세서 초기화
        
        Args:
            api_key: Google Gemini API 키
            model: 사용할 모델명
        """
        super().__init__(api_key, model)
        self.variation_engine = VariationEngine()
        self.logger = logging.getLogger(__name__)
    
    def generate_single_variation(self, image_path: Path, variation_id: int,
                                 variation_type: str = "random", 
                                 output_dir: Path = None,
                                 output_format: str = "png",
                                 seed: Optional[int] = None) -> Dict[str, Union[bool, str, Path, int]]:
        """
        단일 이미지 변형 생성
        
        Args:
            image_path: 원본 이미지 경로
            variation_id: 변형 식별자
            variation_type: 변형 타입
            output_dir: 출력 디렉토리
            output_format: 출력 형식
            seed: 시드값
            
        Returns:
            Dict: 변형 생성 결과
        """
        if not self.variation_engine.validate_variation_type(variation_type):
            return {
                "success": False,
                "error": f"지원하지 않는 변형 타입: {variation_type}",
                "variation_id": variation_id
            }
        
        try:
            # 출력 디렉토리 설정
            if output_dir is None:
                output_dir = image_path.parent
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 출력 파일명 생성
            output_filename = f"{image_path.stem}_variation_{variation_id:02d}.{output_format}"
            output_path = output_dir / output_filename
            
            # 이미지 로드
            with Image.open(image_path) as base_image:
                # 변형 프롬프트 생성
                variation_prompt = self.variation_engine.create_variation_prompt(
                    base_image, variation_id, variation_type, seed
                )
                
                # 변형 생성 (기존 process_single_image 활용)
                result = self.process_single_image(
                    image_path=image_path,
                    prompt=variation_prompt,
                    output_path=output_path,
                    output_format=output_format
                )
                
                # 결과에 변형 정보 추가
                result.update({
                    "variation_id": variation_id,
                    "variation_type": variation_type,
                    "variation_prompt": variation_prompt
                })
                
                return result
                
        except Exception as e:
            self.logger.error(f"변형 {variation_id} 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "variation_id": variation_id,
                "variation_type": variation_type
            }
    
    def generate_variations(self, image_path: Path, count: int,
                          variation_type: str = "random",
                          output_dir: Path = None,
                          output_format: str = "png",
                          name_template: str = "{stem}_variation_{id:02d}.{ext}",
                          seed: Optional[int] = None,
                          progress_callback: Optional[Callable] = None) -> Dict[str, Union[int, List, float]]:
        """
        이미지의 다양한 변형을 생성
        
        Args:
            image_path: 원본 이미지 경로
            count: 생성할 변형 개수
            variation_type: 변형 타입
            output_dir: 출력 디렉토리
            output_format: 출력 형식
            name_template: 파일명 템플릿
            seed: 시드값
            progress_callback: 진행률 콜백 함수
            
        Returns:
            Dict: 변형 생성 결과
        """
        if not self.validate_image_file(image_path):
            return {
                "successful": 0,
                "failed": 1,
                "total": count,
                "variations": [],
                "error": f"유효하지 않은 이미지 파일: {image_path}"
            }
        
        results = {
            "successful": 0,
            "failed": 0,
            "total": count,
            "variations": [],
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None
        }
        
        self.logger.info(f"변형 생성 시작: {image_path.name}, 개수: {count}, 타입: {variation_type}")
        
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = image_path.parent / f"{image_path.stem}_variations"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(count):
            if progress_callback:
                progress_callback(i + 1, count, f"변형 {i + 1} 생성 중...")
            
            # 각 변형에 대해 다른 시드 사용 (재현성 보장)
            variation_seed = seed + i if seed is not None else None
            
            # 변형 생성
            variation_result = self.generate_single_variation(
                image_path=image_path,
                variation_id=i + 1,
                variation_type=variation_type,
                output_dir=output_dir,
                output_format=output_format,
                seed=variation_seed
            )
            
            results["variations"].append(variation_result)
            
            if variation_result["success"]:
                results["successful"] += 1
                self.logger.info(f"변형 {i + 1} 생성 성공: {variation_result.get('output_file', 'Unknown')}")
            else:
                results["failed"] += 1
                self.logger.error(f"변형 {i + 1} 생성 실패: {variation_result.get('error', 'Unknown error')}")
        
        # 결과 정리
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        self.logger.info(
            f"변형 생성 완료: {results['successful']} 성공, "
            f"{results['failed']} 실패, {results['duration']:.2f}초 소요"
        )
        
        return results
    
    def process_single_variation(self, image_path: Path, variation_prompt: str, 
                               output_path: Path) -> Dict[str, Union[bool, str, float]]:
        """
        단일 변형 처리 (기존 시스템과의 호환성을 위한 래퍼)
        
        Args:
            image_path: 이미지 경로
            variation_prompt: 변형 프롬프트
            output_path: 출력 경로
            
        Returns:
            Dict: 처리 결과
        """
        return self.process_single_image(
            image_path=image_path,
            prompt=variation_prompt,
            output_path=output_path
        )
    
    def process_variation_batch(self, image_path: Path, count: int, 
                              output_dir: Path, variation_type: str = "random") -> Dict[str, Union[int, List]]:
        """
        변형 배치 처리 (기존 시스템과의 호환성을 위한 래퍼)
        
        Args:
            image_path: 이미지 경로
            count: 변형 개수
            output_dir: 출력 디렉토리
            variation_type: 변형 타입
            
        Returns:
            Dict: 처리 결과
        """
        return self.generate_variations(
            image_path=image_path,
            count=count,
            variation_type=variation_type,
            output_dir=output_dir
        )


# =======================================
# Phase 4: Enhanced Image Variation Processor
# =======================================

class EnhancedImageVariationProcessor(ImageVariationProcessor):
    """고급 기능이 통합된 이미지 변형 프로세서"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image-preview", 
                 enable_quality_analysis: bool = True, enable_caching: bool = True,
                 enable_duplication_prevention: bool = True):
        super().__init__(api_key, model)
        
        # 고급 기능 모듈들 (optional import)
        try:
            from variation_advanced import (
                VariationQualityAnalyzer, DuplicationPreventer,
                MemoryOptimizer, RetryManager, VariationCache, AdaptiveQualityManager
            )
            
            self.quality_analyzer = VariationQualityAnalyzer() if enable_quality_analysis else None
            self.duplication_preventer = DuplicationPreventer() if enable_duplication_prevention else None
            self.memory_optimizer = MemoryOptimizer()
            self.retry_manager = RetryManager()
            self.cache = VariationCache() if enable_caching else None
            self.quality_manager = AdaptiveQualityManager()
            
            self.advanced_features_enabled = True
            self.logger.info("고급 기능 모듈 로드 완료")
            
        except ImportError as e:
            self.logger.warning(f"고급 기능 모듈을 찾을 수 없음: {e}")
            self.logger.info("기본 모드로 동작합니다.")
            self.quality_analyzer = None
            self.duplication_preventer = None
            self.memory_optimizer = None
            self.retry_manager = None
            self.cache = None
            self.quality_manager = None
            self.advanced_features_enabled = False
    
    def generate_variations_enhanced(self, image_path: Path, count: int,
                                   variation_type: str = "random",
                                   output_dir: Path = None,
                                   seed: int = None,
                                   styles: List[str] = None,
                                   **kwargs) -> Dict[str, Any]:
        """고급 기능이 적용된 변형 생성"""
        
        if not self.advanced_features_enabled:
            # 고급 기능이 비활성화된 경우 기본 메서드 사용
            self.logger.info("기본 변형 생성 모드 사용")
            return self.generate_variations(
                image_path=image_path,
                count=count,
                variation_type=variation_type,
                output_dir=output_dir,
                seed=seed
            )
        
        try:
            return self._generate_variations_with_advanced_features(
                image_path, count, variation_type, output_dir, seed, styles, **kwargs
            )
        except Exception as e:
            self.logger.error(f"고급 변형 생성 실패, 기본 모드로 폴백: {e}")
            return self.generate_variations(
                image_path=image_path,
                count=count,
                variation_type=variation_type,
                output_dir=output_dir,
                seed=seed
            )
    
    def _generate_variations_with_advanced_features(self, image_path: Path, count: int,
                                                  variation_type: str, output_dir: Path, 
                                                  seed: int, styles: List[str], **kwargs) -> Dict[str, Any]:
        """고급 기능을 사용한 변형 생성 내부 로직"""
        
        # 캐시 확인
        cache_params = {
            'variation_type': variation_type,
            'count': count,
            'seed': seed,
            'styles': styles
        }
        
        if self.cache:
            cache_key = self.cache.generate_cache_key(image_path, '', cache_params)
            cached_result = self.cache.get_cached_result(cache_key)
            if cached_result:
                self.logger.info(f"캐시된 결과 사용: {cache_key}")
                return self._format_cached_result(cached_result)
        
        # 메모리 최적화
        original_image = Image.open(image_path)
        if self.memory_optimizer:
            optimized_image = self.memory_optimizer.optimize_image_size(original_image)
        else:
            optimized_image = original_image
        
        # 품질 설정 적용
        if self.quality_manager:
            quality_settings = self.quality_manager.get_current_settings()
        else:
            quality_settings = {
                'max_image_size': 2048,
                'quality_threshold': 0.6,
                'max_attempts_per_variation': 3
            }
        
        results = {
            'successful': 0,
            'failed': 0,
            'total': count,
            'variations': [],
            'quality_scores': []
        }
        
        # 중복 방지 시스템 초기화
        if self.duplication_preventer:
            self.duplication_preventer.clear()
        
        # 변형 생성 (품질 기반 재시도 포함)
        attempts = 0
        max_total_attempts = count * quality_settings['max_attempts_per_variation']
        
        while results['successful'] < count and attempts < max_total_attempts:
            try:
                self.logger.info(f"변형 생성 시도 {attempts + 1}/{max_total_attempts}")
                
                # 재시도 메커니즘으로 변형 생성
                if self.retry_manager:
                    variation_result = self.retry_manager.retry_with_backoff(
                        self._generate_single_variation_with_quality_check,
                        optimized_image,
                        attempts,
                        quality_settings,
                        image_path,
                        output_dir or Path.cwd(),
                        variation_type,
                        seed
                    )
                else:
                    variation_result = self._generate_single_variation_with_quality_check(
                        optimized_image, attempts, quality_settings,
                        image_path, output_dir or Path.cwd(), variation_type, seed
                    )
                
                if variation_result['success']:
                    results['successful'] += 1
                    results['variations'].append(variation_result)
                    if 'quality_metrics' in variation_result:
                        results['quality_scores'].append(variation_result['quality_metrics'])
                    
                    self.logger.info(f"변형 성공: {results['successful']}/{count}")
                else:
                    results['failed'] += 1
                    self.logger.warning(f"변형 실패: {variation_result.get('error', '알 수 없는 오류')}")
                
            except Exception as e:
                results['failed'] += 1
                self.logger.error(f"변형 생성 오류 (시도 {attempts + 1}): {e}")
            
            attempts += 1
        
        # 성능 기반 품질 조정
        if self.quality_manager:
            success_rate = results['successful'] / max(1, results['successful'] + results['failed'])
            self.quality_manager.adjust_quality_based_on_performance(success_rate)
        
        # 결과 캐싱
        if self.cache and results['variations']:
            result_paths = [Path(v['output_file']) for v in results['variations'] if 'output_file' in v]
            if result_paths:
                self.cache.cache_result(cache_key, result_paths, image_path, '', cache_params)
        
        return results
    
    def _generate_single_variation_with_quality_check(self, image: Image.Image, 
                                                     variation_id: int,
                                                     quality_settings: Dict,
                                                     image_path: Path,
                                                     output_dir: Path,
                                                     variation_type: str,
                                                     seed: int = None) -> Dict[str, Any]:
        """품질 검증이 포함된 단일 변형 생성"""
        
        try:
            # 기본 변형 생성 (기존 메서드 활용)
            temp_output_dir = output_dir / f"temp_{variation_id}"
            temp_output_dir.mkdir(exist_ok=True)
            
            variation_result = self.generate_single_variation(
                image_path=image_path,
                variation_id=variation_id,
                variation_type=variation_type,
                output_dir=temp_output_dir,
                seed=seed + variation_id if seed else None
            )
            
            if not variation_result['success']:
                return variation_result
            
            # 생성된 이미지 로드
            generated_image = Image.open(variation_result['output_file'])
            
            # 중복 검사
            if self.duplication_preventer and self.duplication_preventer.is_duplicate(generated_image):
                Path(variation_result['output_file']).unlink(missing_ok=True)
                return {
                    'success': False,
                    'error': '중복된 변형이 생성됨',
                    'quality_metrics': {}
                }
            
            # 품질 분석
            quality_metrics = {}
            if self.quality_analyzer:
                other_variations = []
                if self.duplication_preventer:
                    other_variations = self.duplication_preventer.generated_variations
                
                quality_metrics = self.quality_analyzer.analyze_variation_quality(
                    image, generated_image, other_variations
                )
                
                # 품질 기준 확인
                acceptable_quality = self.quality_analyzer.is_acceptable_quality(quality_metrics)
                meets_threshold = quality_metrics.get('overall_quality', 0) >= quality_settings['quality_threshold']
                
                if not (acceptable_quality and meets_threshold):
                    Path(variation_result['output_file']).unlink(missing_ok=True)
                    return {
                        'success': False,
                        'error': f"품질 기준 미달 (점수: {quality_metrics.get('overall_quality', 0):.2f})",
                        'quality_metrics': quality_metrics
                    }
            
            # 최종 위치로 이미지 이동
            final_output_path = output_dir / f"variation_{variation_id:03d}.png"
            shutil.move(variation_result['output_file'], final_output_path)
            temp_output_dir.rmdir()
            
            # 중복 방지 시스템에 등록
            if self.duplication_preventer:
                self.duplication_preventer.add_variation(generated_image)
            
            variation_result['output_file'] = str(final_output_path)
            variation_result['quality_metrics'] = quality_metrics
            
            return variation_result
            
        except Exception as e:
            self.logger.error(f"품질 검증 변형 생성 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'quality_metrics': {}
            }
    
    def _format_cached_result(self, cached_paths: List[Path]) -> Dict[str, Any]:
        """캐시된 결과를 표준 형식으로 포맷"""
        variations = []
        for i, path in enumerate(cached_paths):
            if path.exists():
                variations.append({
                    'success': True,
                    'output_file': str(path),
                    'variation_id': i,
                    'cached': True
                })
        
        return {
            'successful': len(variations),
            'failed': 0,
            'total': len(cached_paths),
            'variations': variations,
            'quality_scores': [],
            'from_cache': True
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        stats = {
            'advanced_features_enabled': self.advanced_features_enabled,
            'cache_enabled': self.cache is not None,
            'quality_analysis_enabled': self.quality_analyzer is not None,
            'duplication_prevention_enabled': self.duplication_preventer is not None
        }
        
        if self.quality_manager:
            stats['current_quality_level'] = self.quality_manager.current_quality_level
            stats['success_rate_history'] = self.quality_manager.success_rate_history[-10:]  # 최근 10개
        
        return stats