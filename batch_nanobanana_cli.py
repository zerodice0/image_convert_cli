#!/usr/bin/env python3
"""
Batch NanoBanana Image Generator - CLI Application
Generate images using Google's Gemini API with batch processing capabilities
Designed for Linux terminal environments
"""

import argparse
import os
import sys
import getpass
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import signal
from concurrent.futures import ProcessPoolExecutor, as_completed

# Third-party imports
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    from io import BytesIO
    from tqdm import tqdm
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("📦 Install with: pip install google-genai Pillow tqdm rich")
    sys.exit(1)

# Local imports
try:
    from batch_nanobanana_core import ImageVariationProcessor
except ImportError as e:
    print(f"❌ Missing core module: {e}")
    print("💡 Make sure batch_nanobanana_core.py is in the same directory")
    sys.exit(1)


class BatchNanoBananaCLI:
    """Command-line interface for batch image generation"""
    
    def __init__(self):
        self.console = Console()
        self.is_processing = False
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
        
        # Signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown"""
        self.console.print("\n🛑 [yellow]Processing interrupted by user[/yellow]")
        self.is_processing = False
        if signum == signal.SIGINT:
            sys.exit(0)
    
    def setup_logging(self, log_file: Optional[str] = None, verbose: bool = False):
        """Setup logging configuration"""
        level = logging.DEBUG if verbose else logging.INFO
        
        handlers = [RichHandler(console=self.console, rich_tracebacks=True)]
        
        if log_file:
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        self.logger = logging.getLogger(__name__)
    
    def get_api_key(self, args) -> str:
        """Get API key from various sources with priority order"""
        
        # Priority 1: Command-line argument (with security warning)
        if args.api_key:
            self.console.print("⚠️ [yellow]WARNING: API key provided via command line is visible in process list[/yellow]")
            self.console.print("💡 [cyan]Consider using environment variable GEMINI_API_KEY instead[/cyan]")
            return args.api_key
        
        # Priority 2: Environment variable
        env_key = os.getenv('GEMINI_API_KEY')
        if env_key:
            self.console.print("✅ [green]Using API key from environment variable[/green]")
            return env_key
        
        # Priority 3: Config file
        if args.config and os.path.exists(args.config):
            try:
                with open(args.config, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('GEMINI_API_KEY='):
                            api_key = line.split('=', 1)[1]
                            self.console.print(f"✅ [green]Using API key from config file: {args.config}[/green]")
                            return api_key
            except Exception as e:
                self.logger.warning(f"Error reading config file {args.config}: {e}")
        
        # Priority 4: Interactive prompt (if not in dry-run mode)
        if hasattr(args, 'dry_run') and args.dry_run:
            self.console.print("🧪 [yellow]Dry-run mode: using dummy API key[/yellow]")
            return "dummy-api-key-for-dry-run"
        
        self.console.print("🔑 [yellow]API key not found in environment or config file[/yellow]")
        
        try:
            api_key = getpass.getpass("Enter your Gemini API key (input hidden): ")
            
            if not api_key.strip():
                self.console.print("❌ [red]API key is required to proceed[/red]")
                sys.exit(1)
            
            return api_key.strip()
        except (EOFError, KeyboardInterrupt):
            self.console.print("\n❌ [red]API key input cancelled or not available[/red]")
            self.console.print("💡 [cyan]Try setting GEMINI_API_KEY environment variable or use --config option[/cyan]")
            sys.exit(1)
    
    def validate_paths(self, input_dir: str, output_dir: str) -> tuple[Path, Path]:
        """Validate and prepare input/output directories"""
        
        # Validate input directory
        input_path = Path(input_dir).expanduser().resolve()
        if not input_path.exists():
            self.console.print(f"❌ [red]Input directory does not exist: {input_path}[/red]")
            sys.exit(1)
        
        if not input_path.is_dir():
            self.console.print(f"❌ [red]Input path is not a directory: {input_path}[/red]")
            sys.exit(1)
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir).expanduser().resolve()
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self.console.print(f"❌ [red]Permission denied creating output directory: {output_path}[/red]")
            sys.exit(1)
        except Exception as e:
            self.console.print(f"❌ [red]Error creating output directory: {e}[/red]")
            sys.exit(1)
        
        return input_path, output_path
    
    def get_image_files(self, input_path: Path) -> List[Path]:
        """Get list of supported image files from input directory"""
        image_files = []
        
        for file_path in input_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        
        return sorted(image_files)
    
    def process_images(self, image_files: List[Path], output_path: Path, 
                      prompt: str, api_key: str, dry_run: bool = False,
                      output_format: str = "png", concurrent: int = 1) -> dict:
        """Process all images in the list"""
        
        if dry_run:
            self.console.print("🧪 [yellow]DRY RUN MODE - No actual processing will occur[/yellow]")
            for image_file in image_files:
                output_filename = f"{image_file.stem}_generated.{output_format}"
                self.console.print(f"Would process: {image_file.name} → {output_filename}")
            return {"successful": len(image_files), "failed": 0, "skipped": 0}
        
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=api_key)
            
            results = {"successful": 0, "failed": 0, "skipped": 0}
            
            # Process with progress bar
            with tqdm(total=len(image_files), desc="Processing images", 
                     unit="image", colour="green") as pbar:
                
                for image_file in image_files:
                    if not self.is_processing:
                        self.logger.info("Processing interrupted by user")
                        break
                    
                    pbar.set_description(f"Processing {image_file.name}")
                    
                    try:
                        # Check if output file already exists
                        output_filename = f"{image_file.stem}_generated.{output_format}"
                        output_file_path = output_path / output_filename
                        
                        if output_file_path.exists():
                            self.logger.warning(f"Output file exists, skipping: {output_filename}")
                            results["skipped"] += 1
                            pbar.update(1)
                            continue
                        
                        # Load and process image
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
                                    generated_image.save(output_file_path)
                                    self.logger.info(f"Generated: {output_filename}")
                                    results["successful"] += 1
                                    output_saved = True
                                    break
                            
                            if not output_saved:
                                self.logger.error(f"No image generated for: {image_file.name}")
                                results["failed"] += 1
                    
                    except Exception as e:
                        self.logger.error(f"Error processing {image_file.name}: {str(e)}")
                        results["failed"] += 1
                    
                    pbar.update(1)
            
            return results
            
        except Exception as e:
            self.console.print(f"❌ [red]Fatal error: {str(e)}[/red]")
            return {"successful": 0, "failed": len(image_files), "skipped": 0}
    
    def run(self, args):
        """Main execution method"""
        self.is_processing = True
        
        # Setup logging
        self.setup_logging(args.log_file, args.verbose)
        
        # Route to appropriate mode handler
        if args.variation:
            return self.run_variation_mode(args)
        elif args.batch_variation:
            return self.run_batch_variation_mode(args)
        else:
            return self.run_batch_mode(args)  # 기존 기능
    
    def run_batch_mode(self, args):
        """기존 배치 처리 모드"""
        # Display header
        self.console.print(Panel.fit("🍌 Batch NanoBanana Image Generator", 
                                   style="bold green"))
        
        # Get API key
        api_key = self.get_api_key(args)
        
        # Validate paths
        input_path, output_path = self.validate_paths(args.input_dir, args.output_dir)
        
        # Get image files
        image_files = self.get_image_files(input_path)
        
        if not image_files:
            self.console.print(f"❌ [red]No supported image files found in: {input_path}[/red]")
            self.console.print(f"Supported formats: {', '.join(self.supported_formats)}")
            sys.exit(1)
        
        # Display processing info
        self.console.print(f"📁 Input: {input_path}")
        self.console.print(f"📁 Output: {output_path}")
        self.console.print(f"🖼️  Found {len(image_files)} images")
        self.console.print(f"💬 Prompt: [cyan]{args.prompt}[/cyan]")
        
        if args.dry_run:
            self.console.print("🧪 [yellow]DRY RUN MODE[/yellow]")
        
        # Confirm processing (unless quiet mode)
        if not args.quiet and not args.dry_run:
            if not Confirm.ask(f"Process {len(image_files)} images?"):
                self.console.print("Operation cancelled by user")
                sys.exit(0)
        
        # Process images
        start_time = datetime.now()
        results = self.process_images(
            image_files=image_files,
            output_path=output_path,
            prompt=args.prompt,
            api_key=api_key,
            dry_run=args.dry_run,
            output_format=args.format,
            concurrent=args.concurrent
        )
        end_time = datetime.now()
        
        # Display results
        duration = end_time - start_time
        self.console.print("\n" + "="*50)
        self.console.print(f"✅ [green]Processing completed in {duration}[/green]")
        self.console.print(f"📊 Results:")
        self.console.print(f"  • Successful: {results['successful']}")
        self.console.print(f"  • Failed: {results['failed']}")
        self.console.print(f"  • Skipped: {results['skipped']}")
        
        # Exit with appropriate code
        exit_code = 0 if results['failed'] == 0 else 1
        sys.exit(exit_code)
    
    def run_variation_mode(self, args):
        """이미지 변형 생성 모드 (단일 또는 다중 이미지)"""
        self.console.print("🎨 [bold cyan]이미지 변형 생성 모드[/bold cyan]")
        
        # 입력 검증
        if not self.validate_variation_inputs(args):
            return 1
        
        # 변형 프로세서 초기화
        processor = ImageVariationProcessor(
            api_key=self.get_api_key(args),
            model="gemini-2.5-flash-image-preview"
        )
        
        # 단일 이미지 vs 다중 이미지 모드 버릘며
        if args.image:
            # 단일 이미지 변형
            self.console.print(f"[cyan]단일 이미지 변형:[/cyan] {args.image}")
            results = self.process_single_image_variations(processor, args)
            self.print_variation_results(results)
            return 0 if results['successful'] > 0 else 1
        else:
            # 다중 이미지 변형 (디렉토리)
            input_path = Path(args.input_dir)
            output_path = Path(args.output_dir)
            
            self.console.print(f"[cyan]다중 이미지 변형:[/cyan] {input_path}")
            
            # 이미지 파일 가져오기
            image_files = self.get_image_files_with_extensions(input_path, args.extensions)
            self.console.print(f"[green]처리할 이미지 수:[/green] {len(image_files)}개")
            
            # 다중 이미지 변형 처리
            results = self.process_multiple_image_variations(processor, args, image_files, output_path)
            self.print_multi_variation_results(results)
            return 0 if results['total_successful'] > 0 else 1
    
    def run_batch_variation_mode(self, args):
        """배치 변형 생성 모드"""
        self.console.print("📦 [bold magenta]배치 변형 생성 모드[/bold magenta]")
        
        # 이미지 파일 검색
        input_path, output_path = self.validate_paths(args.input_dir, args.output_dir)
        image_files = self.get_image_files(input_path)
        
        if not image_files:
            self.console.print("❌ [red]처리할 이미지가 없습니다[/red]")
            return 1
        
        # 배치 변형 처리
        results = self.process_batch_variations(args, image_files, output_path)
        
        # 최종 리포트
        self.print_batch_variation_summary(results)
        return 0 if results['total_successful'] > 0 else 1
    
    # =========================
    # 변형 생성 지원 메서드
    # =========================
    
    def validate_variation_inputs(self, args) -> bool:
        """변형 모드 입력 검증"""
        errors = []
        
        # 입력 소스 검증 (이미지 또는 디렉토리 중 하나는 필요)
        if not args.image and not args.input_dir:
            errors.append("--image 또는 --input-dir 옵션 중 하나가 필요합니다")
        elif args.image and args.input_dir:
            errors.append("--image와 --input-dir 옵션은 동시에 사용할 수 없습니다")
        
        # 단일 이미지 검증
        if args.image:
            if not Path(args.image).exists():
                errors.append(f"이미지 파일이 존재하지 않습니다: {args.image}")
            elif not self.is_supported_image_format(args.image):
                errors.append(f"지원되지 않는 이미지 형식: {args.image}")
        
        # 디렉토리 검증
        if args.input_dir:
            input_path = Path(args.input_dir)
            if not input_path.exists():
                errors.append(f"입력 디렉토리가 존재하지 않습니다: {args.input_dir}")
            elif not input_path.is_dir():
                errors.append(f"입력 경로가 디렉토리가 아닙니다: {args.input_dir}")
            else:
                # 지원되는 이미지 파일이 있는지 확인
                image_files = self.get_image_files_with_extensions(input_path, args.extensions)
                if not image_files:
                    errors.append(f"입력 디렉토리에 지원되는 이미지 파일이 없습니다: {args.input_dir}")
        
        # 변형 개수 검증
        if args.count < 1 or args.count > 50:
            errors.append("변형 개수는 1~50 사이여야 합니다")
        
        # 출력 디렉토리 검증
        if not args.output_dir:
            errors.append("--output-dir 옵션이 필요합니다")
        
        # 품질 임계값 검증
        if not 0.0 <= args.quality_threshold <= 1.0:
            errors.append("품질 임계값은 0.0~1.0 사이여야 합니다")
        
        if errors:
            for error in errors:
                self.console.print(f"❌ [red]{error}[/red]")
            return False
        
        return True
    
    def is_supported_image_format(self, filepath: str) -> bool:
        """이미지 포맷 지원 여부 확인"""
        return Path(filepath).suffix.lower() in self.supported_formats
    
    def process_single_image_variations(self, processor: ImageVariationProcessor, args) -> Dict[str, Any]:
        """단일 이미지의 여러 변형 생성"""
        image_path = Path(args.image)
        output_dir = Path(args.output_dir)
        
        results = {
            'successful': 0,
            'failed': 0,
            'total': args.count,
            'variations': []
        }
        
        self.console.print(f"🖼️ 처리 이미지: [bold]{image_path.name}[/bold]")
        self.console.print(f"📊 생성할 변형: [bold]{args.count}[/bold]개")
        
        # 진행률 바 생성
        with tqdm(total=args.count, desc="변형 생성", unit="개") as pbar:
            for i in range(args.count):
                if not self.is_processing:
                    break
                
                try:
                    # 변형 생성
                    variation_result = processor.generate_single_variation(
                        image_path=image_path,
                        variation_id=i,
                        variation_type=args.variation_type,
                        output_dir=output_dir,
                        seed=args.seed + i if args.seed else None
                    )
                    
                    if variation_result['success']:
                        results['successful'] += 1
                        results['variations'].append(variation_result)
                        pbar.set_postfix(성공=results['successful'])
                    else:
                        results['failed'] += 1
                        self.console.print(f"⚠️ 변형 {i+1} 생성 실패: {variation_result['error']}")
                    
                    pbar.update(1)
                    
                except Exception as e:
                    results['failed'] += 1
                    self.console.print(f"❌ 변형 {i+1} 처리 오류: {e}")
                    pbar.update(1)
        
        return results
    
    def process_batch_variations(self, args, image_files: List[Path], output_path: Path) -> Dict[str, Any]:
        """배치 변형 처리"""
        total_images = len(image_files)
        total_variations = total_images * args.count_per_image
        
        results = {
            'total_images': total_images,
            'total_variations': total_variations,
            'total_successful': 0,
            'total_failed': 0,
            'image_results': []
        }
        
        self.console.print(f"📊 처리할 이미지: [bold]{total_images}[/bold]장")
        self.console.print(f"🎨 총 생성할 변형: [bold]{total_variations}[/bold]개")
        
        # 병렬 처리 설정
        max_workers = min(args.parallel or 1, total_images)
        
        if max_workers > 1:
            self.console.print(f"⚡ 병렬 처리: [bold]{max_workers}[/bold]개 워커")
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 각 이미지에 대해 변형 작업 제출
                future_to_image = {}
                
                for image_path in image_files:
                    future = executor.submit(
                        process_image_variations_worker,
                        str(image_path),
                        args.count_per_image,
                        str(output_path),
                        args.variation_type,
                        args.styles,
                        args.seed,
                        self.get_api_key(args)
                    )
                    future_to_image[future] = image_path
                
                # 결과 수집 (진행률 표시와 함께)
                with tqdm(total=total_images, desc="이미지 처리", unit="장") as pbar:
                    for future in as_completed(future_to_image):
                        image_path = future_to_image[future]
                        try:
                            image_result = future.result()
                            results['image_results'].append(image_result)
                            results['total_successful'] += image_result['successful']
                            results['total_failed'] += image_result['failed']
                            
                            pbar.set_postfix(
                                성공=results['total_successful'],
                                실패=results['total_failed']
                            )
                            
                        except Exception as e:
                            self.console.print(f"❌ {image_path.name} 처리 실패: {e}")
                            results['total_failed'] += args.count_per_image
                        
                        pbar.update(1)
        else:
            # 순차 처리
            with tqdm(total=total_images, desc="이미지 처리", unit="장") as pbar:
                for image_path in image_files:
                    if not self.is_processing:
                        break
                    
                    try:
                        image_result = self.process_single_image_variations_sync(
                            image_path, args, output_path
                        )
                        results['image_results'].append(image_result)
                        results['total_successful'] += image_result['successful']
                        results['total_failed'] += image_result['failed']
                        
                        pbar.set_postfix(
                            성공=results['total_successful'],
                            실패=results['total_failed']
                        )
                    except Exception as e:
                        self.console.print(f"❌ {image_path.name} 처리 실패: {e}")
                        results['total_failed'] += args.count_per_image
                    
                    pbar.update(1)
        
        return results
    
    def process_single_image_variations_sync(self, image_path: Path, args, output_path: Path) -> Dict[str, Any]:
        """단일 이미지 변형 생성 (동기 처리용)"""
        try:
            processor = ImageVariationProcessor(
                api_key=self.get_api_key(args),
                model="gemini-2.5-flash-image-preview"
            )
            
            # 출력 디렉토리 설정
            image_name = image_path.stem
            image_output_dir = output_path / f"{image_name}_variations"
            image_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 변형 생성
            results = processor.generate_variations(
                image_path=image_path,
                count=args.count_per_image,
                variation_type=args.variation_type,
                output_dir=image_output_dir,
                seed=args.seed
            )
            
            return {
                'image_path': str(image_path),
                'successful': results['successful'],
                'failed': results['failed'],
                'output_dir': str(image_output_dir)
            }
            
        except Exception as e:
            return {
                'image_path': str(image_path),
                'successful': 0,
                'failed': args.count_per_image,
                'error': str(e)
            }
    
    def parse_styles(self, styles_str: str) -> Optional[List[str]]:
        """스타일 문자열 파싱"""
        if not styles_str:
            return None
        
        valid_styles = {
            'rearrange': 'object_rearrange',
            'add': 'object_add',
            'remove': 'object_remove',
            'style': 'style_change',
            'composition': 'composition'
        }
        
        styles = [s.strip().lower() for s in styles_str.split(',')]
        invalid_styles = [s for s in styles if s not in valid_styles]
        
        if invalid_styles:
            self.console.print(f"⚠️ [yellow]유효하지 않은 스타일: {', '.join(invalid_styles)}[/yellow]")
            self.console.print(f"💡 사용 가능한 스타일: {', '.join(valid_styles.keys())}")
        
        return [valid_styles[s] for s in styles if s in valid_styles]
    
    def print_variation_results(self, results: Dict[str, Any]):
        """변형 생성 결과 출력"""
        self.console.print("\n" + "="*60)
        self.console.print("📊 [bold]변형 생성 결과[/bold]")
        self.console.print("="*60)
        
        success_rate = (results['successful'] / results['total']) * 100
        
        self.console.print(f"✅ 성공: [bold green]{results['successful']}[/bold green]개")
        self.console.print(f"❌ 실패: [bold red]{results['failed']}[/bold red]개")
        self.console.print(f"📈 성공률: [bold]{success_rate:.1f}%[/bold]")
        
        if results['variations']:
            self.console.print("\n🖼️ [bold]생성된 변형들:[/bold]")
            for i, var in enumerate(results['variations']):
                if 'output_file' in var:
                    self.console.print(f"  {i+1:2d}. {Path(var['output_file']).name}")
        
        self.console.print("="*60)
    
    def get_image_files_with_extensions(self, input_path: Path, extensions: str) -> List[Path]:
        """지정된 확장자의 이미지 파일들을 가져오기"""
        ext_list = [ext.strip().lower() for ext in extensions.split(',')]
        image_files = []
        
        for ext in ext_list:
            # 점이 없으면 추가
            if not ext.startswith('.'):
                ext = '.' + ext
            
            # glob 패턴으로 파일 검색
            pattern = f"*{ext}"
            files = list(input_path.glob(pattern))
            files.extend(list(input_path.glob(pattern.upper())))  # 대문자도 검색
            image_files.extend(files)
        
        # 중복 제거 및 정렬
        return sorted(list(set(image_files)))
    
    def process_multiple_image_variations(self, processor: ImageVariationProcessor, 
                                        args, image_files: List[Path], 
                                        output_path: Path) -> Dict[str, Any]:
        """다중 이미지 변형 처리"""
        results = {
            'total_images': len(image_files),
            'total_variations': len(image_files) * args.count,
            'total_successful': 0,
            'total_failed': 0,
            'image_results': []
        }
        
        # 출력 디렉토리 생성
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Progress bar 설정
        desc = "다중 이미지 변형 생성"
        progress_bar = tqdm(
            total=len(image_files),
            desc=desc,
            unit="image",
            dynamic_ncols=True
        )
        
        try:
            for i, image_file in enumerate(image_files, 1):
                progress_bar.set_description(f"{desc} ({image_file.name})")
                
                try:
                    # 각 이미지별 출력 디렉토리
                    image_output_dir = output_path / f"{image_file.stem}_variations"
                    
                    # 단일 이미지 변형 처리
                    image_result = self.process_single_image_variations_for_multi(
                        processor, args, image_file, image_output_dir
                    )
                    
                    results['image_results'].append({
                        'image_name': image_file.name,
                        'successful': image_result['successful'],
                        'failed': image_result['failed'],
                        'output_dir': str(image_output_dir)
                    })
                    
                    results['total_successful'] += image_result['successful']
                    results['total_failed'] += image_result['failed']
                    
                except Exception as e:
                    print(f"❌ {image_file.name} 처리 중 오류: {str(e)}")
                    results['image_results'].append({
                        'image_name': image_file.name,
                        'successful': 0,
                        'failed': args.count,
                        'error': str(e)
                    })
                    results['total_failed'] += args.count
                
                progress_bar.update(1)
        
        finally:
            progress_bar.close()
        
        return results
    
    def process_single_image_variations_for_multi(self, processor: ImageVariationProcessor,
                                                 args, image_path: Path, 
                                                 output_dir: Path) -> Dict[str, Any]:
        """다중 처리용 단일 이미지 변형 (progress bar 없음)"""
        # 출력 디렉토리 생성
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 변형 생성
        try:
            # Use enhanced version if available, otherwise basic version
            if hasattr(processor, 'generate_variations_enhanced') and args.styles:
                results = processor.generate_variations_enhanced(
                    image_path=image_path,
                    count=args.count,
                    variation_type=args.variation_type,
                    styles=args.styles.split(',') if args.styles else None,
                    output_dir=output_dir,
                    seed=args.seed
                )
            else:
                results = processor.generate_variations(
                    image_path=image_path,
                    count=args.count,
                    variation_type=args.variation_type,
                    output_dir=output_dir,
                    seed=args.seed
                )
            return results
        except Exception as e:
            return {
                'successful': 0,
                'failed': args.count,
                'error': str(e),
                'variations': []
            }
    
    def print_multi_variation_results(self, results: Dict[str, Any]):
        """다중 이미지 변형 결과 출력"""
        print("\n" + "="*70)
        print("📦 다중 이미지 변형 생성 결과")
        print("="*70)
        
        success_rate = 0
        if results['total_variations'] > 0:
            success_rate = (results['total_successful'] / results['total_variations']) * 100
        
        print(f"🖼️ 처리된 이미지: {results['total_images']}장")
        print(f"🎨 총 변형 수: {results['total_variations']}개")
        print(f"✅ 성공: {results['total_successful']}개")
        print(f"❌ 실패: {results['total_failed']}개")
        print(f"📈 전체 성공률: {success_rate:.1f}%")
        
        # 이미지별 상세 결과
        if results['image_results']:
            print(f"\n📋 이미지별 결과 상위 10개:")
            for i, img_result in enumerate(results['image_results'][:10], 1):
                status = "✅" if img_result['successful'] > 0 else "❌"
                if 'error' in img_result:
                    print(f"  {i:2d}. {status} {img_result['image_name']} - 오류: {img_result['error'][:50]}...")
                else:
                    print(f"  {i:2d}. {status} {img_result['image_name']} - 성공: {img_result['successful']}, 실패: {img_result['failed']}")
            
            if len(results['image_results']) > 10:
                remaining = len(results['image_results']) - 10
                print(f"     ... 및 {remaining}개 추가 이미지")
        
        print("="*70)
    
    def print_batch_variation_summary(self, results: Dict[str, Any]):
        """배치 변형 결과 요약"""
        self.console.print("\n" + "="*70)
        self.console.print("📦 [bold]배치 변형 생성 요약[/bold]")
        self.console.print("="*70)
        
        success_rate = (results['total_successful'] / results['total_variations']) * 100
        
        self.console.print(f"🖼️ 처리된 이미지: [bold]{results['total_images']}[/bold]장")
        self.console.print(f"🎨 총 변형 수: [bold]{results['total_variations']}[/bold]개")
        self.console.print(f"✅ 성공: [bold green]{results['total_successful']}[/bold green]개")
        self.console.print(f"❌ 실패: [bold red]{results['total_failed']}[/bold red]개")
        self.console.print(f"📈 전체 성공률: [bold]{success_rate:.1f}%[/bold]")
        
        # 이미지별 상세 결과
        if results['image_results']:
            self.console.print(f"\n📋 [bold]이미지별 결과:[/bold]")
            for result in results['image_results']:
                image_name = Path(result['image_path']).name
                success = result['successful']
                failed = result['failed']
                total = success + failed
                rate = (success / total * 100) if total > 0 else 0
                
                self.console.print(f"  📁 {image_name}: {success}/{total} ({rate:.0f}%)")
        
        self.console.print("="*70)


