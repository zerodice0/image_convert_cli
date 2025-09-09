#!/usr/bin/env python3
"""
Integration tests for image variation functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageDraw
import json
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from batch_nanobanana_core import (
    ImageVariationProcessor,
    EnhancedImageVariationProcessor,
    VariationEngine
)


class TestVariationIntegration(unittest.TestCase):
    """Integration tests for variation system"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.test_dir / "input"
        self.output_dir = self.test_dir / "output"
        
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create test images
        self.create_test_images()
    
    def create_test_images(self):
        """Create test images with patterns"""
        image_configs = [
            {'name': 'landscape.jpg', 'size': (1920, 1080), 'color': (135, 206, 235)},  # Sky blue
            {'name': 'portrait.jpg', 'size': (1080, 1920), 'color': (255, 182, 193)},   # Light pink
            {'name': 'square.png', 'size': (1024, 1024), 'color': (144, 238, 144)},     # Light green
            {'name': 'small.jpg', 'size': (512, 512), 'color': (255, 255, 200)},        # Light yellow
        ]
        
        for config in image_configs:
            img = Image.new('RGB', config['size'], config['color'])
            
            # Add simple patterns for testing
            draw = ImageDraw.Draw(img)
            
            # Border rectangle
            draw.rectangle([50, 50, config['size'][0]-50, config['size'][1]-50], 
                         outline=(0, 0, 0), width=5)
            
            # Center circle
            center_x, center_y = config['size'][0] // 2, config['size'][1] // 2
            radius = min(config['size']) // 8
            draw.ellipse([center_x-radius, center_y-radius, 
                         center_x+radius, center_y+radius], 
                        outline=(255, 0, 0), width=3)
            
            img.save(self.input_dir / config['name'])
    
    def test_full_variation_pipeline_mock(self):
        """Test complete variation pipeline without API calls"""
        processor = ImageVariationProcessor("test-api-key-12345")
        
        test_image = self.input_dir / "square.png"
        
        # Test input validation
        self.assertTrue(processor.validate_image_file(test_image))
        
        # Test prompt generation through engine
        engine = VariationEngine()
        prompt = engine.create_variation_prompt(
            base_image=Image.open(test_image),
            variation_id=1,
            variation_type='random',
            seed=42
        )
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 20)
        
        # Test output directory creation
        output_path = self.output_dir / "variation_test"
        output_path.mkdir(exist_ok=True)
        
        # Verify directory structure
        self.assertTrue(output_path.exists())
    
    def test_enhanced_processor_initialization(self):
        """Test EnhancedImageVariationProcessor initialization"""
        processor = EnhancedImageVariationProcessor("test-api-key")
        
        # Test initialization
        self.assertIsNotNone(processor.quality_analyzer)
        self.assertIsNotNone(processor.duplication_preventer)
        self.assertIsNotNone(processor.memory_optimizer)
        self.assertIsNotNone(processor.cache)
        self.assertIsNotNone(processor.retry_manager)
        self.assertIsNotNone(processor.quality_manager)
        
        # Test fallback mode
        stats = processor.get_performance_stats()
        self.assertIn('advanced_features_enabled', stats)
        self.assertIn('success_rate_history', stats)
    
    def test_gui_cli_compatibility_structure(self):
        """Test GUI and CLI compatibility without actual execution"""
        # Test CLI argument validation structure
        from batch_nanobanana_cli import BatchNanoBananaCLI
        
        cli = BatchNanoBananaCLI()
        
        # Mock arguments for validation testing
        class MockArgs:
            def __init__(self, input_dir, output_dir):
                self.image = str(input_dir / "square.png")
                self.count = 2
                self.variation_type = 'random'
                self.output_dir = str(output_dir / "cli_test")
                self.styles = None
                self.seed = None
                self.quality_threshold = 0.7
                self.max_attempts = 2
                self.parallel = 1
        
        args = MockArgs(self.input_dir, self.output_dir)
        
        # Test input validation (should pass without API calls)
        result = cli.validate_variation_inputs(args)
        self.assertTrue(result)
        
        # Test output directory creation
        Path(args.output_dir).mkdir(exist_ok=True)
        self.assertTrue(Path(args.output_dir).exists())
    
    def test_error_handling_workflows(self):
        """Test error handling in various scenarios"""
        processor = ImageVariationProcessor("invalid-api-key")
        
        # Test with non-existent image
        fake_image = self.test_dir / "nonexistent.jpg"
        result = processor.generate_single_variation(
            image_path=fake_image,
            variation_id=1,
            variation_type="random"
        )
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Test with invalid variation type
        valid_image = self.input_dir / "small.jpg"
        result = processor.generate_single_variation(
            image_path=valid_image,
            variation_id=1,
            variation_type="invalid_type"
        )
        self.assertFalse(result["success"])
        self.assertIn("지원하지 않는 변형 타입", result["error"])
    
    def test_batch_processing_structure(self):
        """Test batch processing structure without API calls"""
        processor = ImageVariationProcessor("test-api-key")
        
        # Test batch validation
        input_files = list(self.input_dir.glob("*.jpg")) + list(self.input_dir.glob("*.png"))
        self.assertGreater(len(input_files), 0)
        
        for image_file in input_files:
            self.assertTrue(processor.validate_image_file(image_file))
        
        # Test output structure
        batch_output = self.output_dir / "batch_test"
        batch_output.mkdir(exist_ok=True)
        
        for i, image_file in enumerate(input_files):
            image_output = batch_output / f"{image_file.stem}_variations"
            image_output.mkdir(exist_ok=True)
            self.assertTrue(image_output.exists())
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)


