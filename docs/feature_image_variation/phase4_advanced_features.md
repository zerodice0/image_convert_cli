# Phase 4: 고급 기능 및 최적화

## 📋 개요
이미지 변형 생성 기능의 품질, 성능, 안정성을 향상시키는 고급 기능들을 구현하는 단계입니다.

## 🎯 목표
- 변형 품질 검증 시스템 구현
- 중복 결과 방지 알고리즘 개발
- 성능 최적화 및 메모리 관리
- 고급 오류 처리 및 복구 메커니즘

## 🔍 변형 품질 검증 시스템

### 1. 품질 메트릭 정의
```python
class VariationQualityAnalyzer:
    """변형 품질 분석 및 검증"""
    
    def __init__(self):
        self.quality_thresholds = {
            'similarity_min': 0.3,  # 원본과의 최소 유사도
            'similarity_max': 0.9,  # 원본과의 최대 유사도
            'diversity_min': 0.2,   # 다른 변형들과의 최소 차이
            'aesthetic_min': 0.6,   # 미적 품질 최소 기준
            'object_integrity': 0.7  # 객체 완전성 기준
        }
    
    def analyze_variation_quality(self, original_image: Image, 
                                variation_image: Image, 
                                other_variations: List[Image] = None) -> Dict[str, float]:
        """변형 품질 종합 분석"""
        metrics = {}
        
        # 1. 원본과의 유사도 분석
        metrics['similarity'] = self.calculate_similarity(original_image, variation_image)
        
        # 2. 다양성 분석 (다른 변형들과의 차이)
        if other_variations:
            metrics['diversity'] = self.calculate_diversity(variation_image, other_variations)
        
        # 3. 미적 품질 분석
        metrics['aesthetic'] = self.analyze_aesthetic_quality(variation_image)
        
        # 4. 객체 완전성 검증
        metrics['object_integrity'] = self.verify_object_integrity(variation_image)
        
        # 5. 전체 품질 점수 계산
        metrics['overall_quality'] = self.calculate_overall_quality(metrics)
        
        return metrics
    
    def calculate_similarity(self, img1: Image, img2: Image) -> float:
        """이미지 간 유사도 계산 (SSIM 기반)"""
        from skimage.metrics import structural_similarity as ssim
        import numpy as np
        
        # 이미지를 그레이스케일로 변환
        img1_gray = np.array(img1.convert('L'))
        img2_gray = np.array(img2.convert('L'))
        
        # 크기 통일
        if img1_gray.shape != img2_gray.shape:
            img2_resized = cv2.resize(img2_gray, img1_gray.shape[::-1])
        else:
            img2_resized = img2_gray
        
        # SSIM 계산
        similarity_score = ssim(img1_gray, img2_resized)
        return similarity_score
    
    def calculate_diversity(self, target_img: Image, other_imgs: List[Image]) -> float:
        """변형들 간 다양성 계산"""
        if not other_imgs:
            return 1.0
        
        # 각 이미지와의 차이 계산
        differences = []
        for other_img in other_imgs:
            similarity = self.calculate_similarity(target_img, other_img)
            differences.append(1.0 - similarity)  # 차이 = 1 - 유사도
        
        # 평균 차이도 반환
        return sum(differences) / len(differences)
    
    def analyze_aesthetic_quality(self, image: Image) -> float:
        """미적 품질 분석"""
        import numpy as np
        from PIL import ImageStat
        
        # 기본 이미지 통계
        stat = ImageStat.Stat(image)
        
        metrics = {}
        
        # 1. 색상 분산 (다채로운 색상 선호)
        color_variance = np.var([stat.var[i] for i in range(min(3, len(stat.var)))])
        metrics['color_variance'] = min(color_variance / 10000, 1.0)
        
        # 2. 대비 분석
        img_array = np.array(image.convert('L'))
        contrast = np.std(img_array) / 255.0
        metrics['contrast'] = min(contrast * 2, 1.0)
        
        # 3. 밝기 균형
        brightness = np.mean(img_array) / 255.0
        brightness_balance = 1.0 - abs(brightness - 0.5) * 2
        metrics['brightness_balance'] = brightness_balance
        
        # 4. 선명도 (Laplacian variance)
        laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
        sharpness = min(laplacian_var / 1000, 1.0)
        metrics['sharpness'] = sharpness
        
        # 종합 미적 점수
        weights = {
            'color_variance': 0.25,
            'contrast': 0.25,
            'brightness_balance': 0.25,
            'sharpness': 0.25
        }
        
        aesthetic_score = sum(metrics[key] * weights[key] for key in weights)
        return aesthetic_score
    
    def verify_object_integrity(self, image: Image) -> float:
        """객체 완전성 검증"""
        # 간단한 엣지 검출 기반 객체 완전성 확인
        import cv2
        import numpy as np
        
        img_array = np.array(image.convert('L'))
        
        # Canny 엣지 검출
        edges = cv2.Canny(img_array, 50, 150)
        
        # 연결된 컴포넌트 분석
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(edges)
        
        # 객체 완전성 점수 (연결된 영역의 크기와 개수 기반)
        if num_labels > 1:  # 배경 제외
            # 큰 연결 영역들의 비율
            areas = stats[1:, cv2.CC_STAT_AREA]  # 배경(라벨 0) 제외
            total_area = image.size[0] * image.size[1]
            large_areas = areas[areas > total_area * 0.01]  # 전체의 1% 이상
            integrity = min(len(large_areas) / 10, 1.0)
        else:
            integrity = 0.1  # 거의 엣지가 없는 경우
        
        return integrity
    
    def calculate_overall_quality(self, metrics: Dict[str, float]) -> float:
        """전체 품질 점수 계산"""
        weights = {
            'similarity': 0.2,      # 원본과의 적절한 유사성
            'diversity': 0.3,       # 다른 변형들과의 차별성
            'aesthetic': 0.3,       # 미적 품질
            'object_integrity': 0.2  # 객체 완전성
        }
        
        # 유사도는 적정 범위에 있을 때 높은 점수
        similarity_score = metrics.get('similarity', 0.5)
        if 0.3 <= similarity_score <= 0.9:
            similarity_weighted = 1.0 - abs(similarity_score - 0.6) / 0.3
        else:
            similarity_weighted = 0.1
        
        weighted_metrics = {
            'similarity': similarity_weighted,
            'diversity': metrics.get('diversity', 0.5),
            'aesthetic': metrics.get('aesthetic', 0.5),
            'object_integrity': metrics.get('object_integrity', 0.5)
        }
        
        overall = sum(weighted_metrics[key] * weights[key] for key in weights)
        return overall

    def is_acceptable_quality(self, metrics: Dict[str, float]) -> bool:
        """품질 기준 통과 여부 판단"""
        checks = [
            self.quality_thresholds['similarity_min'] <= metrics.get('similarity', 0) <= self.quality_thresholds['similarity_max'],
            metrics.get('diversity', 0) >= self.quality_thresholds['diversity_min'],
            metrics.get('aesthetic', 0) >= self.quality_thresholds['aesthetic_min'],
            metrics.get('object_integrity', 0) >= self.quality_thresholds['object_integrity'],
            metrics.get('overall_quality', 0) >= 0.6
        ]
        
        return all(checks)
```

