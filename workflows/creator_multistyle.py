#!/usr/bin/env python3
"""
크리에이터를 위한 멀티 스타일 테스트 워크플로우
하나의 이미지로 여러 스타일을 테스트하고 비교할 수 있습니다.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime
import shutil


class CreatorMultiStyleTester:
    """크리에이터를 위한 멀티 스타일 테스트 도구"""
    
    def __init__(self):
        self.base_styles = {
            "artistic": "이 이미지를 예술적이고 창의적인 작품으로 변환해주세요",
            "cinematic": "이 이미지를 영화 같은 장면으로 변환해주세요",
            "dreamy": "이 이미지를 꿈꾸는 듯한 환상적인 분위기로 변환해주세요",
            "vintage": "이 이미지를 따뜻한 빈티지 필름 카메라 스타일로 변환해주세요",
            "futuristic": "이 이미지를 미래적이고 사이버틱한 스타일로 변환해주세요",
            "watercolor": "이 이미지를 부드러운 수채화 스타일로 변환해주세요",
            "oil_painting": "이 이미지를 고전적인 유화 스타일로 변환해주세요",
            "anime": "이 이미지를 애니메이션 스타일로 변환해주세요",
            "sketch": "이 이미지를 연필 스케치 스타일로 변환해주세요",
            "pop_art": "이 이미지를 생동감 있는 팝 아트 스타일로 변환해주세요"
        }
        
        self.mood_modifiers = {
            "bright": "밝고 생동감 있게",
            "dark": "어둡고 신비로운 분위기로",
            "warm": "따뜻한 색조로",
            "cool": "차가운 색조로",
            "dramatic": "드라마틱하고 강렬하게",
            "peaceful": "평화롭고 고요하게",
            "energetic": "역동적이고 활기차게",
            "melancholic": "감성적이고 우울한 분위기로"
        }
    
    def generate_style_combinations(self, base_styles=None, moods=None, custom_prompts=None):
        """스타일 조합 생성"""
        combinations = []
        
        # 기본 스타일
        if base_styles:
            for style in base_styles:
                if style in self.base_styles:
                    combinations.append({
                        "name": style,
                        "prompt": self.base_styles[style]
                    })
        
        # 스타일 + 무드 조합
        if base_styles and moods:
            for style in base_styles:
                if style in self.base_styles:
                    for mood in moods:
                        if mood in self.mood_modifiers:
                            combined_name = f"{style}_{mood}"
                            combined_prompt = f"{self.base_styles[style]}. {self.mood_modifiers[mood]} 만들어주세요."
                            combinations.append({
                                "name": combined_name,
                                "prompt": combined_prompt
                            })
        
        # 커스텀 프롬프트
        if custom_prompts:
            for i, prompt in enumerate(custom_prompts):
                combinations.append({
                    "name": f"custom_{i+1}",
                    "prompt": prompt
                })
        
        return combinations
    
    def create_test_structure(self, base_dir, image_file, combinations):
        """테스트용 디렉토리 구조 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_dir = Path(base_dir) / f"multistyle_test_{timestamp}"
        
        # 메인 디렉토리 생성
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # 원본 이미지 복사
        original_dir = test_dir / "original"
        original_dir.mkdir(exist_ok=True)
        shutil.copy2(image_file, original_dir / Path(image_file).name)
        
        # 각 스타일별 디렉토리 생성
        style_dirs = {}
        for combo in combinations:
            style_dir = test_dir / combo["name"]
            style_dir.mkdir(exist_ok=True)
            style_dirs[combo["name"]] = style_dir
        
        # 결과 비교용 디렉토리
        comparison_dir = test_dir / "comparison"
        comparison_dir.mkdir(exist_ok=True)
        
        # 설정 파일 저장
        config = {
            "timestamp": timestamp,
            "original_image": str(image_file),
            "combinations": combinations,
            "directories": {name: str(path) for name, path in style_dirs.items()}
        }
        
        with open(test_dir / "test_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return test_dir, style_dirs, original_dir
    
    def run_style_test(self, image_file, combinations, output_dir=None, concurrent=1):
        """멀티 스타일 테스트 실행"""
        if output_dir is None:
            output_dir = Path.cwd() / "multistyle_results"
        
        # 테스트 구조 생성
        test_dir, style_dirs, original_dir = self.create_test_structure(
            output_dir, image_file, combinations
        )
        
        print(f"🎨 멀티 스타일 테스트 시작")
        print(f"📁 테스트 디렉토리: {test_dir}")
        print(f"🖼️  원본 이미지: {Path(image_file).name}")
        print(f"🎯 테스트할 스타일: {len(combinations)}개")
        print("=" * 50)
        
        results = []
        
        for i, combo in enumerate(combinations, 1):
            print(f"[{i}/{len(combinations)}] 처리 중: {combo['name']}")
            print(f"💬 프롬프트: {combo['prompt']}")
            
            # CLI 명령어 구성
            cmd = [
                sys.executable, "batch_nanobanana_cli.py",
                "--input-dir", str(original_dir),
                "--output-dir", str(style_dirs[combo['name']]),
                "--prompt", combo['prompt'],
                "--concurrent", str(concurrent),
                "--quiet"
            ]
            
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ 완료: {combo['name']}")
                results.append({
                    "style": combo['name'],
                    "prompt": combo['prompt'],
                    "status": "success",
                    "output_dir": str(style_dirs[combo['name']])
                })
            except subprocess.CalledProcessError as e:
                print(f"❌ 실패: {combo['name']} - {e}")
                results.append({
                    "style": combo['name'],
                    "prompt": combo['prompt'],
                    "status": "failed",
                    "error": str(e)
                })
            
            print("-" * 30)
        
        # 결과 저장
        results_file = test_dir / "results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 성공한 결과들을 비교 폴더에 복사
        self.create_comparison_grid(test_dir, results)
        
        print(f"\n🎉 멀티 스타일 테스트 완료!")
        print(f"📊 성공: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
        print(f"📁 결과 위치: {test_dir}")
        
        # HTML 비교 페이지 생성
        self.create_comparison_html(test_dir, results, Path(image_file).name)
        
        return test_dir, results
    
    def create_comparison_grid(self, test_dir, results):
        """결과 비교를 위한 그리드 생성"""
        comparison_dir = test_dir / "comparison"
        
        # 성공한 결과들 복사
        for result in results:
            if result['status'] == 'success':
                source_dir = Path(result['output_dir'])
                generated_files = list(source_dir.glob("*_generated.*"))
                
                for file in generated_files:
                    new_name = f"{result['style']}_{file.name}"
                    shutil.copy2(file, comparison_dir / new_name)
    
    def create_comparison_html(self, test_dir, results, original_name):
        """결과 비교를 위한 HTML 페이지 생성"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>스타일 비교 - {original_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card img {{
            width: 100%;
            height: 250px;
            object-fit: cover;
        }}
        .card-content {{
            padding: 15px;
        }}
        .style-name {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 8px;
            color: #333;
        }}
        .prompt {{
            font-size: 0.9em;
            color: #666;
            line-height: 1.4;
        }}
        .original {{
            border: 3px solid #4CAF50;
        }}
        .failed {{
            background-color: #ffebee;
            border: 1px solid #f44336;
        }}
        .failed-text {{
            color: #f44336;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 스타일 비교 결과</h1>
        <h2>원본: {original_name}</h2>
        <p>생성 시간: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}</p>
    </div>
    
    <div class="grid">
"""
        
        # 원본 이미지
        original_dir = test_dir / "original"
        original_files = list(original_dir.glob("*"))
        if original_files:
            original_file = original_files[0]
            html_content += f"""
        <div class="card original">
            <img src="original/{original_file.name}" alt="원본">
            <div class="card-content">
                <div class="style-name">🖼️ 원본 이미지</div>
                <div class="prompt">변환 전 원본 이미지입니다.</div>
            </div>
        </div>
"""
        
        # 각 스타일 결과
        for result in results:
            if result['status'] == 'success':
                # 생성된 파일 찾기
                style_dir = Path(result['output_dir'])
                generated_files = list(style_dir.glob("*_generated.*"))
                
                if generated_files:
                    generated_file = generated_files[0]
                    relative_path = f"{result['style']}/{generated_file.name}"
                    html_content += f"""
        <div class="card">
            <img src="{relative_path}" alt="{result['style']}">
            <div class="card-content">
                <div class="style-name">🎨 {result['style'].replace('_', ' ').title()}</div>
                <div class="prompt">{result['prompt']}</div>
            </div>
        </div>
"""
            else:
                html_content += f"""
        <div class="card failed">
            <div class="card-content">
                <div class="style-name failed-text">❌ {result['style'].replace('_', ' ').title()}</div>
                <div class="prompt">{result['prompt']}</div>
                <div class="prompt" style="color: #f44336; margin-top: 10px;">
                    처리 실패: {result.get('error', '알 수 없는 오류')}
                </div>
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        # HTML 파일 저장
        html_file = test_dir / "comparison.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"📊 비교 페이지 생성: {html_file}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="크리에이터 멀티 스타일 테스터")
    parser.add_argument("image", help="테스트할 이미지 파일")
    parser.add_argument("--styles", nargs="+", help="테스트할 기본 스타일들")
    parser.add_argument("--moods", nargs="+", help="적용할 무드들")
    parser.add_argument("--custom", nargs="+", help="커스텀 프롬프트들")
    parser.add_argument("--output", "-o", help="출력 디렉토리")
    parser.add_argument("--concurrent", "-c", type=int, default=1, help="동시 처리 수")
    parser.add_argument("--list-styles", action="store_true", help="사용 가능한 스타일 목록 표시")
    parser.add_argument("--list-moods", action="store_true", help="사용 가능한 무드 목록 표시")
    parser.add_argument("--preset", choices=["basic", "artistic", "moody", "all"], 
                       help="미리 정의된 스타일 세트")
    
    args = parser.parse_args()
    
    tester = CreatorMultiStyleTester()
    
    # 목록 표시
    if args.list_styles:
        print("🎨 사용 가능한 기본 스타일:")
        for style, desc in tester.base_styles.items():
            print(f"  {style}: {desc}")
        return 0
    
    if args.list_moods:
        print("🌈 사용 가능한 무드:")
        for mood, desc in tester.mood_modifiers.items():
            print(f"  {mood}: {desc}")
        return 0
    
    # 이미지 파일 확인
    if not os.path.exists(args.image):
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {args.image}")
        return 1
    
    # 프리셋 설정
    if args.preset:
        presets = {
            "basic": {
                "styles": ["artistic", "vintage", "cinematic"],
                "moods": None
            },
            "artistic": {
                "styles": ["watercolor", "oil_painting", "sketch", "pop_art"],
                "moods": None
            },
            "moody": {
                "styles": ["cinematic", "dreamy"],
                "moods": ["dramatic", "peaceful", "melancholic"]
            },
            "all": {
                "styles": list(tester.base_styles.keys())[:5],  # 처음 5개만
                "moods": ["bright", "dark", "warm"]
            }
        }
        
        preset_config = presets[args.preset]
        styles = preset_config["styles"]
        moods = preset_config["moods"]
    else:
        styles = args.styles
        moods = args.moods
    
    # 스타일 조합 생성
    combinations = tester.generate_style_combinations(
        base_styles=styles,
        moods=moods,
        custom_prompts=args.custom
    )
    
    if not combinations:
        print("❌ 테스트할 스타일이 없습니다.")
        print("--styles, --moods, --custom 또는 --preset 옵션을 사용하세요.")
        print("사용 가능한 옵션: --list-styles, --list-moods")
        return 1
    
    print(f"🎯 생성된 스타일 조합 ({len(combinations)}개):")
    for combo in combinations:
        print(f"  - {combo['name']}")
    print()
    
    # 확인
    try:
        response = input("계속하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("취소되었습니다.")
            return 0
    except KeyboardInterrupt:
        print("\n취소되었습니다.")
        return 0
    
    # 테스트 실행
    try:
        test_dir, results = tester.run_style_test(
            image_file=args.image,
            combinations=combinations,
            output_dir=args.output,
            concurrent=args.concurrent
        )
        
        # 결과 폴더 열기 (시스템에 따라)
        if sys.platform == "win32":
            os.startfile(test_dir)
        elif sys.platform == "darwin":
            subprocess.run(["open", test_dir])
        else:
            subprocess.run(["xdg-open", test_dir])
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자에 의해 중단되었습니다.")
        return 0
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())