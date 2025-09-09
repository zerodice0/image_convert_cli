#!/usr/bin/env python3
"""
Advanced Image Variation Features
고급 이미지 변형 기능들: 품질 검증, 중복 방지, 성능 최적화, 캐싱 등
"""

import os
import sys
import json
import time
import hashlib
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import tempfile
import numpy as np
from PIL import Image, ImageStat, ImageFilter

# 선택적 의존성들 (없으면 폴백 구현 사용)
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from skimage.metrics import structural_similarity as ssim
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False

try:
    import imagehash
    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False


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
    
    def analyze_variation_quality(self, original_image: Image.Image, 
                                variation_image: Image.Image, 
                                other_variations: List[Image.Image] = None) -> Dict[str, float]:
        """변형 품질 종합 분석"""
        metrics = {}
        
        try:
            # 1. 원본과의 유사도 분석
            metrics['similarity'] = self.calculate_similarity(original_image, variation_image)
            
            # 2. 다양성 분석 (다른 변형들과의 차이)
            if other_variations:
                metrics['diversity'] = self.calculate_diversity(variation_image, other_variations)
            else:
                metrics['diversity'] = 1.0  # 첫 번째 변형은 최대 다양성
            
            # 3. 미적 품질 분석
            metrics['aesthetic'] = self.analyze_aesthetic_quality(variation_image)
            
            # 4. 객체 완전성 검증
            metrics['object_integrity'] = self.verify_object_integrity(variation_image)
            
            # 5. 전체 품질 점수 계산
            metrics['overall_quality'] = self.calculate_overall_quality(metrics)
            
        except Exception as e:
            logging.warning(f"품질 분석 중 오류: {e}")
            # 기본값으로 폴백
            metrics = {
                'similarity': 0.5,
                'diversity': 0.5,
                'aesthetic': 0.5,
                'object_integrity': 0.5,
                'overall_quality': 0.5
            }
        
        return metrics
    
    def calculate_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """이미지 간 유사도 계산"""
        try:
            if HAS_SKIMAGE and HAS_OPENCV:
                return self._calculate_similarity_ssim(img1, img2)
            else:
                return self._calculate_similarity_histogram(img1, img2)
        except Exception as e:
            logging.warning(f"유사도 계산 오류: {e}")
            return 0.5
    
    def _calculate_similarity_ssim(self, img1: Image.Image, img2: Image.Image) -> float:
        """SSIM 기반 유사도 계산 (고급)"""
        # 이미지를 그레이스케일로 변환
        img1_gray = np.array(img1.convert('L'))
        img2_gray = np.array(img2.convert('L'))
        
        # 크기 통일
        if img1_gray.shape != img2_gray.shape:
            img2_gray = cv2.resize(img2_gray, img1_gray.shape[::-1])
        
        # SSIM 계산
        similarity_score = ssim(img1_gray, img2_gray)
        return max(0.0, min(1.0, similarity_score))
    
    def _calculate_similarity_histogram(self, img1: Image.Image, img2: Image.Image) -> float:
        """히스토그램 기반 유사도 계산 (폴백)"""
        # RGB 채널별 히스토그램 생성
        hist1 = img1.histogram()
        hist2 = img2.histogram()
        
        # 코사인 유사도 계산
        sum_sq1 = sum(x*x for x in hist1)
        sum_sq2 = sum(x*x for x in hist2)
        sum_prod = sum(x*y for x, y in zip(hist1, hist2))
        
        if sum_sq1 * sum_sq2 == 0:
            return 0.0
        
        similarity = sum_prod / (sum_sq1 * sum_sq2) ** 0.5
        return max(0.0, min(1.0, similarity))
    
    def calculate_diversity(self, target_img: Image.Image, other_imgs: List[Image.Image]) -> float:
        """변형들 간 다양성 계산"""
        if not other_imgs:
            return 1.0
        
        try:
            # 각 이미지와의 차이 계산
            differences = []
            for other_img in other_imgs:
                similarity = self.calculate_similarity(target_img, other_img)
                differences.append(1.0 - similarity)  # 차이 = 1 - 유사도
            
            # 평균 차이도 반환
            return sum(differences) / len(differences)
        except Exception as e:
            logging.warning(f"다양성 계산 오류: {e}")
            return 0.5
    
    def analyze_aesthetic_quality(self, image: Image.Image) -> float:
        """미적 품질 분석"""
        try:
            # 기본 이미지 통계
            stat = ImageStat.Stat(image)
            
            metrics = {}
            
            # 1. 색상 분산 (다채로운 색상 선호)
            if len(stat.var) >= 3:
                color_variance = np.var(stat.var[:3])
                metrics['color_variance'] = min(color_variance / 10000, 1.0)
            else:
                metrics['color_variance'] = 0.5
            
            # 2. 대비 분석
            img_array = np.array(image.convert('L'))
            contrast = np.std(img_array) / 255.0
            metrics['contrast'] = min(contrast * 2, 1.0)
            
            # 3. 밝기 균형
            brightness = np.mean(img_array) / 255.0
            brightness_balance = 1.0 - abs(brightness - 0.5) * 2
            metrics['brightness_balance'] = max(0.0, brightness_balance)
            
            # 4. 선명도 (간단한 방식)
            sharpness = self._calculate_sharpness_simple(image)
            metrics['sharpness'] = sharpness
            
            # 종합 미적 점수
            weights = {
                'color_variance': 0.25,
                'contrast': 0.25,
                'brightness_balance': 0.25,
                'sharpness': 0.25
            }
            
            aesthetic_score = sum(metrics[key] * weights[key] for key in weights)
            return max(0.0, min(1.0, aesthetic_score))
            
        except Exception as e:
            logging.warning(f"미적 품질 분석 오류: {e}")
            return 0.5
    
    def _calculate_sharpness_simple(self, image: Image.Image) -> float:
        """간단한 선명도 계산 (PIL 기반)"""
        try:
            # 엣지 필터 적용
            edges = image.filter(ImageFilter.FIND_EDGES)
            
            # 엣지 픽셀의 분산 계산
            edge_array = np.array(edges.convert('L'))
            sharpness = np.var(edge_array) / (255.0 ** 2)
            
            return min(sharpness * 10, 1.0)
        except Exception as e:
            logging.warning(f"선명도 계산 오류: {e}")
            return 0.5
    
    def verify_object_integrity(self, image: Image.Image) -> float:
        """객체 완전성 검증 (단순화된 버전)"""
        try:
            if HAS_OPENCV:
                return self._verify_object_integrity_opencv(image)
            else:
                return self._verify_object_integrity_simple(image)
        except Exception as e:
            logging.warning(f"객체 완전성 검증 오류: {e}")
            return 0.5
    
    def _verify_object_integrity_opencv(self, image: Image.Image) -> float:
        """OpenCV 기반 객체 완전성 검증"""
        img_array = np.array(image.convert('L'))
        
        # Canny 엣지 검출
        edges = cv2.Canny(img_array, 50, 150)
        
        # 연결된 컴포넌트 분석
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(edges)
        
        # 객체 완전성 점수
        if num_labels > 1:
            areas = stats[1:, cv2.CC_STAT_AREA]  # 배경 제외
            total_area = image.size[0] * image.size[1]
            large_areas = areas[areas > total_area * 0.01]
            integrity = min(len(large_areas) / 10, 1.0)
        else:
            integrity = 0.1
        
        return integrity
    
    def _verify_object_integrity_simple(self, image: Image.Image) -> float:
        """단순한 객체 완전성 검증 (폴백)"""
        # 엣지 필터로 근사적 분석
        edges = image.filter(ImageFilter.FIND_EDGES)
        edge_array = np.array(edges.convert('L'))
        
        # 엣지 픽셀 비율 계산
        edge_pixels = np.sum(edge_array > 50)
        total_pixels = edge_array.size
        edge_ratio = edge_pixels / total_pixels
        
        # 적절한 엣지 비율을 객체 완전성으로 간주
        integrity = min(edge_ratio * 20, 1.0)  # 5% 엣지 = 1.0 점수
        return max(0.1, integrity)
    
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
        return max(0.0, min(1.0, overall))

    def is_acceptable_quality(self, metrics: Dict[str, float]) -> bool:
        """품질 기준 통과 여부 판단"""
        try:
            checks = [
                self.quality_thresholds['similarity_min'] <= metrics.get('similarity', 0) <= self.quality_thresholds['similarity_max'],
                metrics.get('diversity', 0) >= self.quality_thresholds['diversity_min'],
                metrics.get('aesthetic', 0) >= self.quality_thresholds['aesthetic_min'],
                metrics.get('object_integrity', 0) >= self.quality_thresholds['object_integrity'],
                metrics.get('overall_quality', 0) >= 0.6
            ]
            
            return all(checks)
        except Exception as e:
            logging.warning(f"품질 기준 확인 오류: {e}")
            return True  # 오류 시 관대하게 처리