### 2. 중복 결과 방지 시스템
```python
class DuplicationPreventer:
    """변형 중복 방지 시스템"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.similarity_threshold = similarity_threshold
        self.generated_variations = []
        self.image_hashes = set()
        
    def is_duplicate(self, new_image: Image) -> bool:
        """새 이미지가 기존 변형들과 중복인지 확인"""
        # 1. 이미지 해시 기반 빠른 중복 검사
        image_hash = self.calculate_image_hash(new_image)
        if image_hash in self.image_hashes:
            return True
        
        # 2. 구조적 유사도 기반 정밀 검사
        for existing_image in self.generated_variations:
            similarity = self.calculate_similarity(new_image, existing_image)
            if similarity > self.similarity_threshold:
                return True
        
        return False
    
    def calculate_image_hash(self, image: Image) -> str:
        """이미지의 지각적 해시 계산"""
        import imagehash
        
        # 여러 해시 알고리즘 조합 사용
        hash_methods = [
            imagehash.average_hash,
            imagehash.phash,
            imagehash.dhash
        ]
        
        hashes = []
        for hash_method in hash_methods:
            hash_value = hash_method(image)
            hashes.append(str(hash_value))
        
        # 조합된 해시
        combined_hash = "|".join(hashes)
        return combined_hash
    
    def add_variation(self, image: Image):
        """새로운 변형을 중복 방지 시스템에 등록"""
        if not self.is_duplicate(image):
            self.generated_variations.append(image.copy())
            self.image_hashes.add(self.calculate_image_hash(image))
            return True
        return False
    
    def clear(self):
        """등록된 변형들 초기화"""
        self.generated_variations.clear()
        self.image_hashes.clear()
```

