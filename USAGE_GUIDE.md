# 🍌 NanoBanana 사용 가이드 - 완전판

이미지 AI 변환을 위한 완전한 사용 가이드입니다. 당신의 상황에 맞는 최적의 방법을 찾아보세요!

## 🚀 빠른 시작: 어떤 버전을 선택할까요?

### 📊 선택 가이드

| 상황 | 권장 버전 | 이유 |
|------|-----------|------|
| 컴퓨터 초보자 | **GUI 버전** | 클릭만으로 쉽게 사용 |
| 개인 사진 몇 장 | **GUI 버전** | 간단하고 직관적 |
| 블로그/SNS 콘텐츠 | **GUI → CLI** | 처음엔 GUI, 익숙해지면 CLI |
| 회사 업무용 | **CLI 버전** | 자동화와 배치 처리 |
| 개발자/서버 | **CLI 버전** | 스크립트 통합 가능 |
| 수백 장 이상 | **CLI 버전** | 대량 처리에 최적화 |

---

## 📱 GUI 버전 (초보자 추천)

### 🎯 이런 분께 추천
- 컴퓨터 초보자
- 가끔 이미지 처리하는 분
- 복잡한 설정을 원하지 않는 분
- Windows/Mac 사용자

### 📦 설치 방법

**Windows 사용자:**
1. 프로젝트 폴더 압축 해제
2. `install_windows.bat` 더블클릭
3. `run_windows.bat` 더블클릭해서 실행

**Mac 사용자:**
```bash
chmod +x install_mac.sh && ./install_mac.sh
./run_mac.sh
```

### 🖱️ 사용 방법

