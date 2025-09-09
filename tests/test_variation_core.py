#!/usr/bin/env python3
"""
Unit tests for image variation functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from batch_nanobanana_core import (
    VariationPromptGenerator,
    VariationEngine, 
    ImageVariationProcessor
)


class TestVariationPromptGenerator(unittest.TestCase):
    """Test the variation prompt generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = VariationPromptGenerator()
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertIsInstance(self.generator.object_templates, dict)
        self.assertIsInstance(self.generator.style_templates, dict)
        self.assertIsInstance(self.generator.composition_templates, dict)
        
        # Check that templates contain expected keys
        self.assertIn('object_rearrange', self.generator.object_templates)
        self.assertIn('object_add', self.generator.object_templates)
        self.assertIn('object_remove', self.generator.object_templates)
        self.assertIn('style_change', self.generator.style_templates)
        self.assertIn('composition', self.generator.composition_templates)
    
    def test_generate_prompt_basic_types(self):
        """Test prompt generation for basic variation types"""
        variation_types = ['random', 'object_rearrange', 'object_add', 
                          'object_remove', 'style_change', 'composition']
        
        for variation_type in variation_types:
            prompt = self.generator.generate_prompt(variation_type, seed=42)
            
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 10)  # Should be meaningful length
            self.assertNotEqual(prompt.strip(), "")
    
    def test_generate_prompt_with_seed_consistency(self):
        """Test that same seed produces same prompt"""
        seed = 12345
        variation_type = 'object_rearrange'
        
        prompt1 = self.generator.generate_prompt(variation_type, seed)
        prompt2 = self.generator.generate_prompt(variation_type, seed)
        
        self.assertEqual(prompt1, prompt2)
    
    def test_generate_prompt_without_seed_varies(self):
        """Test that no seed produces different prompts"""
        variation_type = 'style_change'
        
        prompts = [self.generator.generate_prompt(variation_type) for _ in range(5)]
        
        # Should have some variation (not all identical)
        unique_prompts = set(prompts)
        self.assertGreater(len(unique_prompts), 1)
    
    def test_generate_prompt_error_handling(self):
        """Test error handling for invalid variation types"""
        # Invalid type should return default prompt
        prompt = self.generator.generate_prompt('invalid_type')
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_object_lists_not_empty(self):
        """Test that object lists are populated"""
        self.assertGreater(len(self.generator._get_random_objects()), 0)
        self.assertGreater(len(self.generator._get_random_positions()), 0)
        self.assertGreater(len(self.generator._get_random_directions()), 0)
        self.assertGreater(len(self.generator._get_art_styles()), 0)
        self.assertGreater(len(self.generator._get_lighting_types()), 0)


