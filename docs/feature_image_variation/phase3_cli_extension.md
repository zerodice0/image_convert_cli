# Phase 3: CLI 인터페이스 확장

## 📋 개요
기존 CLI 애플리케이션에 이미지 변형 생성 기능을 추가하여, 명령줄에서 자동화 및 스크립팅을 통한 변형 생성을 지원하는 단계입니다.

## 🎯 목표
- 새로운 `--variation` 모드 추가
- 변형 관련 명령행 옵션 구현
- 배치 모드와 변형 모드의 통합
- CLI 도움말 및 예제 업데이트

## 💻 CLI 설계

### 1. 새로운 명령행 옵션
```bash
# 기본 변형 생성
python batch_nanobanana_cli.py --variation \
  --image photo.jpg \
  --count 5 \
  --output-dir ./variations

# 고급 변형 옵션
python batch_nanobanana_cli.py --variation \
  --image photo.jpg \
  --count 10 \
  --variation-type random \
  --styles rearrange,add,remove \
  --output-dir ./variations \
  --name-template "var_{index}_{timestamp}.png"

# 배치 + 변형 모드 (각 이미지당 n개 변형)
python batch_nanobanana_cli.py --batch-variation \
  --input-dir ./photos \
  --count-per-image 3 \
  --output-dir ./batch_variations \
  --parallel 2
```

### 2. 새로운 인수 그룹
```python
# batch_nanobanana_cli.py 인수 파서 확장
def setup_argument_parser():
    parser = argparse.ArgumentParser(
        description="NanoBanana 이미지 생성 도구 - 배치 처리 및 변형 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  # 단일 이미지 변형 생성
  %(prog)s --variation --image photo.jpg --count 5 --output-dir variations

  # 특정 스타일로 변형 생성
  %(prog)s --variation --image photo.jpg --styles rearrange,add --count 3

  # 배치 변형 (각 이미지당 여러 변형)
  %(prog)s --batch-variation --input-dir photos --count-per-image 2
        """
    )
    
    # 모드 선택 (상호 배타적)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--batch', action='store_true',
                           help='배치 처리 모드 (기존 기능)')
    mode_group.add_argument('--variation', action='store_true',
                           help='단일 이미지 변형 생성 모드')
    mode_group.add_argument('--batch-variation', action='store_true',
                           help='배치 변형 모드 (각 이미지당 여러 변형)')
    
    # 변형 모드 전용 옵션
    variation_group = parser.add_argument_group('변형 생성 옵션')
    variation_group.add_argument('--image', type=str,
                                help='변형할 단일 이미지 파일 경로')
    variation_group.add_argument('--count', type=int, default=5,
                                help='생성할 변형 개수 (기본값: 5)')
    variation_group.add_argument('--count-per-image', type=int, default=3,
                                help='배치 변형 시 이미지당 변형 개수 (기본값: 3)')
    variation_group.add_argument('--variation-type', 
                                choices=['random', 'rearrange', 'add', 'remove', 'style', 'composition'],
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
    
    return parser
```

## 🔧 구현 세부사항

### 1. 변형 모드 처리 로직
```python
class BatchNanoBananaCLI:
    def run(self, args):
        """메인 실행 함수"""
        if args.variation:
            return self.run_variation_mode(args)
        elif args.batch_variation:
            return self.run_batch_variation_mode(args)
        else:
            return self.run_batch_mode(args)  # 기존 기능
    
    def run_variation_mode(self, args):
        """단일 이미지 변형 생성 모드"""
        self.console.print("🎨 [bold cyan]이미지 변형 생성 모드[/bold cyan]")
        
        # 입력 검증
        if not self.validate_variation_inputs(args):
            return 1
        
        # 변형 프로세서 초기화
        processor = ImageVariationProcessor(
            api_key=self.get_api_key(args),
            model=args.model
        )
        
        # 변형 생성 실행
        results = self.process_single_image_variations(processor, args)
        
        # 결과 리포트
        self.print_variation_results(results)
        return 0 if results['successful'] > 0 else 1
    
    def run_batch_variation_mode(self, args):
        """배치 변형 생성 모드"""
        self.console.print("📦 [bold magenta]배치 변형 생성 모드[/bold magenta]")
        
        # 이미지 파일 검색
        image_files = self.get_image_files(args.input_dir, args.recursive)
        
        if not image_files:
            self.console.print("❌ [red]처리할 이미지가 없습니다[/red]")
            return 1
        
        # 배치 변형 처리
        results = self.process_batch_variations(args, image_files)
        
        # 최종 리포트
        self.print_batch_variation_summary(results)
        return 0 if results['total_successful'] > 0 else 1
```