1. **API Key 입력**
   - [Google AI Studio](https://aistudio.google.com/)에서 API 키 발급
   - 프로그램 상단에 입력

2. **폴더 선택**
   - 입력 폴더: 변환할 이미지들이 있는 폴더
   - 출력 폴더: 결과물을 저장할 폴더

3. **프롬프트 작성**
   ```
   예시: "이 사진을 유화 스타일로 변환해주세요"
   예시: "이 이미지에 마법 같은 효과를 추가해주세요"
   ```

4. **처리 시작** 버튼 클릭

### ✨ GUI 버전 장점
- 클릭만으로 쉬운 사용
- 실시간 진행상황 확인
- 오류 메시지를 팝업으로 확인
- 설정 저장 기능

---

## 💻 CLI 버전 (고급자 추천)

### 🎯 이런 분께 추천
- Linux 사용자
- 자동화가 필요한 분
- 대량 이미지 처리
- 개발자/시스템 관리자

### 📦 설치 방법

```bash
# 1. 가상환경 생성 (권장)
python3 -m venv nano_banana_env
source nano_banana_env/bin/activate

# 2. 패키지 설치
pip install -r requirements_cli.txt

# 3. 실행 권한 부여
chmod +x batch_nanobanana_cli.py
```

### ⌨️ 기본 사용법

```bash
# API 키 설정 (한 번만)
export GEMINI_API_KEY="your-api-key-here"

# 기본 실행
python batch_nanobanana_cli.py \
  --input-dir ./images \
  --output-dir ./results \
  --prompt "이미지를 예술작품으로 변환"
```

### 🔧 고급 옵션

```bash
# 상세 로그와 함께 실행
python batch_nanobanana_cli.py \
  -i ./photos \
  -o ./generated \
  -p "빈티지 스타일로 변환" \
  --verbose \
  --log-file processing.log

# 병렬 처리 (빠른 처리)
python batch_nanobanana_cli.py \
  -i ./images \
  -o ./results \
  -p "아티스틱 변환" \
  --concurrent 4

# 테스트 실행 (실제 처리 없이 미리보기)
python batch_nanobanana_cli.py \
  -i ./test \
  -o ./output \
  -p "테스트 프롬프트" \
  --dry-run
```

### ✨ CLI 버전 장점
- 빠른 대량 처리
- 스크립트 자동화 가능
- 서버 환경에서 실행
- 세밀한 제어 옵션

---

## 🛠️ 실무 워크플로우 예시

### 📸 개인 사진 정리 (GUI)

**상황:** 휴가 사진 20장을 인스타용으로 변환

1. GUI 프로그램 실행
2. API 키 입력
3. 휴가 사진 폴더 선택
4. 인스타용 폴더 생성하여 선택
5. 프롬프트: "이 사진을 밝고 생동감 있는 인스타그램 스타일로 변환"
6. 처리 시작
7. 결과 확인 후 업로드

**예상 시간:** 10-15분

### 🏢 비즈니스 콘텐츠 제작 (CLI)

**상황:** 제품 사진 100장을 마케팅용으로 변환

```bash
#!/bin/bash
# marketing_transform.sh

export GEMINI_API_KEY="your-api-key"

python batch_nanobanana_cli.py \
  --input-dir /data/product_photos \
  --output-dir /data/marketing_images \
  --prompt "이 제품 사진을 고급스럽고 매력적인 마케팅 이미지로 변환" \
  --concurrent 3 \
  --log-file marketing_$(date +%Y%m%d).log \
  --quiet

echo "마케팅 이미지 변환 완료!"
```

**예상 시간:** 30-45분 (API 속도에 따라)

### 🎨 크리에이터 워크플로우 (혼합)

**1단계: 테스트 (GUI)**
- 몇 장의 샘플로 프롬프트 테스트
- 다양한 스타일 실험

**2단계: 대량 처리 (CLI)**
- 확정된 프롬프트로 전체 이미지 처리
- 배치 스크립트로 자동화

### 📊 데이터 분석/연구 (CLI + 로깅)

```bash
# 다양한 프롬프트 테스트
PROMPTS=(
  "사진을 수채화로 변환"
  "사진을 유화로 변환" 
  "사진을 만화 스타일로 변환"
)

for prompt in "${PROMPTS[@]}"; do
  python batch_nanobanana_cli.py \
    -i ./test_images \
    -o "./results_$(echo $prompt | tr ' ' '_')" \
    -p "$prompt" \
    --log-file "test_$prompt.log"
done
```

---

## 🔐 보안 가이드

### API 키 관리

**✅ 안전한 방법:**
```bash
# 환경변수 설정 (권장)
export GEMINI_API_KEY="your-key"

# 설정 파일 사용 (CLI)
echo "GEMINI_API_KEY=your-key" > ~/.nanobanana/config
chmod 600 ~/.nanobanana/config
```

**❌ 위험한 방법:**
```bash
# 명령어에 직접 입력 (프로세스 목록에 노출)
python script.py --api-key "your-key"  # 하지 마세요!
```

### 파일 권한

```bash
# 설정 파일 보호
chmod 600 ~/.nanobanana/config

# 스크립트 실행 권한
chmod +x batch_nanobanana_cli.py

# 결과 폴더 권한 확인
ls -la /path/to/output/
```

---

## 🚨 문제해결 가이드

### 일반적인 문제들

**1. "API 키 오류"**
```bash
# 키 확인
echo $GEMINI_API_KEY

# 새 키 발급
# Google AI Studio에서 새로 생성
```

**2. "파일을 찾을 수 없음"**
```bash
# 경로 확인
ls -la /path/to/images/

# 권한 확인
ls -la /path/to/output/

# 상대 경로 사용
./images 대신 /full/path/to/images 사용
```

**3. "메모리 부족"**
```bash
# 동시 처리 수 줄이기
--concurrent 1

# 이미지 크기 확인
file *.jpg | grep -i size
```

**4. "느린 처리 속도"**
- API 서버 상태 확인
- 네트워크 연결 확인  
- 동시 처리 수 조정
- 이미지 크기 최적화

### 플랫폼별 문제

**Windows:**
- 경로에 한글이 있으면 오류 가능
- 바이러스 백신이 차단할 수 있음

**Mac:**
- Gatekeeper 보안 설정 확인
- Python 경로 문제 가능

**Linux:**
- 권한 문제가 가장 흔함
- 가상환경 활성화 확인

---

## 📈 성능 최적화

### 이미지 준비

```bash
# 이미지 크기 확인
identify *.jpg

# 일괄 리사이즈 (ImageMagick)
mogrify -resize 1920x1080 *.jpg

# 큰 이미지 찾기
find . -name "*.jpg" -size +5M
```

### CLI 최적화

```bash
# CPU 코어 수만큼 병렬 처리
--concurrent $(nproc)

# 조용한 모드로 빠른 처리
--quiet

# JPG 출력으로 용량 절약
--format jpg
```

### 모니터링

```bash
# 실시간 로그 확인
tail -f processing.log

# 시스템 리소스 모니터링
htop

# 디스크 공간 확인
df -h
```

---

## 📚 실습 예제

### 🎓 초보자 실습 (GUI)

**미션: 가족 사진 3장을 드라마틱하게 변환**

1. GUI 프로그램 실행
2. 테스트 폴더에 가족 사진 3장 복사
3. API 키 입력
4. 프롬프트: "이 가족 사진을 따뜻하고 드라마틱한 영화 포스터 스타일로 변환"
5. 결과 확인 및 만족도 평가

### 💼 중급자 실습 (CLI)

**미션: 제품 사진 10장을 3가지 스타일로 변환**

```bash
# 스타일 1: 미니멀
python batch_nanobanana_cli.py \
  -i ./products \
  -o ./minimal_style \
  -p "깔끔하고 미니멀한 제품 사진으로 변환"

# 스타일 2: 럭셔리
python batch_nanobanana_cli.py \
  -i ./products \
  -o ./luxury_style \
  -p "고급스럽고 프리미엄한 럭셔리 제품 사진으로 변환"

# 스타일 3: 빈티지
python batch_nanobanana_cli.py \
  -i ./products \
  -o ./vintage_style \
  -p "따뜻하고 향수를 불러일으키는 빈티지 스타일로 변환"
```

### 🚀 고급자 실습 (자동화)

**미션: 매일 새로운 이미지를 자동 처리하는 스크립트**

```bash
#!/bin/bash
# daily_processor.sh

TODAY=$(date +%Y%m%d)
INPUT_DIR="/data/incoming"
OUTPUT_DIR="/data/processed/$TODAY"

# 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 새 이미지가 있는지 확인
if [ "$(ls -A $INPUT_DIR)" ]; then
    echo "Processing images for $TODAY"
    
    python batch_nanobanana_cli.py \
        --input-dir "$INPUT_DIR" \
        --output-dir "$OUTPUT_DIR" \
        --prompt "이 이미지를 프로페셔널하고 세련된 스타일로 변환" \
        --concurrent 2 \
        --log-file "$OUTPUT_DIR/processing.log" \
        --quiet
    
    # 원본 이미지 아카이브
    mv "$INPUT_DIR"/* "/data/archive/$TODAY/"
    
    echo "Processing complete: $OUTPUT_DIR"
else
    echo "No new images to process"
fi
```

**크론탭 설정 (매일 자동 실행):**
```bash
# 매일 오전 9시에 실행
0 9 * * * /path/to/daily_processor.sh
```

---

## 📖 빠른 참조

### GUI 단축키
- `Ctrl+O`: 입력 폴더 선택
- `Ctrl+S`: 출력 폴더 선택
- `F5`: 처리 시작
- `ESC`: 처리 중지

### CLI 필수 명령어
```bash
# 기본 실행
python batch_nanobanana_cli.py -i input -o output -p "prompt"

# 도움말
python batch_nanobanana_cli.py --help

# 테스트 실행
python batch_nanobanana_cli.py ... --dry-run

# 상세 로그
python batch_nanobanana_cli.py ... --verbose
```

### 자주 사용하는 프롬프트
```
"이 사진을 따뜻하고 부드러운 스타일로 변환"
"이 이미지를 프로페셔널한 포트레이트로 변환"
"이 제품 사진을 매력적인 마케팅 이미지로 변환"
"이 풍경을 꿈꾸는 듯한 환상적인 이미지로 변환"
"이 사진을 빈티지 필름 카메라로 찍은 것처럼 변환"
```

---

## 🎯 다음 단계

### GUI 사용자 → CLI 전환
1. GUI로 몇 번 사용해보기
2. 프롬프트 패턴 파악
3. CLI 기본 명령어 연습
4. 간단한 스크립트 작성

### CLI 사용자 → 고급 활용
1. 자동화 스크립트 작성
2. 크론탭으로 정기 실행
3. 로그 분석 도구 활용
4. 성능 모니터링 설정

### 비즈니스 활용
1. 워크플로우 표준화
2. 품질 관리 프로세스
3. 백업 및 아카이브 전략
4. 팀 협업 도구 통합

---

## 💡 팁과 노하우

### 프롬프트 작성 팁
- 구체적이고 명확하게 작성
- 스타일, 색감, 분위기 포함
- 너무 복잡하지 않게 (2-3문장)
- 참고 이미지나 작가 이름 활용

### 효율적인 워크플로우
- 소량으로 테스트 후 대량 처리
- 로그를 활용한 결과 분석
- 백업은 필수
- API 사용량 모니터링

### 품질 관리
- 원본 이미지 품질이 중요
- 적절한 해상도 유지
- 일관된 프롬프트 사용
- 정기적인 결과 검토

---

이 가이드를 통해 NanoBanana를 효과적으로 활용하시길 바랍니다! 
추가 질문이나 문제가 있으시면 언제든 문의해주세요. 🙂