## ⚡ 성능 최적화

### 1. 메모리 관리
```python
class MemoryOptimizer:
    """메모리 사용량 최적화"""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.current_memory_usage = 0
        
    def optimize_image_size(self, image: Image, max_dimension: int = 2048) -> Image:
        """이미지 크기 최적화"""
        width, height = image.size
        
        if max(width, height) > max_dimension:
            # 비례적 리사이즈
            if width > height:
                new_width = max_dimension
                new_height = int((height * max_dimension) / width)
            else:
                new_height = max_dimension
                new_width = int((width * max_dimension) / height)
            
            optimized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return optimized
        
        return image
    
    def manage_batch_memory(self, batch_size: int, image_sizes: List[tuple]) -> int:
        """배치 처리 시 메모리 기반 최적 배치 크기 계산"""
        # 평균 이미지 메모리 사용량 추정
        avg_pixels = sum(w * h for w, h in image_sizes) / len(image_sizes)
        estimated_mb_per_image = (avg_pixels * 3 * 4) / (1024 * 1024)  # RGB, float32
        
        # API 응답 이미지까지 고려한 메모리 사용량
        total_memory_per_batch = estimated_mb_per_image * batch_size * 2  # 원본 + 결과
        
        if total_memory_per_batch > self.max_memory_mb:
            optimal_batch_size = max(1, int(self.max_memory_mb / (estimated_mb_per_image * 2)))
            return optimal_batch_size
        
        return batch_size
    
    def cleanup_temp_files(self, temp_dir: Path):
        """임시 파일 정리"""
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
```

### 2. 캐싱 시스템
```python
class VariationCache:
    """변형 생성 결과 캐싱"""
    
    def __init__(self, cache_dir: Path = None, max_cache_size_gb: float = 1.0):
        self.cache_dir = cache_dir or Path.home() / '.nanobanana_cache' / 'variations'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size_gb = max_cache_size_gb
        self.cache_index = self.load_cache_index()
        
    def generate_cache_key(self, image_path: Path, prompt: str, variation_params: Dict) -> str:
        """캐시 키 생성"""
        import hashlib
        
        # 이미지 파일 해시
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        
        # 프롬프트 및 파라미터 해시
        param_str = f"{prompt}_{json.dumps(variation_params, sort_keys=True)}"
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        
        return f"{file_hash}_{param_hash}"
    
    def get_cached_result(self, cache_key: str) -> Optional[List[Path]]:
        """캐시된 결과 조회"""
        if cache_key in self.cache_index:
            cache_entry = self.cache_index[cache_key]
            result_paths = [Path(path) for path in cache_entry['results']]
            
            # 파일 존재 확인
            if all(path.exists() for path in result_paths):
                # 최근 사용 시간 업데이트
                cache_entry['last_used'] = datetime.now().isoformat()
                self.save_cache_index()
                return result_paths
            else:
                # 누락된 파일이 있으면 캐시 엔트리 제거
                del self.cache_index[cache_key]
                
        return None
    
    def cache_result(self, cache_key: str, result_paths: List[Path], 
                    original_image: Path, prompt: str, params: Dict):
        """결과를 캐시에 저장"""
        cache_subdir = self.cache_dir / cache_key
        cache_subdir.mkdir(exist_ok=True)
        
        cached_paths = []
        for i, result_path in enumerate(result_paths):
            if result_path.exists():
                cached_path = cache_subdir / f"variation_{i}{result_path.suffix}"
                shutil.copy2(result_path, cached_path)
                cached_paths.append(str(cached_path))
        
        # 캐시 인덱스 업데이트
        self.cache_index[cache_key] = {
            'results': cached_paths,
            'original_image': str(original_image),
            'prompt': prompt,
            'params': params,
            'created': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }
        
        self.save_cache_index()
        self.cleanup_old_cache()
    
    def cleanup_old_cache(self):
        """오래된 캐시 정리"""
        # 캐시 크기 확인
        total_size = sum(
            sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            for cache_dir in self.cache_dir.iterdir()
            if cache_dir.is_dir()
        ) / (1024**3)  # GB 변환
        
        if total_size > self.max_cache_size_gb:
            # 오래된 항목부터 제거
            sorted_entries = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]['last_used']
            )
            
            for cache_key, entry in sorted_entries:
                if total_size <= self.max_cache_size_gb * 0.8:  # 80%까지 줄이기
                    break
                    
                # 캐시 디렉토리 제거
                cache_subdir = self.cache_dir / cache_key
                if cache_subdir.exists():
                    shutil.rmtree(cache_subdir)
                
                # 인덱스에서 제거
                del self.cache_index[cache_key]
                
                # 제거된 크기 계산
                removed_size = sum(len(path) for path in entry['results']) / (1024**3)
                total_size -= removed_size
            
            self.save_cache_index()
```

