#!/usr/bin/env python3
"""
Tests for advanced image variation features
고급 이미지 변형 기능 테스트
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from PIL import Image
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from variation_advanced import (
        VariationQualityAnalyzer,
        DuplicationPreventer, 
        MemoryOptimizer,
        VariationCache,
        RetryManager,
        AdaptiveQualityManager
    )
    from batch_nanobanana_core import EnhancedImageVariationProcessor
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"Advanced features not available: {e}")
    ADVANCED_FEATURES_AVAILABLE = False


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestVariationQualityAnalyzer(unittest.TestCase):
    """Test variation quality analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = VariationQualityAnalyzer()
        
        # Create test images
        self.test_image1 = Image.new('RGB', (100, 100), 'red')
        self.test_image2 = Image.new('RGB', (100, 100), 'blue')
        self.test_image3 = Image.new('RGB', (100, 100), 'green')
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertIsInstance(self.analyzer.quality_thresholds, dict)
        self.assertIn('similarity_min', self.analyzer.quality_thresholds)
        self.assertIn('aesthetic_min', self.analyzer.quality_thresholds)
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        # Same image should have high similarity
        similarity_same = self.analyzer.calculate_similarity(self.test_image1, self.test_image1)
        self.assertGreater(similarity_same, 0.9)
        
        # Different images should have lower similarity
        similarity_diff = self.analyzer.calculate_similarity(self.test_image1, self.test_image2)
        self.assertLess(similarity_diff, similarity_same)
        
        # Should return float between 0 and 1
        self.assertGreaterEqual(similarity_diff, 0.0)
        self.assertLessEqual(similarity_diff, 1.0)
    
    def test_calculate_diversity(self):
        """Test diversity calculation"""
        other_images = [self.test_image2, self.test_image3]
        diversity = self.analyzer.calculate_diversity(self.test_image1, other_images)
        
        self.assertIsInstance(diversity, float)
        self.assertGreaterEqual(diversity, 0.0)
        self.assertLessEqual(diversity, 1.0)
        
        # Empty list should return max diversity
        diversity_empty = self.analyzer.calculate_diversity(self.test_image1, [])
        self.assertEqual(diversity_empty, 1.0)
    
    def test_analyze_aesthetic_quality(self):
        """Test aesthetic quality analysis"""
        aesthetic_score = self.analyzer.analyze_aesthetic_quality(self.test_image1)
        
        self.assertIsInstance(aesthetic_score, float)
        self.assertGreaterEqual(aesthetic_score, 0.0)
        self.assertLessEqual(aesthetic_score, 1.0)
    
    def test_verify_object_integrity(self):
        """Test object integrity verification"""
        integrity_score = self.analyzer.verify_object_integrity(self.test_image1)
        
        self.assertIsInstance(integrity_score, float)
        self.assertGreaterEqual(integrity_score, 0.0)
        self.assertLessEqual(integrity_score, 1.0)
    
    def test_analyze_variation_quality(self):
        """Test comprehensive quality analysis"""
        quality_metrics = self.analyzer.analyze_variation_quality(
            self.test_image1, self.test_image2, [self.test_image3]
        )
        
        required_metrics = ['similarity', 'diversity', 'aesthetic', 'object_integrity', 'overall_quality']
        for metric in required_metrics:
            self.assertIn(metric, quality_metrics)
            self.assertIsInstance(quality_metrics[metric], float)
            self.assertGreaterEqual(quality_metrics[metric], 0.0)
            self.assertLessEqual(quality_metrics[metric], 1.0)
    
    def test_is_acceptable_quality(self):
        """Test quality acceptance criteria"""
        # Good quality metrics
        good_metrics = {
            'similarity': 0.6,
            'diversity': 0.8,
            'aesthetic': 0.7,
            'object_integrity': 0.8,
            'overall_quality': 0.7
        }
        self.assertTrue(self.analyzer.is_acceptable_quality(good_metrics))
        
        # Poor quality metrics
        poor_metrics = {
            'similarity': 0.1,
            'diversity': 0.1,
            'aesthetic': 0.1,
            'object_integrity': 0.1,
            'overall_quality': 0.1
        }
        self.assertFalse(self.analyzer.is_acceptable_quality(poor_metrics))


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestDuplicationPreventer(unittest.TestCase):
    """Test duplication prevention system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.preventer = DuplicationPreventer()
        
        # Create test images
        self.test_image1 = Image.new('RGB', (50, 50), 'red')
        self.test_image2 = Image.new('RGB', (50, 50), 'blue')
        self.test_image1_copy = Image.new('RGB', (50, 50), 'red')
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertEqual(len(self.preventer.generated_variations), 0)
        self.assertEqual(len(self.preventer.image_hashes), 0)
        self.assertIsInstance(self.preventer.similarity_threshold, float)
    
    def test_calculate_image_hash(self):
        """Test image hash calculation"""
        hash1 = self.preventer.calculate_image_hash(self.test_image1)
        hash2 = self.preventer.calculate_image_hash(self.test_image2)
        hash1_copy = self.preventer.calculate_image_hash(self.test_image1_copy)
        
        self.assertIsInstance(hash1, str)
        self.assertNotEqual(hash1, hash2)  # Different images should have different hashes
        self.assertEqual(hash1, hash1_copy)  # Same images should have same hashes
    
    def test_add_variation(self):
        """Test adding variations"""
        # First image should be added successfully
        result1 = self.preventer.add_variation(self.test_image1)
        self.assertTrue(result1)
        self.assertEqual(len(self.preventer.generated_variations), 1)
        
        # Different image should be added successfully
        result2 = self.preventer.add_variation(self.test_image2)
        self.assertTrue(result2)
        self.assertEqual(len(self.preventer.generated_variations), 2)
        
        # Duplicate should not be added
        result3 = self.preventer.add_variation(self.test_image1_copy)
        self.assertFalse(result3)
        self.assertEqual(len(self.preventer.generated_variations), 2)
    
    def test_is_duplicate(self):
        """Test duplicate detection"""
        # Add first image
        self.preventer.add_variation(self.test_image1)
        
        # Different image should not be duplicate
        self.assertFalse(self.preventer.is_duplicate(self.test_image2))
        
        # Same image should be duplicate
        self.assertTrue(self.preventer.is_duplicate(self.test_image1_copy))
    
    def test_clear(self):
        """Test clearing variations"""
        self.preventer.add_variation(self.test_image1)
        self.preventer.add_variation(self.test_image2)
        
        self.assertEqual(len(self.preventer.generated_variations), 2)
        
        self.preventer.clear()
        
        self.assertEqual(len(self.preventer.generated_variations), 0)
        self.assertEqual(len(self.preventer.image_hashes), 0)


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestMemoryOptimizer(unittest.TestCase):
    """Test memory optimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = MemoryOptimizer()
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertIsInstance(self.optimizer.max_memory_mb, int)
        self.assertGreater(self.optimizer.max_memory_mb, 0)
    
    def test_optimize_image_size(self):
        """Test image size optimization"""
        # Large image that should be resized
        large_image = Image.new('RGB', (4000, 3000), 'red')
        optimized = self.optimizer.optimize_image_size(large_image, max_dimension=2048)
        
        # Should be resized
        self.assertLessEqual(max(optimized.size), 2048)
        self.assertLess(optimized.size[0] * optimized.size[1], large_image.size[0] * large_image.size[1])
        
        # Small image should not be resized
        small_image = Image.new('RGB', (100, 100), 'blue')
        not_optimized = self.optimizer.optimize_image_size(small_image, max_dimension=2048)
        
        self.assertEqual(not_optimized.size, small_image.size)
    
    def test_manage_batch_memory(self):
        """Test batch memory management"""
        image_sizes = [(1000, 1000), (2000, 1500), (800, 600)]
        
        # Normal batch size
        optimal_size = self.optimizer.manage_batch_memory(5, image_sizes)
        self.assertIsInstance(optimal_size, int)
        self.assertGreater(optimal_size, 0)
        
        # Very large batch size should be reduced
        optimal_size_large = self.optimizer.manage_batch_memory(1000, image_sizes)
        self.assertLess(optimal_size_large, 1000)
    
    def test_cleanup_temp_files(self):
        """Test temp file cleanup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some temp files
            (temp_path / "test1.txt").write_text("test")
            (temp_path / "test2.txt").write_text("test")
            
            # Directory should exist and have files
            self.assertTrue(temp_path.exists())
            self.assertEqual(len(list(temp_path.iterdir())), 2)
            
            # Cleanup should remove everything
            self.optimizer.cleanup_temp_files(temp_path)


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestVariationCache(unittest.TestCase):
    """Test variation cache system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = VariationCache(cache_dir=Path(self.temp_dir) / 'cache')
        
        # Create test image
        self.test_image_path = Path(self.temp_dir) / 'test.png'
        test_image = Image.new('RGB', (100, 100), 'red')
        test_image.save(self.test_image_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertTrue(self.cache.cache_dir.exists())
        self.assertIsInstance(self.cache.max_cache_size_gb, float)
        self.assertIsInstance(self.cache.cache_index, dict)
    
    def test_generate_cache_key(self):
        """Test cache key generation"""
        params = {'variation_type': 'random', 'count': 5}
        key = self.cache.generate_cache_key(self.test_image_path, 'test prompt', params)
        
        self.assertIsInstance(key, str)
        self.assertGreater(len(key), 0)
        
        # Same inputs should generate same key
        key2 = self.cache.generate_cache_key(self.test_image_path, 'test prompt', params)
        self.assertEqual(key, key2)
        
        # Different inputs should generate different keys
        different_params = {'variation_type': 'rearrange', 'count': 3}
        key3 = self.cache.generate_cache_key(self.test_image_path, 'test prompt', different_params)
        self.assertNotEqual(key, key3)
    
    def test_cache_and_retrieve_result(self):
        """Test caching and retrieving results"""
        # Create test result files
        result_path1 = Path(self.temp_dir) / 'result1.png'
        result_path2 = Path(self.temp_dir) / 'result2.png'
        
        test_image = Image.new('RGB', (50, 50), 'blue')
        test_image.save(result_path1)
        test_image.save(result_path2)
        
        cache_key = 'test_key_123'
        params = {'variation_type': 'random'}
        
        # Cache the results
        self.cache.cache_result(
            cache_key, 
            [result_path1, result_path2], 
            self.test_image_path, 
            'test prompt', 
            params
        )
        
        # Should be in cache index
        self.assertIn(cache_key, self.cache.cache_index)
        
        # Retrieve cached results
        cached_results = self.cache.get_cached_result(cache_key)
        
        self.assertIsNotNone(cached_results)
        self.assertEqual(len(cached_results), 2)
        self.assertTrue(all(path.exists() for path in cached_results))
    
    def test_cache_miss(self):
        """Test cache miss behavior"""
        result = self.cache.get_cached_result('nonexistent_key')
        self.assertIsNone(result)


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestRetryManager(unittest.TestCase):
    """Test retry manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.retry_manager = RetryManager(max_attempts=3, base_delay=0.1)
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertEqual(self.retry_manager.max_attempts, 3)
        self.assertEqual(self.retry_manager.base_delay, 0.1)
    
    def test_successful_operation(self):
        """Test successful operation on first try"""
        def successful_func():
            return "success"
        
        result = self.retry_manager.retry_with_backoff(successful_func)
        self.assertEqual(result, "success")
    
    def test_retry_mechanism(self):
        """Test retry mechanism with eventual success"""
        attempt_count = [0]
        
        def flaky_func():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise Exception("Temporary failure")
            return "success after retries"
        
        result = self.retry_manager.retry_with_backoff(flaky_func)
        self.assertEqual(result, "success after retries")
        self.assertEqual(attempt_count[0], 3)
    
    def test_non_retryable_error(self):
        """Test non-retryable errors are not retried"""
        def non_retryable_func():
            raise Exception("authentication failed")
        
        with self.assertRaises(Exception) as cm:
            self.retry_manager.retry_with_backoff(non_retryable_func)
        
        self.assertIn("authentication failed", str(cm.exception))
    
    def test_is_non_retryable_error(self):
        """Test non-retryable error detection"""
        retryable_error = Exception("network timeout")
        non_retryable_error = Exception("invalid api key")
        
        self.assertFalse(self.retry_manager.is_non_retryable_error(retryable_error))
        self.assertTrue(self.retry_manager.is_non_retryable_error(non_retryable_error))


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestAdaptiveQualityManager(unittest.TestCase):
    """Test adaptive quality manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.quality_manager = AdaptiveQualityManager()
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertEqual(self.quality_manager.current_quality_level, 'high')
        self.assertIsInstance(self.quality_manager.quality_settings, dict)
        self.assertIn('high', self.quality_manager.quality_settings)
        self.assertIn('medium', self.quality_manager.quality_settings)
        self.assertIn('low', self.quality_manager.quality_settings)
    
    def test_quality_adjustment(self):
        """Test quality level adjustment based on performance"""
        # Start with high quality
        self.assertEqual(self.quality_manager.current_quality_level, 'high')
        
        # Poor performance should lower quality
        for _ in range(5):
            self.quality_manager.adjust_quality_based_on_performance(0.3)
        
        # Should have adjusted to medium or low
        self.assertIn(self.quality_manager.current_quality_level, ['medium', 'low'])
        
        # Good performance should restore quality
        for _ in range(5):
            self.quality_manager.adjust_quality_based_on_performance(0.9)
        
        self.assertEqual(self.quality_manager.current_quality_level, 'high')
    
    def test_get_current_settings(self):
        """Test getting current quality settings"""
        settings = self.quality_manager.get_current_settings()
        
        self.assertIsInstance(settings, dict)
        self.assertIn('max_image_size', settings)
        self.assertIn('quality_threshold', settings)
        self.assertIn('max_attempts_per_variation', settings)
        
        # Should be a copy, not the original
        settings['test'] = 'test'
        original_settings = self.quality_manager.quality_settings[self.quality_manager.current_quality_level]
        self.assertNotIn('test', original_settings)


@unittest.skipUnless(ADVANCED_FEATURES_AVAILABLE, "Advanced features not available")
class TestEnhancedImageVariationProcessor(unittest.TestCase):
    """Test enhanced image variation processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use a dummy API key for testing
        self.processor = EnhancedImageVariationProcessor(
            "test-api-key-12345",
            enable_quality_analysis=True,
            enable_caching=True,
            enable_duplication_prevention=True
        )
        
        # Create a temporary directory for test files
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create a test image
        self.test_image_path = self.temp_dir / "test_image.png"
        test_image = Image.new('RGB', (200, 200), 'green')
        test_image.save(self.test_image_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test proper initialization"""
        # Should have advanced features enabled if module is available
        if ADVANCED_FEATURES_AVAILABLE:
            self.assertTrue(self.processor.advanced_features_enabled)
            self.assertIsNotNone(self.processor.quality_analyzer)
            self.assertIsNotNone(self.processor.duplication_preventer)
            self.assertIsNotNone(self.processor.memory_optimizer)
    
    def test_fallback_to_basic_mode(self):
        """Test fallback to basic mode when advanced features fail"""
        # This test would require mocking the advanced features import failure
        # For now, we just test that the basic method is available
        self.assertTrue(hasattr(self.processor, 'generate_variations'))
        self.assertTrue(callable(self.processor.generate_variations))
    
    def test_get_performance_stats(self):
        """Test performance statistics"""
        stats = self.processor.get_performance_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('advanced_features_enabled', stats)
        self.assertIn('cache_enabled', stats)
        self.assertIn('quality_analysis_enabled', stats)
        self.assertIn('duplication_prevention_enabled', stats)
        
        if self.processor.advanced_features_enabled:
            self.assertIn('current_quality_level', stats)


if __name__ == '__main__':
    unittest.main(verbosity=2)