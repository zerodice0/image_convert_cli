#!/usr/bin/env python3
"""
Performance benchmark for image variation functionality
"""

import time
import statistics
import tempfile
from pathlib import Path
from PIL import Image
import psutil
import os
import json
import sys
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from batch_nanobanana_core import (
    VariationEngine, 
    VariationPromptGenerator,
    ImageVariationProcessor
)


class VariationBenchmark:
    """Performance benchmark for image variation system"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def benchmark_prompt_generation(self, iterations: int = 1000):
        """Benchmark prompt generation performance"""
        print(f"🔄 Benchmarking prompt generation ({iterations} iterations)...")
        
        generator = VariationPromptGenerator()
        engine = VariationEngine()
        test_image = Image.new('RGB', (512, 512), 'blue')
        
        variation_types = list(engine.VARIATION_TYPES.keys())
        
        # Benchmark different variation types
        type_results = {}
        
        for variation_type in variation_types:
            times = []
            
            for i in range(iterations // len(variation_types)):
                start_time = time.perf_counter()
                
                prompt = engine.create_variation_prompt(
                    base_image=test_image,
                    variation_id=i,
                    variation_type=variation_type,
                    seed=42
                )
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            type_results[variation_type] = {
                'avg_time': statistics.mean(times) * 1000,  # ms
                'min_time': min(times) * 1000,
                'max_time': max(times) * 1000,
                'std_dev': statistics.stdev(times) * 1000,
                'iterations': len(times)
            }
        
        self.results['prompt_generation'] = type_results
        print(f"✅ Prompt generation benchmark completed")
    
    def benchmark_image_processing(self, image_sizes: List[tuple]):
        """Benchmark image processing performance"""
        print(f"🖼️ Benchmarking image processing...")
        
        processing_results = {}
        
        for size in image_sizes:
            print(f"  Testing {size[0]}x{size[1]} images...")
            
            # Create test image
            test_image = Image.new('RGB', size, (100, 150, 200))
            image_path = self.temp_dir / f"test_{size[0]}x{size[1]}.png"
            test_image.save(image_path)
            
            try:
                # Memory usage before
                memory_before = self.process.memory_info().rss / 1024 / 1024
                
                # Time image loading and basic processing
                start_time = time.perf_counter()
                
                # Simulate image processing operations
                loaded_image = Image.open(image_path)
                resized = loaded_image.resize((size[0] // 2, size[1] // 2))
                converted = loaded_image.convert('RGB')
                
                end_time = time.perf_counter()
                memory_after = self.process.memory_info().rss / 1024 / 1024
                
                processing_results[f"{size[0]}x{size[1]}"] = {
                    'processing_time': (end_time - start_time) * 1000,  # ms
                    'memory_usage': memory_after - memory_before,  # MB
                    'image_size_mb': image_path.stat().st_size / 1024 / 1024
                }
                
            finally:
                # Cleanup
                if image_path.exists():
                    image_path.unlink()
        
        self.results['image_processing'] = processing_results
        print(f"✅ Image processing benchmark completed")
    
    def benchmark_quality_analysis(self, iterations: int = 100):
        """Benchmark quality analysis performance"""
        print(f"🔍 Benchmarking quality analysis...")
        
        try:
            from variation_advanced import VariationQualityAnalyzer
            analyzer = VariationQualityAnalyzer()
            
            # Create test images
            img1 = Image.new('RGB', (512, 512), 'red')
            img2 = Image.new('RGB', (512, 512), 'blue')
            img3 = Image.new('RGB', (512, 512), 'green')
            variations = [img2, img3]
            
            times = []
            for i in range(iterations):
                start_time = time.perf_counter()
                
                metrics = analyzer.analyze_variation_quality(img1, img2, variations)
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            self.results['quality_analysis'] = {
                'avg_time': statistics.mean(times) * 1000,  # ms
                'min_time': min(times) * 1000,
                'max_time': max(times) * 1000,
                'std_dev': statistics.stdev(times) * 1000,
                'throughput': len(times) / sum(times),  # analyses per second
                'iterations': iterations
            }
            
            print(f"✅ Quality analysis benchmark completed")
            
        except ImportError:
            print("⚠️ Advanced quality analysis not available")
            self.results['quality_analysis'] = {
                'status': 'unavailable',
                'reason': 'variation_advanced module not found'
            }
    
    def benchmark_memory_usage(self, batch_sizes: List[int]):
        """Benchmark memory usage with different batch sizes"""
        print(f"💾 Benchmarking memory usage...")
        
        memory_results = {}
        
        for batch_size in batch_sizes:
            print(f"  Testing batch size: {batch_size}")
            
            # Initial memory
            initial_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Create batch of images
            images = []
            for i in range(batch_size):
                img = Image.new('RGB', (1024, 1024), (i * 25 % 255, i * 35 % 255, i * 45 % 255))
                images.append(img)
            
            # Peak memory
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Process images (simulate variation operations)
            processed = []
            for img in images:
                # Simulate processing
                resized = img.resize((512, 512))
                converted = resized.convert('RGB')
                processed.append(converted)
            
            # Final memory
            final_memory = self.process.memory_info().rss / 1024 / 1024
            
            memory_results[f"batch_{batch_size}"] = {
                'initial_memory': initial_memory,
                'peak_memory': peak_memory,
                'final_memory': final_memory,
                'memory_increase': peak_memory - initial_memory,
                'memory_per_image': (peak_memory - initial_memory) / batch_size if batch_size > 0 else 0
            }
            
            # Cleanup
            del images
            del processed
        
        self.results['memory_usage'] = memory_results
        print(f"✅ Memory usage benchmark completed")
    
    def benchmark_concurrent_processing(self, worker_counts: List[int]):
        """Benchmark concurrent processing simulation"""
        print(f"🔀 Benchmarking concurrent processing...")
        
        import threading
        import queue
        
        def worker(task_queue: queue.Queue, result_queue: queue.Queue):
            """Worker function for concurrent processing"""
            engine = VariationEngine()
            test_image = Image.new('RGB', (256, 256), 'white')
            
            while True:
                try:
                    task_id = task_queue.get(timeout=1)
                    
                    # Simulate processing
                    start_time = time.perf_counter()
                    prompt = engine.create_variation_prompt(
                        base_image=test_image,
                        variation_id=task_id,
                        variation_type='random'
                    )
                    end_time = time.perf_counter()
                    
                    result_queue.put({
                        'task_id': task_id,
                        'processing_time': end_time - start_time,
                        'success': True
                    })
                    
                    task_queue.task_done()
                    
                except queue.Empty:
                    break
                except Exception as e:
                    result_queue.put({
                        'task_id': task_id,
                        'error': str(e),
                        'success': False
                    })
        
        concurrent_results = {}
        total_tasks = 100
        
        for worker_count in worker_counts:
            print(f"  Testing {worker_count} workers...")
            
            task_queue = queue.Queue()
            result_queue = queue.Queue()
            
            # Add tasks
            for i in range(total_tasks):
                task_queue.put(i)
            
            # Start workers
            threads = []
            start_time = time.perf_counter()
            
            for _ in range(worker_count):
                thread = threading.Thread(target=worker, args=(task_queue, result_queue))
                thread.start()
                threads.append(thread)
            
            # Wait for completion
            task_queue.join()
            
            # Stop workers
            for thread in threads:
                thread.join(timeout=1)
            
            end_time = time.perf_counter()
            
            # Collect results
            results = []
            while not result_queue.empty():
                results.append(result_queue.get())
            
            successful = sum(1 for r in results if r.get('success', False))
            total_time = end_time - start_time
            
            concurrent_results[f"{worker_count}_workers"] = {
                'total_time': total_time,
                'successful_tasks': successful,
                'failed_tasks': len(results) - successful,
                'throughput': successful / total_time,
                'avg_time_per_task': total_time / successful if successful > 0 else 0
            }
        
        self.results['concurrent_processing'] = concurrent_results
        print(f"✅ Concurrent processing benchmark completed")
    
    def generate_report(self) -> str:
        """Generate comprehensive benchmark report"""
        report = "# 이미지 변형 성능 벤치마크 리포트\n\n"
        report += f"**실행 시간**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**시스템 정보**: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total // 1024**3:.1f}GB RAM\n\n"
        
        # Prompt generation results
        if 'prompt_generation' in self.results:
            report += "## 📝 프롬프트 생성 성능\n\n"
            for vtype, metrics in self.results['prompt_generation'].items():
                report += f"### {vtype}\n"
                report += f"- 평균 시간: {metrics['avg_time']:.2f}ms\n"
                report += f"- 최소 시간: {metrics['min_time']:.2f}ms\n"
                report += f"- 최대 시간: {metrics['max_time']:.2f}ms\n"
                report += f"- 표준편차: {metrics['std_dev']:.2f}ms\n"
                report += f"- 반복 횟수: {metrics['iterations']}\n\n"
        
        # Image processing results
        if 'image_processing' in self.results:
            report += "## 🖼️ 이미지 처리 성능\n\n"
            for size, metrics in self.results['image_processing'].items():
                report += f"### {size}\n"
                report += f"- 처리 시간: {metrics['processing_time']:.2f}ms\n"
                report += f"- 메모리 사용: {metrics['memory_usage']:.1f}MB\n"
                report += f"- 이미지 크기: {metrics['image_size_mb']:.1f}MB\n\n"
        
        # Quality analysis results
        if 'quality_analysis' in self.results:
            qa = self.results['quality_analysis']
            if qa.get('status') == 'unavailable':
                report += "## 🔍 품질 분석 성능\n\n"
                report += f"⚠️ {qa.get('reason', '사용할 수 없음')}\n\n"
            else:
                report += "## 🔍 품질 분석 성능\n\n"
                report += f"- 평균 시간: {qa['avg_time']:.2f}ms\n"
                report += f"- 최소 시간: {qa['min_time']:.2f}ms\n"
                report += f"- 최대 시간: {qa['max_time']:.2f}ms\n"
                report += f"- 처리량: {qa['throughput']:.1f} 분석/초\n"
                report += f"- 반복 횟수: {qa['iterations']}\n\n"
        
        # Memory usage results
        if 'memory_usage' in self.results:
            report += "## 💾 메모리 사용량\n\n"
            for batch, metrics in self.results['memory_usage'].items():
                report += f"### {batch.replace('_', ' ').title()}\n"
                report += f"- 초기 메모리: {metrics['initial_memory']:.1f}MB\n"
                report += f"- 최대 메모리: {metrics['peak_memory']:.1f}MB\n"
                report += f"- 메모리 증가: {metrics['memory_increase']:.1f}MB\n"
                report += f"- 이미지당 메모리: {metrics['memory_per_image']:.2f}MB\n\n"
        
        # Concurrent processing results
        if 'concurrent_processing' in self.results:
            report += "## 🔀 동시 처리 성능\n\n"
            for config, metrics in self.results['concurrent_processing'].items():
                report += f"### {config.replace('_', ' ').title()}\n"
                report += f"- 총 시간: {metrics['total_time']:.2f}초\n"
                report += f"- 성공한 작업: {metrics['successful_tasks']}\n"
                report += f"- 실패한 작업: {metrics['failed_tasks']}\n"
                report += f"- 처리량: {metrics['throughput']:.1f} 작업/초\n"
                report += f"- 작업당 평균 시간: {metrics['avg_time_per_task']:.2f}초\n\n"
        
        # Performance recommendations
        report += "## 📊 성능 권장사항\n\n"
        report += self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> str:
        """Generate performance recommendations based on results"""
        recommendations = []
        
        # Analyze prompt generation
        if 'prompt_generation' in self.results:
            avg_times = [metrics['avg_time'] for metrics in self.results['prompt_generation'].values()]
            max_avg_time = max(avg_times)
            
            if max_avg_time > 50:  # ms
                recommendations.append("- 프롬프트 생성 시간이 길어 캐싱 시스템 도입을 권장합니다.")
            else:
                recommendations.append("- 프롬프트 생성 성능이 양호합니다.")
        
        # Analyze memory usage
        if 'memory_usage' in self.results:
            max_increase = max(
                metrics['memory_increase'] 
                for metrics in self.results['memory_usage'].values()
            )
            
            if max_increase > 1000:  # MB
                recommendations.append("- 메모리 사용량이 높아 이미지 크기 최적화를 권장합니다.")
            elif max_increase > 500:
                recommendations.append("- 메모리 사용량이 보통 수준입니다. 배치 크기 조정을 고려하세요.")
            else:
                recommendations.append("- 메모리 사용량이 효율적입니다.")
        
        # Analyze concurrent processing
        if 'concurrent_processing' in self.results:
            throughputs = [
                metrics['throughput'] 
                for metrics in self.results['concurrent_processing'].values()
            ]
            
            if len(throughputs) > 1:
                best_throughput = max(throughputs)
                best_config = max(
                    self.results['concurrent_processing'].items(),
                    key=lambda x: x[1]['throughput']
                )[0]
                
                recommendations.append(f"- 최적 동시 처리 설정: {best_config} (처리량: {best_throughput:.1f} 작업/초)")
        
        if not recommendations:
            recommendations.append("- 전체적으로 안정적인 성능을 보입니다.")
        
        return "\n".join(recommendations) + "\n"
    
    def save_results(self, filepath: Path):
        """Save benchmark results to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


def main():
    """Run comprehensive benchmark suite"""
    print("🚀 이미지 변형 성능 벤치마크 시작\n")
    
    benchmark = VariationBenchmark()
    
    try:
        # Run benchmarks
        benchmark.benchmark_prompt_generation(iterations=500)
        benchmark.benchmark_image_processing([(512, 512), (1024, 1024), (2048, 2048)])
        benchmark.benchmark_quality_analysis(iterations=50)
        benchmark.benchmark_memory_usage([1, 5, 10, 20])
        benchmark.benchmark_concurrent_processing([1, 2, 4, 8])
        
        # Generate and save report
        report = benchmark.generate_report()
        print("\n" + "="*60)
        print("📈 벤치마크 결과")
        print("="*60)
        print(report)
        
        # Save to files
        results_dir = Path(__file__).parent.parent / "benchmark_results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        report_file = results_dir / f"benchmark_report_{timestamp}.md"
        results_file = results_dir / f"benchmark_results_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        benchmark.save_results(results_file)
        
        print(f"\n💾 결과 저장됨:")
        print(f"  리포트: {report_file}")
        print(f"  데이터: {results_file}")
        
    finally:
        benchmark.cleanup()


if __name__ == '__main__':
    main()