## 🔧 고급 오류 처리

### 1. 재시도 메커니즘
```python
class RetryManager:
    """지능적 재시도 시스템"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        
    def retry_with_backoff(self, func, *args, **kwargs):
        """지수 백오프를 사용한 재시도"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # 재시도할 수 없는 오류 체크
                if self.is_non_retryable_error(e):
                    raise e
                
                if attempt < self.max_attempts - 1:
                    delay = self.base_delay * (2 ** attempt)  # 지수 백오프
                    time.sleep(delay)
                    
                    # 프롬프트 변형 시도
                    if 'prompt' in kwargs:
                        kwargs['prompt'] = self.modify_prompt_for_retry(
                            kwargs['prompt'], attempt + 1
                        )
        
        # 모든 재시도 실패
        raise last_exception
    
    def is_non_retryable_error(self, error: Exception) -> bool:
        """재시도하지 않을 오류 판단"""
        non_retryable_patterns = [
            'authentication failed',
            'invalid api key',
            'quota exceeded',
            'content policy violation'
        ]
        
        error_msg = str(error).lower()
        return any(pattern in error_msg for pattern in non_retryable_patterns)
    
    def modify_prompt_for_retry(self, original_prompt: str, attempt: int) -> str:
        """재시도 시 프롬프트 변형"""
        variations = [
            f"{original_prompt} (alternative interpretation)",
            f"Create a different version of: {original_prompt}",
            f"Generate an alternative approach to: {original_prompt}",
            f"Please try again with: {original_prompt}"
        ]
        
        if attempt - 1 < len(variations):
            return variations[attempt - 1]
        return original_prompt
```

### 2. 점진적 품질 조정
```python
class AdaptiveQualityManager:
    """점진적 품질 조정 시스템"""
    
    def __init__(self):
        self.success_rate_history = []
        self.current_quality_level = 'high'
        self.quality_settings = {
            'high': {
                'max_image_size': 2048,
                'quality_threshold': 0.8,
                'max_attempts_per_variation': 3
            },
            'medium': {
                'max_image_size': 1536,
                'quality_threshold': 0.6,
                'max_attempts_per_variation': 2
            },
            'low': {
                'max_image_size': 1024,
                'quality_threshold': 0.4,
                'max_attempts_per_variation': 1
            }
        }
    
    def adjust_quality_based_on_performance(self, success_rate: float):
        """성능 기반 품질 수준 조정"""
        self.success_rate_history.append(success_rate)
        
        # 최근 5회 평균 계산
        if len(self.success_rate_history) >= 5:
            recent_avg = sum(self.success_rate_history[-5:]) / 5
            
            # 품질 수준 조정
            if recent_avg < 0.5 and self.current_quality_level == 'high':
                self.current_quality_level = 'medium'
                logging.info("품질 수준을 중간으로 낮춤 (성능 개선을 위해)")
            elif recent_avg < 0.3 and self.current_quality_level == 'medium':
                self.current_quality_level = 'low'
                logging.info("품질 수준을 낮음으로 조정 (안정성 확보를 위해)")
            elif recent_avg > 0.8 and self.current_quality_level != 'high':
                self.current_quality_level = 'high'
                logging.info("성능이 좋아져 품질 수준을 높음으로 복원")
    
    def get_current_settings(self) -> Dict:
        """현재 품질 설정 반환"""
        return self.quality_settings[self.current_quality_level].copy()
```