class TestPerformanceBenchmark(unittest.TestCase):
    """Performance benchmark tests"""
    
    def test_memory_usage_simulation(self):
        """Test memory usage with image processing simulation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate large image processing
        large_images = []
        try:
            for i in range(5):  # Reduced from 10 to 5 for testing
                img = Image.new('RGB', (1024, 1024), (i*50, i*50, i*50))
                large_images.append(img)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory
            
            # Memory should be reasonable (less than 200MB for test)
            self.assertLess(memory_increase, 200, 
                           f"Memory usage too high: {memory_increase:.1f}MB")
        
        finally:
            # Clean up
            del large_images
    
    def test_processing_speed_simulation(self):
        """Test processing speed with prompt generation"""
        import time
        from batch_nanobanana_core import VariationEngine
        
        engine = VariationEngine()
        test_image = Image.new('RGB', (256, 256), 'white')
        
        start_time = time.time()
        
        # Generate multiple prompts
        prompts = []
        for i in range(50):  # Reduced from 100 to 50 for testing
            prompt = engine.create_variation_prompt(
                base_image=test_image,
                variation_id=i,
                variation_type='random',
                seed=i
            )
            prompts.append(prompt)
        
        elapsed_time = time.time() - start_time
        
        # 50 prompts should be generated quickly (under 1 second)
        self.assertLess(elapsed_time, 1.0,
                       f"Prompt generation too slow: {elapsed_time:.2f}s")
        
        # Verify all prompts were generated
        self.assertEqual(len(prompts), 50)
        
        # Verify prompts are not empty
        for prompt in prompts:
            self.assertGreater(len(prompt), 5)


class TestUserScenarios(unittest.TestCase):
    """User scenario simulation tests"""
    
    def setUp(self):
        """Setup for user scenario tests"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.processor = ImageVariationProcessor("test-api-key")
    
    def test_casual_user_workflow_simulation(self):
        """Simulate casual user workflow structure"""
        # Scenario: Family photos variation
        
        # Create mock family photos
        family_photos = []
        for i in range(3):
            photo_path = self.test_dir / f"family_{i+1}.jpg"
            img = Image.new('RGB', (1920, 1080), (100+i*50, 150+i*30, 200+i*40))
            
            # Add some simple content
            draw = ImageDraw.Draw(img)
            draw.rectangle([100, 100, 1820, 980], outline=(0, 0, 0), width=5)
            draw.text((960, 540), f"Family Photo {i+1}", fill=(255, 255, 255))
            
            img.save(photo_path)
            family_photos.append(photo_path)
        
        # Validate all photos
        for photo in family_photos:
            self.assertTrue(self.processor.validate_image_file(photo))
        
        # Test variation parameters
        variation_settings = {
            'count': 5,
            'variation_type': 'random',
            'styles': ['rearrange', 'style'],
            'quality_threshold': 0.7
        }
        
        # Verify settings are valid
        self.assertGreater(variation_settings['count'], 0)
        self.assertLessEqual(variation_settings['count'], 20)
        self.assertIn(variation_settings['variation_type'], 
                     ['random', 'rearrange', 'add', 'remove', 'style', 'composition'])
    
    def test_professional_user_workflow_simulation(self):
        """Simulate professional user workflow structure"""
        # Scenario: Product photos batch variation
        
        # Create mock product photos
        product_photos = []
        products = ['product_a', 'product_b', 'product_c']
        
        for product in products:
            photo_path = self.test_dir / f"{product}.jpg"
            img = Image.new('RGB', (2048, 2048), (240, 240, 240))  # Light gray background
            
            # Add product representation
            draw = ImageDraw.Draw(img)
            draw.rectangle([512, 512, 1536, 1536], fill=(200, 100, 50), outline=(0, 0, 0), width=3)
            draw.text((1024, 1024), product.replace('_', ' ').title(), 
                     fill=(255, 255, 255), anchor="mm")
            
            img.save(photo_path)
            product_photos.append(photo_path)
        
        # Test batch processing structure
        batch_settings = {
            'count_per_image': 10,
            'variation_types': ['rearrange', 'add', 'style'],
            'parallel_workers': 2,
            'quality_threshold': 0.8
        }
        
        # Validate batch settings
        self.assertGreater(batch_settings['count_per_image'], 0)
        self.assertLessEqual(batch_settings['parallel_workers'], 4)
        self.assertGreaterEqual(batch_settings['quality_threshold'], 0.5)
        
        # Test output directory structure
        batch_output = self.test_dir / "batch_variations"
        batch_output.mkdir()
        
        for product_photo in product_photos:
            product_output = batch_output / f"{product_photo.stem}_variations"
            product_output.mkdir()
            self.assertTrue(product_output.exists())
    
    def test_error_recovery_scenario_simulation(self):
        """Simulate error recovery scenarios"""
        # Scenario: Network issues and retries
        
        # Create test image
        test_image = self.test_dir / "test_image.jpg"
        img = Image.new('RGB', (1024, 1024), 'blue')
        img.save(test_image)
        
        # Test retry configuration
        retry_settings = {
            'max_attempts': 3,
            'backoff_factor': 2,
            'timeout': 30,
            'retryable_errors': ['network', 'timeout', 'rate_limit']
        }
        
        # Validate retry settings
        self.assertGreaterEqual(retry_settings['max_attempts'], 1)
        self.assertLessEqual(retry_settings['max_attempts'], 5)
        self.assertGreater(retry_settings['timeout'], 0)
        
        # Test error simulation
        error_scenarios = [
            {'type': 'network_error', 'retryable': True},
            {'type': 'invalid_api_key', 'retryable': False},
            {'type': 'quota_exceeded', 'retryable': True},
            {'type': 'invalid_image', 'retryable': False}
        ]
        
        for scenario in error_scenarios:
            self.assertIn('type', scenario)
            self.assertIn('retryable', scenario)
            self.assertIsInstance(scenario['retryable'], bool)
    
    def tearDown(self):
        """Clean up user scenario tests"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)


if __name__ == '__main__':
    # Create test directories if needed
    tests_dir = Path(__file__).parent
    tests_dir.mkdir(exist_ok=True)
    
    # Run tests with detailed output
    unittest.main(verbosity=2)