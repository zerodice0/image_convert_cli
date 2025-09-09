#!/usr/bin/env python3
"""
최종 배포 전 검증 스크립트
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import time
import importlib.util
from typing import Dict, List, Any


class FinalValidator:
    """Final deployment validation system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.info = []
        
        print("🚀 NanoBanana 이미지 변형 기능 최종 검증 시작")
        print(f"📁 프로젝트 경로: {self.project_root}")
        print("="*60)
    
    def validate_project_structure(self):
        """Validate project structure and required files"""
        print("📂 프로젝트 구조 검증 중...")
        
        required_files = [
            'batch_nanobanana_core.py',
            'batch_nanobanana_gui.py', 
            'batch_nanobanana_cli.py',
            'variation_advanced.py',
            'README.md'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.errors.append(f"필수 파일 누락: {file_path}")
            elif full_path.stat().st_size == 0:
                self.errors.append(f"빈 파일: {file_path}")
            else:
                self.info.append(f"✓ {file_path} 존재 확인")
        
        # Check test directories
        test_dirs = ['tests', 'benchmarks', 'docs']
        for test_dir in test_dirs:
            dir_path = self.project_root / test_dir
            if not dir_path.exists():
                self.warnings.append(f"디렉토리 누락: {test_dir}")
            else:
                self.info.append(f"✓ {test_dir}/ 디렉토리 확인")
        
        print("✅ 프로젝트 구조 검증 완료")
    
    def validate_dependencies(self):
        """Validate required and optional dependencies"""
        print("📦 의존성 검증 중...")
        
        required_deps = {
            'PIL': 'Pillow',
            'google': 'google-generativeai',
            'tkinter': 'tkinter (built-in)',
            'pathlib': 'pathlib (built-in)',
            'json': 'json (built-in)',
            'logging': 'logging (built-in)'
        }
        
        optional_deps = {
            'cv2': 'opencv-python',
            'skimage': 'scikit-image', 
            'imagehash': 'imagehash',
            'psutil': 'psutil',
            'pytest': 'pytest'
        }
        
        # Check required dependencies
        for module, package in required_deps.items():
            try:
                importlib.import_module(module)
                self.info.append(f"✓ {package} 사용 가능")
            except ImportError:
                self.errors.append(f"필수 의존성 누락: {package}")
        
        # Check optional dependencies
        optional_available = 0
        for module, package in optional_deps.items():
            try:
                importlib.import_module(module)
                self.info.append(f"✓ {package} 사용 가능 (선택적)")
                optional_available += 1
            except ImportError:
                self.warnings.append(f"선택적 의존성 누락: {package}")
        
        if optional_available >= len(optional_deps) * 0.7:
            self.info.append(f"✓ 선택적 의존성 {optional_available}/{len(optional_deps)}개 사용 가능")
        else:
            self.warnings.append(f"선택적 의존성이 부족합니다 ({optional_available}/{len(optional_deps)})")
        
        print("✅ 의존성 검증 완료")
    
    def run_tests(self):
        """Run comprehensive test suite"""
        print("🧪 테스트 실행 중...")
        
        test_files = [
            'tests/test_variation_core.py',
            'tests/test_variation_advanced.py',
            'tests/test_variation_integration.py'
        ]
        
        total_passed = 0
        total_failed = 0
        
        for test_file in test_files:
            test_path = self.project_root / test_file
            if not test_path.exists():
                self.warnings.append(f"테스트 파일 누락: {test_file}")
                continue
            
            try:
                print(f"  실행 중: {test_file}")
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', 
                    str(test_path), '-v', '--tb=short'
                ], capture_output=True, text=True, cwd=self.project_root, timeout=300)
                
                if result.returncode == 0:
                    # Parse test results
                    output_lines = result.stdout.split('\n')
                    for line in output_lines:
                        if 'passed' in line and 'failed' in line:
                            # Extract numbers from pytest summary
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == 'passed':
                                    total_passed += int(parts[i-1])
                                elif part == 'failed':
                                    total_failed += int(parts[i-1])
                    
                    self.info.append(f"✓ {test_file} 테스트 통과")
                else:
                    self.errors.append(f"테스트 실패: {test_file}")
                    if result.stderr:
                        self.errors.append(f"  오류: {result.stderr[:200]}...")
                        
            except subprocess.TimeoutExpired:
                self.errors.append(f"테스트 타임아웃: {test_file}")
            except Exception as e:
                self.errors.append(f"테스트 실행 오류: {test_file} - {str(e)}")
        
        if total_passed > 0:
            self.info.append(f"✓ 총 {total_passed}개 테스트 통과")
        if total_failed > 0:
            self.errors.append(f"총 {total_failed}개 테스트 실패")
        
        print("✅ 테스트 실행 완료")
    
    def validate_imports(self):
        """Validate that core modules can be imported"""
        print("🔧 모듈 임포트 검증 중...")
        
        core_modules = [
            'batch_nanobanana_core',
            'batch_nanobanana_gui',
            'batch_nanobanana_cli',
            'variation_advanced'
        ]
        
        for module in core_modules:
            try:
                # Change to project directory for import
                old_path = sys.path[:]
                sys.path.insert(0, str(self.project_root))
                
                importlib.import_module(module)
                self.info.append(f"✓ {module} 임포트 성공")
                
            except Exception as e:
                self.errors.append(f"모듈 임포트 실패: {module} - {str(e)[:100]}")
            finally:
                sys.path = old_path
        
        print("✅ 모듈 임포트 검증 완료")
    
    def validate_documentation(self):
        """Validate documentation completeness"""
        print("📚 문서 검증 중...")
        
        required_docs = [
            'docs/IMAGE_VARIATION_GUIDE.md',
            'docs/feature_image_variation/README.md',
            'docs/feature_image_variation/phase1_architecture_design.md',
            'docs/feature_image_variation/phase2_gui_extension.md',
            'docs/feature_image_variation/phase3_cli_extension.md', 
            'docs/feature_image_variation/phase4_advanced_features.md',
            'docs/feature_image_variation/phase5_testing_documentation.md'
        ]
        
        for doc in required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                self.warnings.append(f"문서 누락: {doc}")
            elif doc_path.stat().st_size < 500:  # At least 500 bytes
                self.warnings.append(f"문서가 너무 짧음: {doc}")
            else:
                self.info.append(f"✓ {doc} 문서 확인")
        
        # Check README
        readme_path = self.project_root / 'README.md'
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            if '이미지 변형' in content or 'variation' in content.lower():
                self.info.append("✓ README에 변형 기능 정보 포함")
            else:
                self.warnings.append("README에 변형 기능 정보 부족")
        
        print("✅ 문서 검증 완료")
    
    def run_performance_benchmark(self):
        """Run basic performance benchmark"""
        print("⚡ 성능 벤치마크 실행 중...")
        
        benchmark_path = self.project_root / 'benchmarks' / 'variation_benchmark.py'
        if not benchmark_path.exists():
            self.warnings.append("벤치마크 스크립트 누락")
            return
        
        try:
            # Add timeout for benchmark
            print("  기본 성능 테스트 실행 중... (최대 60초)")
            result = subprocess.run([
                sys.executable, str(benchmark_path)
            ], capture_output=True, text=True, cwd=self.project_root, timeout=60)
            
            if result.returncode == 0:
                self.info.append("✓ 성능 벤치마크 실행 성공")
                
                # Check for performance indicators in output
                output = result.stdout.lower()
                if 'completed' in output:
                    self.info.append("✓ 벤치마크 정상 완료")
                if 'ms' in output:
                    self.info.append("✓ 성능 메트릭 수집됨")
                    
            else:
                self.warnings.append("성능 벤치마크 실행 실패")
                if result.stderr:
                    self.warnings.append(f"  오류: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            self.warnings.append("성능 벤치마크 타임아웃 (60초 초과)")
        except Exception as e:
            self.warnings.append(f"벤치마크 실행 오류: {str(e)}")
        
        print("✅ 성능 벤치마크 완료")
    
    def validate_configuration(self):
        """Validate configuration and environment"""
        print("⚙️ 설정 검증 중...")
        
        # Check environment variables
        env_vars = ['GEMINI_API_KEY', 'GOOGLE_API_KEY']
        api_key_found = False
        
        for var in env_vars:
            if os.getenv(var):
                api_key_found = True
                self.info.append(f"✓ {var} 환경변수 설정됨")
                break
        
        if not api_key_found:
            self.warnings.append("Gemini API 키 환경변수 미설정 (GEMINI_API_KEY 또는 GOOGLE_API_KEY)")
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.info.append(f"✓ Python {python_version.major}.{python_version.minor} 버전 호환")
        else:
            self.errors.append(f"Python 버전 부족: {python_version.major}.{python_version.minor} (최소 3.8 필요)")
        
        # Check disk space (at least 1GB free)
        try:
            import shutil
            free_space = shutil.disk_usage(self.project_root).free / (1024**3)  # GB
            if free_space >= 1.0:
                self.info.append(f"✓ 디스크 여유공간 충분 ({free_space:.1f}GB)")
            else:
                self.warnings.append(f"디스크 여유공간 부족 ({free_space:.1f}GB)")
        except:
            self.warnings.append("디스크 공간 확인 불가")
        
        print("✅ 설정 검증 완료")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        status = 'PASS' if len(self.errors) == 0 else 'FAIL'
        
        report = {
            'validation_status': status,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'project_root': str(self.project_root),
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_info': len(self.info)
            }
        }
        
        return report
    
    def run_validation(self) -> bool:
        """Run complete validation suite"""
        validation_steps = [
            self.validate_project_structure,
            self.validate_dependencies,
            self.validate_imports,
            self.validate_configuration,
            self.run_tests,
            self.validate_documentation,
            self.run_performance_benchmark
        ]
        
        for step in validation_steps:
            try:
                step()
                print()  # Add spacing between steps
            except Exception as e:
                self.errors.append(f"검증 단계 실패: {step.__name__} - {str(e)}")
                print(f"❌ {step.__name__} 실패: {str(e)}\n")
        
        # Generate final report
        report = self.generate_report()
        
        print("="*60)
        print("📊 최종 검증 결과")
        print("="*60)
        
        if report['validation_status'] == 'PASS':
            print("🎉 검증 성공! 이미지 변형 기능 배포 준비 완료")
            print()
            print("✅ 주요 성취사항:")
            for info in self.info[-5:]:  # Show last 5 info items
                print(f"  • {info}")
        else:
            print("❌ 검증 실패! 다음 문제들을 해결하세요:")
            for error in self.errors:
                print(f"  🚨 {error}")
        
        if self.warnings:
            print(f"\n⚠️ 경고사항 ({len(self.warnings)}개):")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... 및 {len(self.warnings)-5}개 추가 경고")
        
        print(f"\n📈 검증 통계:")
        print(f"  • 오류: {report['summary']['total_errors']}개")
        print(f"  • 경고: {report['summary']['total_warnings']}개")
        print(f"  • 정보: {report['summary']['total_info']}개")
        
        # Save detailed report
        try:
            report_file = self.project_root / 'validation_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 상세 리포트 저장됨: {report_file}")
        except Exception as e:
            print(f"⚠️ 리포트 저장 실패: {e}")
        
        return report['validation_status'] == 'PASS'


def main():
    """Main validation entry point"""
    validator = FinalValidator()
    success = validator.run_validation()
    
    print("\n" + "="*60)
    if success:
        print("🚀 이미지 변형 기능이 성공적으로 검증되었습니다!")
        print("배포를 진행할 수 있습니다.")
        exit_code = 0
    else:
        print("🔧 문제를 해결한 후 다시 검증을 실행해주세요.")
        print("자세한 내용은 validation_report.json을 확인하세요.")
        exit_code = 1
    
    print("="*60)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()