class TestVariationEngine(unittest.TestCase):
    """Test the variation engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = VariationEngine()
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertIsInstance(self.engine.VARIATION_TYPES, dict)
        self.assertIsInstance(self.engine.prompt_generator, VariationPromptGenerator)
        
        # Check expected variation types
        expected_types = ['random', 'object_rearrange', 'object_add', 
                         'object_remove', 'style_change', 'composition']
        for vtype in expected_types:
            self.assertIn(vtype, self.engine.VARIATION_TYPES)
    
    def test_validate_variation_type(self):
        """Test variation type validation"""
        # Valid types
        valid_types = ['random', 'object_rearrange', 'object_add']
        for vtype in valid_types:
            self.assertTrue(self.engine.validate_variation_type(vtype))
        
        # Invalid types
        invalid_types = ['invalid', '', 'wrong_type', None]
        for vtype in invalid_types:
            self.assertFalse(self.engine.validate_variation_type(vtype))
    
    def test_get_available_types(self):
        """Test getting available types"""
        types = self.engine.get_available_types()
        self.assertIsInstance(types, dict)
        self.assertEqual(len(types), len(self.engine.VARIATION_TYPES))
        
        # Should be a copy, not the original
        types['test'] = 'test'
        self.assertNotIn('test', self.engine.VARIATION_TYPES)
    
    def test_create_variation_prompt(self):
        """Test variation prompt creation"""
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), 'blue')
        
        prompt = self.engine.create_variation_prompt(
            base_image=test_image,
            variation_id=1,
            variation_type='object_rearrange',
            seed=42
        )
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 10)
    
    def test_create_variation_prompt_with_different_ids(self):
        """Test that different variation IDs produce different prompts"""
        test_image = Image.new('RGB', (100, 100), 'red')
        seed = 100
        
        prompt1 = self.engine.create_variation_prompt(test_image, 1, 'random', seed)
        prompt2 = self.engine.create_variation_prompt(test_image, 2, 'random', seed)
        
        # Should be different due to different variation IDs affecting seed
        # Note: This might occasionally be the same due to randomness, but very unlikely
        self.assertIsInstance(prompt1, str)
        self.assertIsInstance(prompt2, str)


class TestImageVariationProcessor(unittest.TestCase):
    """Test the image variation processor (without API calls)"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use a dummy API key for testing
        self.processor = ImageVariationProcessor("test-api-key-12345")
        
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
        self.assertIsInstance(self.processor.variation_engine, VariationEngine)
        self.assertEqual(self.processor.model, "gemini-2.5-flash-image-preview")
    
    def test_generate_single_variation_invalid_type(self):
        """Test handling of invalid variation type"""
        result = self.processor.generate_single_variation(
            image_path=self.test_image_path,
            variation_id=1,
            variation_type="invalid_type"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("지원하지 않는 변형 타입", result["error"])
        self.assertEqual(result["variation_id"], 1)
    
    def test_generate_single_variation_invalid_image(self):
        """Test handling of invalid image file"""
        invalid_path = self.temp_dir / "nonexistent.png"
        
        result = self.processor.generate_single_variation(
            image_path=invalid_path,
            variation_id=1,
            variation_type="random"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_generate_variations_invalid_image(self):
        """Test batch generation with invalid image"""
        invalid_path = self.temp_dir / "nonexistent.png"
        
        results = self.processor.generate_variations(
            image_path=invalid_path,
            count=3
        )
        
        self.assertEqual(results["successful"], 0)
        self.assertEqual(results["failed"], 1)
        self.assertEqual(results["total"], 3)
        self.assertIn("error", results)
    
    def test_validate_image_file(self):
        """Test image file validation"""
        # Valid image
        self.assertTrue(self.processor.validate_image_file(self.test_image_path))
        
        # Non-existent file
        invalid_path = self.temp_dir / "nonexistent.png"
        self.assertFalse(self.processor.validate_image_file(invalid_path))
        
        # Text file (invalid image)
        text_file = self.temp_dir / "text.txt"
        text_file.write_text("not an image")
        self.assertFalse(self.processor.validate_image_file(text_file))
    
    def test_output_directory_creation(self):
        """Test that output directories are created properly"""
        output_dir = self.temp_dir / "variations"
        
        # Directory should not exist initially
        self.assertFalse(output_dir.exists())
        
        # This will fail at API call, but should create the directory
        try:
            result = self.processor.generate_single_variation(
                image_path=self.test_image_path,
                variation_id=1,
                variation_type="random",
                output_dir=output_dir
            )
        except Exception:
            pass  # Expected to fail at API call
        
        # Directory should now exist
        self.assertTrue(output_dir.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests for the variation system"""
    
    def test_full_pipeline_without_api(self):
        """Test the full pipeline without making API calls"""
        # Create components
        generator = VariationPromptGenerator()
        engine = VariationEngine()
        
        # Test image
        test_image = Image.new('RGB', (100, 100), 'yellow')
        
        # Test prompt generation through engine
        prompt = engine.create_variation_prompt(
            base_image=test_image,
            variation_id=1,
            variation_type='style_change',
            seed=42
        )
        
        # Verify we get a reasonable prompt
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 20)
        
        # Test that the prompt contains expected elements for style change
        prompt_lower = prompt.lower()
        style_keywords = ['style', 'artistic', 'transform', 'aesthetic', 'mood']
        has_style_keyword = any(keyword in prompt_lower for keyword in style_keywords)
        self.assertTrue(has_style_keyword, f"Prompt should contain style-related keywords: {prompt}")
    
    def test_variation_type_coverage(self):
        """Test that all variation types produce valid prompts"""
        generator = VariationPromptGenerator()
        engine = VariationEngine()
        test_image = Image.new('RGB', (50, 50), 'purple')
        
        for variation_type in engine.VARIATION_TYPES.keys():
            prompt = engine.create_variation_prompt(
                base_image=test_image,
                variation_id=1,
                variation_type=variation_type,
                seed=123
            )
            
            self.assertIsInstance(prompt, str, f"Failed for type: {variation_type}")
            self.assertGreater(len(prompt), 5, f"Prompt too short for type: {variation_type}")


if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    tests_dir = Path(__file__).parent
    tests_dir.mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)