class DuplicationPreventer:
    """변형 중복 방지 시스템"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.similarity_threshold = similarity_threshold
        self.generated_variations: List[Image.Image] = []
        self.image_hashes = set()
        
    def is_duplicate(self, new_image: Image.Image) -> bool:
        """새 이미지가 기존 변형들과 중복인지 확인"""
        try:
            # 1. 이미지 해시 기반 빠른 중복 검사
            image_hash = self.calculate_image_hash(new_image)
            if image_hash in self.image_hashes:
                return True
            
            # 2. 구조적 유사도 기반 정밀 검사
            analyzer = VariationQualityAnalyzer()
            for existing_image in self.generated_variations:
                similarity = analyzer.calculate_similarity(new_image, existing_image)
                if similarity > self.similarity_threshold:
                    return True
            
            return False
        except Exception as e:
            logging.warning(f"중복 검사 오류: {e}")
            return False  # 오류 시 관대하게 처리
    
    def calculate_image_hash(self, image: Image.Image) -> str:
        """이미지의 지각적 해시 계산"""
        if HAS_IMAGEHASH:
            return self._calculate_image_hash_advanced(image)
        else:
            return self._calculate_image_hash_simple(image)
    
    def _calculate_image_hash_advanced(self, image: Image.Image) -> str:
        """고급 이미지 해시 계산"""
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
    
    def _calculate_image_hash_simple(self, image: Image.Image) -> str:
        """단순한 이미지 해시 계산 (폴백)"""
        # 이미지를 작은 크기로 리사이즈하고 해시 계산
        small_image = image.resize((8, 8), Image.Resampling.LANCZOS)
        gray_image = small_image.convert('L')
        
        # 픽셀 값들을 해시로 변환
        pixels = list(gray_image.getdata())
        pixel_str = ''.join(str(p) for p in pixels)
        return hashlib.md5(pixel_str.encode()).hexdigest()
    
    def add_variation(self, image: Image.Image) -> bool:
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


class MemoryOptimizer:
    """메모리 사용량 최적화"""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.current_memory_usage = 0
        
    def optimize_image_size(self, image: Image.Image, max_dimension: int = 2048) -> Image.Image:
        """이미지 크기 최적화"""
        try:
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
                logging.info(f"이미지 크기 최적화: {width}x{height} → {new_width}x{new_height}")
                return optimized
            
            return image
        except Exception as e:
            logging.warning(f"이미지 크기 최적화 오류: {e}")
            return image
    
    def manage_batch_memory(self, batch_size: int, image_sizes: List[Tuple[int, int]]) -> int:
        """배치 처리 시 메모리 기반 최적 배치 크기 계산"""
        try:
            if not image_sizes:
                return batch_size
            
            # 평균 이미지 메모리 사용량 추정
            avg_pixels = sum(w * h for w, h in image_sizes) / len(image_sizes)
            estimated_mb_per_image = (avg_pixels * 3 * 4) / (1024 * 1024)  # RGB, float32
            
            # API 응답 이미지까지 고려한 메모리 사용량
            total_memory_per_batch = estimated_mb_per_image * batch_size * 2  # 원본 + 결과
            
            if total_memory_per_batch > self.max_memory_mb:
                optimal_batch_size = max(1, int(self.max_memory_mb / (estimated_mb_per_image * 2)))
                logging.info(f"배치 크기 최적화: {batch_size} → {optimal_batch_size}")
                return optimal_batch_size
            
            return batch_size
        except Exception as e:
            logging.warning(f"배치 메모리 관리 오류: {e}")
            return batch_size
    
    def cleanup_temp_files(self, temp_dir: Path):
        """임시 파일 정리"""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                logging.info(f"임시 파일 정리 완료: {temp_dir}")
        except Exception as e:
            logging.warning(f"임시 파일 정리 오류: {e}")


class VariationCache:
    """변형 생성 결과 캐싱"""
    
    def __init__(self, cache_dir: Path = None, max_cache_size_gb: float = 1.0):
        self.cache_dir = cache_dir or Path.home() / '.nanobanana_cache' / 'variations'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size_gb = max_cache_size_gb
        self.cache_index = self.load_cache_index()
        
    def load_cache_index(self) -> Dict:
        """캐시 인덱스 로드"""
        index_file = self.cache_dir / 'cache_index.json'
        try:
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"캐시 인덱스 로드 오류: {e}")
        return {}
    
    def save_cache_index(self):
        """캐시 인덱스 저장"""
        index_file = self.cache_dir / 'cache_index.json'
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.warning(f"캐시 인덱스 저장 오류: {e}")
        
    def generate_cache_key(self, image_path: Path, prompt: str, variation_params: Dict) -> str:
        """캐시 키 생성"""
        try:
            # 이미지 파일 해시
            with open(image_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            
            # 프롬프트 및 파라미터 해시
            param_str = f"{prompt}_{json.dumps(variation_params, sort_keys=True)}"
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            
            return f"{file_hash}_{param_hash}"
        except Exception as e:
            logging.warning(f"캐시 키 생성 오류: {e}")
            return f"error_{int(time.time())}"
    
    def get_cached_result(self, cache_key: str) -> Optional[List[Path]]:
        """캐시된 결과 조회"""
        try:
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
        except Exception as e:
            logging.warning(f"캐시 조회 오류: {e}")
            return None
    
    def cache_result(self, cache_key: str, result_paths: List[Path], 
                    original_image: Path, prompt: str, params: Dict):
        """결과를 캐시에 저장"""
        try:
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
            
            logging.info(f"결과 캐싱 완료: {cache_key}")
        except Exception as e:
            logging.warning(f"결과 캐싱 오류: {e}")
    
    def cleanup_old_cache(self):
        """오래된 캐시 정리"""
        try:
            # 캐시 크기 확인
            total_size = 0
            for cache_dir in self.cache_dir.iterdir():
                if cache_dir.is_dir():
                    for f in cache_dir.rglob('*'):
                        if f.is_file():
                            total_size += f.stat().st_size
            
            total_size_gb = total_size / (1024**3)
            
            if total_size_gb > self.max_cache_size_gb:
                # 오래된 항목부터 제거
                sorted_entries = sorted(
                    self.cache_index.items(),
                    key=lambda x: x[1].get('last_used', '1970-01-01')
                )
                
                for cache_key, entry in sorted_entries:
                    if total_size_gb <= self.max_cache_size_gb * 0.8:  # 80%까지 줄이기
                        break
                        
                    # 캐시 디렉토리 제거
                    cache_subdir = self.cache_dir / cache_key
                    if cache_subdir.exists():
                        dir_size = sum(f.stat().st_size for f in cache_subdir.rglob('*') if f.is_file())
                        shutil.rmtree(cache_subdir, ignore_errors=True)
                        total_size_gb -= dir_size / (1024**3)
                    
                    # 인덱스에서 제거
                    if cache_key in self.cache_index:
                        del self.cache_index[cache_key]
                
                self.save_cache_index()
                logging.info(f"캐시 정리 완료: {total_size_gb:.2f}GB → {total_size_gb:.2f}GB")
        except Exception as e:
            logging.warning(f"캐시 정리 오류: {e}")


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
                    logging.info(f"재시도 대기 중: {delay:.1f}초 (시도 {attempt + 1}/{self.max_attempts})")
                    time.sleep(delay)
        
        # 모든 재시도 실패
        logging.error(f"모든 재시도 실패: {last_exception}")
        raise last_exception
    
    def is_non_retryable_error(self, error: Exception) -> bool:
        """재시도하지 않을 오류 판단"""
        non_retryable_patterns = [
            'authentication failed',
            'invalid api key',
            'quota exceeded',
            'content policy violation',
            'permission denied'
        ]
        
        error_msg = str(error).lower()
        return any(pattern in error_msg for pattern in non_retryable_patterns)


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