## 🔗 ImageVariationProcessor 통합
```python
class EnhancedImageVariationProcessor(ImageVariationProcessor):
    """고급 기능이 통합된 이미지 변형 프로세서"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image-preview"):
        super().__init__(api_key, model)
        
        # 고급 기능 모듈들
        self.quality_analyzer = VariationQualityAnalyzer()
        self.duplication_preventer = DuplicationPreventer()
        self.memory_optimizer = MemoryOptimizer()
        self.retry_manager = RetryManager()
        self.cache = VariationCache()
        self.quality_manager = AdaptiveQualityManager()
    
    def generate_variations_enhanced(self, image_path: Path, count: int,
                                   **kwargs) -> Dict[str, any]:
        """고급 기능이 적용된 변형 생성"""
        # 캐시 확인
        cache_key = self.cache.generate_cache_key(
            image_path, kwargs.get('prompt', ''), kwargs
        )
        
        cached_result = self.cache.get_cached_result(cache_key)
        if cached_result:
            logging.info(f"캐시된 결과 사용: {cache_key}")
            return self.format_cached_result(cached_result)
        
        # 메모리 최적화
        original_image = Image.open(image_path)
        optimized_image = self.memory_optimizer.optimize_image_size(original_image)
        
        # 품질 설정 적용
        quality_settings = self.quality_manager.get_current_settings()
        
        results = {
            'successful': 0,
            'failed': 0,
            'variations': [],
            'quality_scores': []
        }
        
        # 중복 방지 시스템 초기화
        self.duplication_preventer.clear()
        
        # 변형 생성 (품질 기반 재시도 포함)
        attempts = 0
        while results['successful'] < count and attempts < count * quality_settings['max_attempts_per_variation']:
            try:
                # 재시도 메커니즘으로 변형 생성
                variation_result = self.retry_manager.retry_with_backoff(
                    self._generate_single_variation_with_quality_check,
                    optimized_image,
                    attempts,
                    quality_settings,
                    **kwargs
                )
                
                if variation_result['success']:
                    results['successful'] += 1
                    results['variations'].append(variation_result)
                    results['quality_scores'].append(variation_result['quality_metrics'])
                else:
                    results['failed'] += 1
                
            except Exception as e:
                results['failed'] += 1
                logging.error(f"변형 생성 실패 (시도 {attempts + 1}): {e}")
            
            attempts += 1
        
        # 성능 기반 품질 조정
        success_rate = results['successful'] / max(1, results['successful'] + results['failed'])
        self.quality_manager.adjust_quality_based_on_performance(success_rate)
        
        # 결과 캐싱
        if results['variations']:
            result_paths = [Path(v['output_file']) for v in results['variations']]
            self.cache.cache_result(cache_key, result_paths, image_path, 
                                  kwargs.get('prompt', ''), kwargs)
        
        return results
    
    def _generate_single_variation_with_quality_check(self, image: Image, 
                                                     variation_id: int,
                                                     quality_settings: Dict,
                                                     **kwargs) -> Dict:
        """품질 검증이 포함된 단일 변형 생성"""
        # 기본 변형 생성
        variation_result = self._generate_basic_variation(
            image, variation_id, **kwargs
        )
        
        if not variation_result['success']:
            return variation_result
        
        # 생성된 이미지 로드
        generated_image = Image.open(variation_result['output_file'])
        
        # 중복 검사
        if self.duplication_preventer.is_duplicate(generated_image):
            return {
                'success': False,
                'error': '중복된 변형이 생성됨',
                'quality_metrics': {}
            }
        
        # 품질 분석
        other_variations = [img for img in self.duplication_preventer.generated_variations]
        quality_metrics = self.quality_analyzer.analyze_variation_quality(
            image, generated_image, other_variations
        )
        
        # 품질 기준 확인
        if (quality_metrics['overall_quality'] >= quality_settings['quality_threshold'] 
            and self.quality_analyzer.is_acceptable_quality(quality_metrics)):
            
            # 중복 방지 시스템에 등록
            self.duplication_preventer.add_variation(generated_image)
            
            variation_result['quality_metrics'] = quality_metrics
            return variation_result
        else:
            # 품질 기준 미달
            Path(variation_result['output_file']).unlink(missing_ok=True)
            return {
                'success': False,
                'error': f"품질 기준 미달 (점수: {quality_metrics['overall_quality']:.2f})",
                'quality_metrics': quality_metrics
            }
```

## ✅ 완료 기준
- [ ] 변형 품질 분석 시스템 구현 및 테스트
- [ ] 중복 방지 알고리즘 개발 및 검증
- [ ] 메모리 최적화 및 성능 튜닝
- [ ] 캐싱 시스템 구현 및 테스트
- [ ] 재시도 메커니즘 및 오류 복구 시스템
- [ ] 점진적 품질 조정 시스템 구현
- [ ] 통합된 EnhancedImageVariationProcessor 테스트

## 🔄 다음 단계
Phase 5에서는 전체 시스템의 테스팅, 문서화, 그리고 배포 준비를 진행합니다.