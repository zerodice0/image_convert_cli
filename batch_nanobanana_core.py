#!/usr/bin/env python3
"""
Batch NanoBanana Core - Shared Processing Logic
Core image processing functionality shared between GUI and CLI versions
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Callable
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