# =========================
# 워커 프로세스 함수
# =========================

def process_image_variations_worker(image_path: str, count: int, output_dir: str, 
                                  variation_type: str, styles: str, seed: int, api_key: str) -> Dict[str, Any]:
    """병렬 처리를 위한 워커 함수"""
    try:
        # 새 프로세서 인스턴스 생성 (프로세스 안전성)
        processor = ImageVariationProcessor(
            api_key=api_key,
            model="gemini-2.5-flash-image-preview"
        )
        
        # 출력 디렉토리 설정
        image_name = Path(image_path).stem
        image_output_dir = Path(output_dir) / f"{image_name}_variations"
        image_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 스타일 파싱
        parsed_styles = None
        if styles:
            valid_styles = {
                'rearrange': 'object_rearrange',
                'add': 'object_add',
                'remove': 'object_remove', 
                'style': 'style_change',
                'composition': 'composition'
            }
            style_list = [s.strip().lower() for s in styles.split(',')]
            parsed_styles = [valid_styles[s] for s in style_list if s in valid_styles]
        
        # 변형 생성
        results = processor.generate_variations(
            image_path=Path(image_path),
            count=count,
            variation_type=variation_type,
            output_dir=image_output_dir,
            seed=seed
        )
        
        return {
            'image_path': image_path,
            'successful': results['successful'],
            'failed': results['failed'],
            'output_dir': str(image_output_dir)
        }
        
    except Exception as e:
        return {
            'image_path': image_path,
            'successful': 0,
            'failed': count,
            'error': str(e)
        }


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="NanoBanana 이미지 생성 도구 - 배치 처리 및 변형 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  # 기존 배치 처리 모드
  %(prog)s --batch --input-dir ./images --output-dir ./results --prompt "Transform this image"
  
  # 단일 이미지 변형 생성
  %(prog)s --variation --image photo.jpg --count 5 --output-dir variations
  
  # 여러 이미지 변형 생성 (새로운 기능!)
  %(prog)s --variation --input-dir ./photos --count 5 --output-dir variations
  
  # 특정 스타일로 변형 생성
  %(prog)s --variation --image photo.jpg --styles rearrange,add --count 3 --output-dir variations
  
  # 배치 변형 (각 이미지당 여러 변형)
  %(prog)s --batch-variation --input-dir photos --count-per-image 2 --output-dir variations
  
  # 고급 변형 옵션
  %(prog)s --variation --input-dir portraits --styles "rearrange,add,style" --count 8 --seed 42 --quality-threshold 0.8
        """
    )
    
    # 모드 선택 (상호 배타적)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--batch', action='store_true',
                           help='배치 처리 모드 (기존 기능)')
    mode_group.add_argument('--variation', action='store_true',
                           help='이미지 변형 생성 모드 (단일 또는 다중 이미지)')
    mode_group.add_argument('--batch-variation', action='store_true',
                           help='배치 변형 모드 (각 이미지당 여러 변형)')
    
    # 기존 배치 모드 전용 옵션
    batch_group = parser.add_argument_group('배치 처리 옵션 (--batch 모드에서만 사용)')
    batch_group.add_argument("--prompt", "-p",
                           help="API로 전송할 텍스트 프롬프트")
    batch_group.add_argument("--concurrent", type=int, default=1,
                           help="동시 처리 스레드 수 (기본값: 1)")
    
    # 변형 모드 전용 옵션
    variation_group = parser.add_argument_group('변형 생성 옵션')
    
    # 입력 소스 (둘 중 하나만 사용)
    input_group = variation_group.add_mutually_exclusive_group()
    input_group.add_argument('--image', type=str,
                            help='변형할 단일 이미지 파일 경로')
    input_group.add_argument('--input-dir', '-i', type=str,
                            help='변형할 이미지들이 있는 디렉토리 경로')
    
    variation_group.add_argument('--count', type=int, default=5,
                                help='생성할 변형 개수 (단일 이미지) 또는 이미지당 변형 개수 (다중 이미지) (기본값: 5)')
    variation_group.add_argument('--count-per-image', type=int, default=3,
                                help='배치 변형 시 이미지당 변형 개수 (기본값: 3)')
    variation_group.add_argument('--variation-type', 
                                choices=['random', 'object_rearrange', 'object_add', 'object_remove', 'style_change', 'composition'],
                                default='random',
                                help='변형 타입 선택 (기본값: random)')
    variation_group.add_argument('--styles', type=str,
                                help='적용할 스타일 목록 (콤마 구분: rearrange,add,remove,style,composition)')
    variation_group.add_argument('--seed', type=int,
                                help='변형 생성 시드 (재현 가능한 결과)')
    variation_group.add_argument('--quality-threshold', type=float, default=0.7,
                                help='변형 품질 임계값 (0.0-1.0, 기본값: 0.7)')
    variation_group.add_argument('--max-attempts', type=int, default=3,
                                help='변형 생성 최대 시도 횟수 (기본값: 3)')
    variation_group.add_argument('--parallel', type=int, default=1,
                                help='배치 변형 시 병렬 처리 수 (기본값: 1)')
    variation_group.add_argument('--extensions', type=str, default='jpg,jpeg,png,webp',
                                help='처리할 이미지 확장자 (콤마 구분, 기본값: jpg,jpeg,png,webp)')
    
    # 공통 옵션
    parser.add_argument("--output-dir", "-o", required=True,
                       help="출력 디렉토리 경로")
    parser.add_argument("--api-key",
                       help="Gemini API 키 (환경변수 GEMINI_API_KEY 사용 권장)")
    parser.add_argument("--config", "-c",
                       help="API 키가 포함된 설정 파일 경로")
    parser.add_argument("--format", "-f", default="png",
                       choices=["png", "jpg", "jpeg", "webp"],
                       help="출력 이미지 형식 (기본값: png)")
    parser.add_argument("--dry-run", action="store_true",
                       help="실제 처리 없이 처리 대상만 표시")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="상세 출력 활성화")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="확인 프롬프트 억제")
    parser.add_argument("--log-file", "-l",
                       help="로그 파일 경로 (기본값: 콘솔에만 로그)")
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.quiet and args.verbose:
        print("Error: --quiet and --verbose cannot be used together")
        sys.exit(1)
    
    # Mode-specific validation
    if args.batch:
        if not args.input_dir:
            print("Error: --batch mode requires --input-dir")
            sys.exit(1)
        if not args.prompt:
            print("Error: --batch mode requires --prompt")
            sys.exit(1)
    elif args.variation:
        if not args.image and not args.input_dir:
            print("Error: --variation mode requires either --image or --input-dir")
            sys.exit(1)
        if args.image and args.input_dir:
            print("Error: --variation mode cannot use both --image and --input-dir")
            sys.exit(1)
    elif args.batch_variation:
        if not args.input_dir:
            print("Error: --batch-variation mode requires --input-dir")
            sys.exit(1)
    
    # Create and run CLI application
    cli = BatchNanoBananaCLI()
    cli.run(args)


if __name__ == "__main__":
    main()