# Batch NanoBanana Image Generator - CLI Version

Linux 터미널에서 사용할 수 있는 Batch NanoBanana 이미지 생성기입니다. Google의 Gemini API를 사용하여 여러 이미지를 일괄 처리합니다.

## 시스템 요구사항

- Python 3.8 이상
- Linux 환경 (Ubuntu, CentOS, Debian 등)
- 인터넷 연결 (API 호출용)
- Google Gemini API 키

## 설치

### 1. Python 가상환경 생성 (권장)
```bash
python3 -m venv nano_banana_env
source nano_banana_env/bin/activate
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements_cli.txt
```

또는 개별 설치:
```bash
pip install google-genai Pillow rich tqdm python-dotenv
```

### 3. 실행 권한 부여
```bash
chmod +x batch_nanobanana_cli.py
```

## API 키 설정

보안을 위해 다음 방법들 중 하나를 선택하세요:

### 방법 1: 환경변수 (권장)
```bash
export GEMINI_API_KEY="your-actual-api-key-here"
```

영구 설정을 위해 `.bashrc` 또는 `.profile`에 추가:
```bash
echo 'export GEMINI_API_KEY="your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 방법 2: 설정 파일
```bash
mkdir -p ~/.nanobanana
echo "GEMINI_API_KEY=your-actual-api-key-here" > ~/.nanobanana/config
chmod 600 ~/.nanobanana/config
```

### 방법 3: 대화형 입력
API 키가 환경변수나 설정 파일에 없으면 프로그램이 직접 입력을 요청합니다.

## 사용법

### 기본 사용법

```bash
# 환경변수를 사용한 기본 실행
export GEMINI_API_KEY="your-api-key"
python batch_nanobanana_cli.py \
  --input-dir /path/to/images \
  --output-dir /path/to/results \
  --prompt "Create a picture of my cat eating a nano-banana"
```

### 필수 매개변수

- `--input-dir, -i`: 입력 이미지가 들어있는 디렉토리 경로
- `--output-dir, -o`: 결과 이미지를 저장할 디렉토리 경로  
- `--prompt, -p`: 이미지와 함께 API로 전달할 텍스트 프롬프트

### 선택적 매개변수

- `--api-key`: API 키 직접 지정 (보안상 권장하지 않음)
- `--config, -c`: 설정 파일 경로 지정
- `--format, -f`: 출력 이미지 형식 (png, jpg, jpeg, webp)
- `--concurrent`: 동시 처리 스레드 수 (기본값: 1)
- `--dry-run`: 실제 처리 없이 미리보기만 실행
- `--verbose, -v`: 상세 로그 출력
- `--quiet, -q`: 확인 메시지 생략
- `--log-file, -l`: 로그 파일 경로 지정

### 이미지 변형 생성 매개변수

- `--variation`: 이미지 변형 생성 모드 활성화
- `--image`: 단일 이미지 파일 경로 (variation 모드용)
- `--count`: 생성할 변형 이미지 수 (기본값: 3)
- `--variation-type`: 변형 유형 (object_rearrange, object_add, object_remove, style_change, composition, random)

## 사용 예시

### 1. 기본 사용 (환경변수)
```bash
export GEMINI_API_KEY="your-api-key"
python batch_nanobanana_cli.py \
  -i ./photos \
  -o ./generated \
  -p "Transform this photo into a beautiful painting"
```

### 2. 설정 파일 사용
```bash
python batch_nanobanana_cli.py \
  --input-dir ~/Pictures/raw \
  --output-dir ~/Pictures/processed \
  --prompt "Add magical effects to this image" \
  --config ~/.nanobanana/config \
  --verbose
```

### 3. 다양한 옵션 조합
```bash
python batch_nanobanana_cli.py \
  -i /data/images \
  -o /data/results \
  -p "Create artistic version" \
  --format jpg \
  --concurrent 2 \
  --log-file processing.log \
  --quiet
```

### 4. 테스트 실행 (드라이런)
```bash
python batch_nanobanana_cli.py \
  -i ./test_images \
  -o ./test_output \
  -p "Test prompt" \
  --dry-run \
  --verbose
```

### 5. 이미지 변형 생성 (단일 이미지)
```bash
export GEMINI_API_KEY="your-api-key"
python batch_nanobanana_cli.py --variation \
  --image portrait.jpg \
  --output-dir portrait_variations \
  --count 5 \
  --variation-type object_rearrange
```

### 6. 이미지 변형 생성 (여러 이미지)
```bash
python batch_nanobanana_cli.py --variation \
  --input-dir ./photos \
  --output-dir ./variations \
  --count 3 \
  --variation-type random \
  --verbose
```

## 지원되는 이미지 형식

**입력**: PNG, JPG, JPEG, WebP, BMP, TIFF
**출력**: PNG (기본값), JPG, JPEG, WebP

## 보안 권장사항

1. **환경변수 사용**: API 키를 환경변수로 설정하여 프로세스 목록에 노출되지 않도록 합니다.

2. **설정 파일 권한**: 설정 파일을 사용할 경우 적절한 권한 설정:
   ```bash
   chmod 600 ~/.nanobanana/config
   ```

3. **버전 관리**: API 키를 소스 코드나 설정 파일을 커밋하지 마세요.

4. **네트워크 보안**: 신뢰할 수 있는 네트워크에서만 사용하세요.

## 셸 스크립트 통합

```bash
#!/bin/bash
# batch_process.sh

# 설정
INPUT_DIR="/data/images"
OUTPUT_DIR="/data/processed"
PROMPT="Transform this image into art"

# API 키 확인
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY not set"
    exit 1
fi

# 처리 실행
python batch_nanobanana_cli.py \
    --input-dir "$INPUT_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --prompt "$PROMPT" \
    --quiet \
    --log-file "batch_$(date +%Y%m%d_%H%M%S).log"

# 결과 확인
if [ $? -eq 0 ]; then
    echo "Batch processing completed successfully"
else
    echo "Batch processing failed"
    exit 1
fi
```

## 문제 해결

### 1. 권한 오류
```bash
# 실행 권한이 없는 경우
chmod +x batch_nanobanana_cli.py

# 디렉토리 권한 문제
sudo chown -R $USER:$USER /path/to/directory
```

### 2. API 키 관련 오류
```bash
# 환경변수 확인
echo $GEMINI_API_KEY

# 설정 파일 권한 확인
ls -la ~/.nanobanana/config
```

### 3. 패키지 설치 문제
```bash
# 가상환경 활성화 확인
which python
which pip

# 패키지 재설치
pip install --upgrade -r requirements_cli.txt
```

### 4. 네트워크 연결 확인
```bash
# API 연결 테스트
curl -s https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY
```

## 성능 최적화

1. **동시 처리**: `--concurrent` 옵션으로 병렬 처리 (권장: CPU 코어 수)
2. **로그 레벨**: 운영 환경에서는 `--quiet` 사용
3. **출력 형식**: JPG가 PNG보다 파일 크기가 작음
4. **배치 크기**: 대용량 이미지는 동시 처리 수를 줄이세요

## 로그 및 모니터링

```bash
# 로그 파일로 리다이렉트
python batch_nanobanana_cli.py ... --log-file processing.log

# 실시간 로그 모니터링
tail -f processing.log

# 처리 결과 확인
grep "successful\|failed" processing.log
```

## 라이선스

이 소프트웨어는 원본 Batch NanoBanana GUI 애플리케이션의 CLI 버전입니다.

## 지원

문제가 발생하거나 기능 요청이 있으시면 GitHub 이슈로 제출해주세요.