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
from typing import List, Optional
import logging
from datetime import datetime
import signal

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


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Batch NanoBanana Image Generator - CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with environment variable (RECOMMENDED)
  export GEMINI_API_KEY="your-api-key-here"
  %(prog)s --input-dir ./images --output-dir ./results --prompt "Transform this image"
  
  # With API key as argument (NOT RECOMMENDED - visible in process list)
  %(prog)s --input-dir ./images --output-dir ./results --prompt "Transform this image" --api-key "your-key"
  
  # Dry run mode
  %(prog)s --input-dir ./images --output-dir ./results --prompt "Test prompt" --dry-run
  
  # With config file
  %(prog)s --input-dir ./images --output-dir ./results --prompt "Transform" --config ~/.nanobanana/config
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--input-dir", "-i",
        required=True,
        help="Path to directory containing input images"
    )
    
    parser.add_argument(
        "--output-dir", "-o", 
        required=True,
        help="Path to directory for output images"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Text prompt to send with images to the API"
    )
    
    # API key options
    parser.add_argument(
        "--api-key",
        help="Gemini API key (WARNING: visible in process list. Use GEMINI_API_KEY env var instead)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to config file containing GEMINI_API_KEY=value"
    )
    
    # Optional arguments
    parser.add_argument(
        "--format", "-f",
        default="png",
        choices=["png", "jpg", "jpeg", "webp"],
        help="Output image format (default: png)"
    )
    
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of concurrent processing threads (default: 1)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually doing it"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress confirmation prompts"
    )
    
    parser.add_argument(
        "--log-file", "-l",
        help="Path to log file (default: logs to console only)"
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.quiet and args.verbose:
        print("Error: --quiet and --verbose cannot be used together")
        sys.exit(1)
    
    # Create and run CLI application
    cli = BatchNanoBananaCLI()
    cli.run(args)


if __name__ == "__main__":
    main()