### 2. 변형 생성 프로세스
```python
def process_single_image_variations(self, processor, args):
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
            if self.is_processing_stopped():
                break
            
            try:
                # 변형 생성
                variation_result = processor.generate_variation(
                    image_path=image_path,
                    variation_id=i,
                    variation_type=args.variation_type,
                    styles=self.parse_styles(args.styles),
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

def process_batch_variations(self, args, image_files):
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
    
    # 병렬 처리 설정
    max_workers = min(args.parallel or 1, total_images)
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 각 이미지에 대해 변형 작업 제출
        future_to_image = {}
        
        for image_path in image_files:
            future = executor.submit(
                self.process_image_variations_worker,
                str(image_path),
                args.count_per_image,
                args.output_dir,
                args.variation_type,
                args.styles,
                args.seed
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
    
    return results
```

### 3. 워커 프로세스 함수
```python
def process_image_variations_worker(image_path, count, output_dir, variation_type, styles, seed):
    """병렬 처리를 위한 워커 함수"""
    try:
        # 새 프로세서 인스턴스 생성 (프로세스 안전성)
        processor = ImageVariationProcessor(
            api_key=os.getenv('GEMINI_API_KEY'),
            model="gemini-2.5-flash-image-preview"
        )
        
        # 출력 디렉토리 설정
        image_name = Path(image_path).stem
        image_output_dir = Path(output_dir) / f"{image_name}_variations"
        image_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 변형 생성
        results = processor.generate_variations(
            image_path=Path(image_path),
            count=count,
            variation_type=variation_type,
            styles=parse_styles(styles) if styles else None,
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
```

## 🔧 고급 기능

### 1. 스타일 파싱 및 검증
```python
def parse_styles(self, styles_str):
    """스타일 문자열 파싱"""
    if not styles_str:
        return None
    
    valid_styles = {
        'rearrange': '객체 재배치',
        'add': '객체 추가',
        'remove': '객체 제거',
        'style': '스타일 변경',
        'composition': '구도 변경'
    }
    
    styles = [s.strip().lower() for s in styles_str.split(',')]
    invalid_styles = [s for s in styles if s not in valid_styles]
    
    if invalid_styles:
        self.console.print(f"⚠️ [yellow]유효하지 않은 스타일: {', '.join(invalid_styles)}[/yellow]")
        self.console.print(f"💡 사용 가능한 스타일: {', '.join(valid_styles.keys())}")
    
    return [s for s in styles if s in valid_styles]
```

### 2. 입력 검증
```python
def validate_variation_inputs(self, args):
    """변형 모드 입력 검증"""
    errors = []
    
    # 이미지 파일 검증
    if not args.image:
        errors.append("--image 옵션이 필요합니다")
    elif not Path(args.image).exists():
        errors.append(f"이미지 파일이 존재하지 않습니다: {args.image}")
    elif not self.is_supported_image_format(args.image):
        errors.append(f"지원되지 않는 이미지 형식: {args.image}")
    
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
```

### 3. 결과 리포팅
```python
def print_variation_results(self, results):
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
            self.console.print(f"  {i+1:2d}. {Path(var['output_file']).name}")
    
    self.console.print("="*60)

def print_batch_variation_summary(self, results):
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
```

## 🚀 사용 예제

### 1. 기본 변형 생성
```bash
# 5개 랜덤 변형 생성
python batch_nanobanana_cli.py --variation \
  --image family_photo.jpg \
  --count 5 \
  --output-dir family_variations

# 특정 스타일로 변형
python batch_nanobanana_cli.py --variation \
  --image landscape.jpg \
  --variation-type rearrange \
  --count 3 \
  --output-dir landscape_rearranged
```

### 2. 고급 옵션 사용
```bash
# 복합 스타일 적용
python batch_nanobanana_cli.py --variation \
  --image portrait.jpg \
  --styles "rearrange,add,style" \
  --count 8 \
  --seed 42 \
  --quality-threshold 0.8 \
  --output-dir portrait_variations

# 재현 가능한 결과 (시드 사용)
python batch_nanobanana_cli.py --variation \
  --image test.jpg \
  --seed 12345 \
  --count 3 \
  --output-dir reproducible_test
```

### 3. 배치 변형
```bash
# 각 이미지당 3개 변형
python batch_nanobanana_cli.py --batch-variation \
  --input-dir ./wedding_photos \
  --count-per-image 3 \
  --variation-type random \
  --output-dir ./wedding_variations \
  --parallel 2

# 대용량 배치 처리
python batch_nanobanana_cli.py --batch-variation \
  --input-dir ./product_catalog \
  --count-per-image 5 \
  --styles "style,composition" \
  --parallel 4 \
  --output-dir ./catalog_variations \
  --log-file batch_variation.log
```

## ✅ 완료 기준
- [ ] 새로운 변형 모드 명령행 옵션 구현
- [ ] 단일 이미지 변형 기능 동작 확인
- [ ] 배치 변형 기능 구현 및 테스트
- [ ] 병렬 처리 및 성능 최적화
- [ ] 입력 검증 및 에러 처리 완료
- [ ] 결과 리포팅 시스템 구현
- [ ] 도움말 및 예제 업데이트

## 🔄 다음 단계
Phase 4에서는 변형 품질 검증, 중복 방지, 성능 최적화 등 고급 기능을 구현합니다.