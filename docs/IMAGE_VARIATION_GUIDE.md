# 🎨 이미지 변형 생성 가이드

## 개요
NanoBanana의 이미지 변형 생성 기능을 사용하면 하나의 원본 이미지에서 여러 가지 다른 변형을 자동으로 생성할 수 있습니다. Google Gemini AI를 활용하여 이미지 내의 객체들을 재배치하거나, 새로운 요소를 추가하거나, 스타일을 변경하는 등 다양한 변형을 생성합니다.

## 🖼️ GUI 사용법

### 1. 이미지 변형 탭 열기
1. NanoBanana GUI를 실행합니다
2. 상단의 "이미지 변형" 탭을 클릭합니다

### 2. 이미지 선택 및 기본 설정
1. **"이미지 선택"** 버튼을 클릭하여 변형할 이미지를 선택합니다
2. **변형 개수**를 설정합니다 (1-20개)
3. **변형 타입**을 선택합니다:
   - **랜덤 변형 (random)**: 다양한 변형을 무작위로 생성
   - **객체 재배치 (rearrange)**: 이미지 내 객체들의 위치 변경
   - **객체 추가 (add)**: 새로운 요소 추가
   - **객체 제거 (remove)**: 기존 요소 제거
   - **스타일 변경 (style)**: 전체적인 스타일 변화
   - **구도 변경 (composition)**: 이미지 구성 및 배치 변경

### 3. 고급 설정 (선택사항)
- **스타일 옵션**: 원하는 변형 스타일을 체크박스로 선택
  - ☐ 객체 재배치
  - ☐ 객체 추가  
  - ☐ 객체 제거
  - ☐ 스타일 변경
  - ☐ 구도 변경

- **시드값**: 재현 가능한 결과를 위한 시드 설정 (선택사항)
- **품질 임계값**: 생성될 변형의 최소 품질 기준 (0.0-1.0)

### 4. 변형 생성 및 결과 확인
1. **"변형 생성 시작"** 버튼을 클릭합니다
2. 진행률 표시줄을 통해 생성 과정을 모니터링합니다
3. 완료 후 결과 갤러리에서 생성된 변형들을 확인합니다
4. 각 썸네일을 클릭하면 전체 크기로 볼 수 있습니다
5. 우클릭으로 이미지를 저장하거나 복사할 수 있습니다

## 💻 CLI 사용법

### 기본 명령어 구조
```bash
python batch_nanobanana_cli.py [모드] [옵션들]
```

### 단일 이미지 변형 생성
```bash
# 기본 사용법: 5개 변형 생성
python batch_nanobanana_cli.py --variation \
  --image photo.jpg \
  --count 5 \
  --output-dir variations

# 특정 변형 타입으로 생성
python batch_nanobanana_cli.py --variation \
  --image portrait.jpg \
  --variation-type rearrange \
  --count 3 \
  --output-dir rearranged_variations

# 복합 스타일 적용
python batch_nanobanana_cli.py --variation \
  --image landscape.jpg \
  --styles "rearrange,add,style" \
  --count 7 \
  --output-dir mixed_variations
```

### 배치 변형 생성
```bash
# 여러 이미지를 각각 3개씩 변형
python batch_nanobanana_cli.py --batch-variation \
  --input-dir ./photos \
  --count-per-image 3 \
  --output-dir ./batch_variations \
  --parallel 2

# 특정 확장자만 처리
python batch_nanobanana_cli.py --batch-variation \
  --input-dir ./images \
  --extensions "jpg,png,webp" \
  --count-per-image 5 \
  --output-dir ./variations \
  --parallel 4
```

### 고급 옵션 활용
```bash
# 고품질 설정으로 변형 생성
python batch_nanobanana_cli.py --variation \
  --image professional_photo.jpg \
  --count 5 \
  --seed 42 \
  --quality-threshold 0.8 \
  --max-attempts 3 \
  --output-dir high_quality_variations

# 품질 분석과 함께 생성
python batch_nanobanana_cli.py --variation \
  --image art_piece.jpg \
  --count 10 \
  --variation-type style \
  --enable-quality-analysis \
  --output-dir analyzed_variations
```

### CLI 옵션 참조

#### 공통 옵션
- `--api-key`: Gemini API 키 (환경변수 GEMINI_API_KEY로도 설정 가능)
- `--output-dir`: 출력 디렉토리
- `--verbose`: 상세한 로그 출력

#### 변형 생성 옵션
- `--image`: 원본 이미지 파일 경로
- `--count`: 생성할 변형 개수 (1-50)
- `--variation-type`: 변형 타입 (random, rearrange, add, remove, style, composition)
- `--styles`: 적용할 스타일 목록 (쉼표로 구분)
- `--seed`: 재현 가능한 결과를 위한 시드값
- `--quality-threshold`: 품질 임계값 (0.0-1.0, 기본값: 0.7)
- `--max-attempts`: 최대 시도 횟수 (기본값: 3)

#### 배치 처리 옵션
- `--input-dir`: 입력 이미지 디렉토리
- `--count-per-image`: 이미지당 생성할 변형 개수
- `--extensions`: 처리할 파일 확장자 (기본값: jpg,jpeg,png,webp)
- `--parallel`: 병렬 처리 프로세스 수
- `--skip-existing`: 기존 출력 파일 건너뛰기

## 🎯 최적 사용법 팁

### 1. 이미지 선택 가이드
**권장 이미지 특성:**
- **해상도**: 최소 1024x1024 픽셀 이상 (더 나은 품질을 위해)
- **명확한 객체**: 사람, 동물, 자동차, 건물 등 구별되는 객체가 포함된 이미지
- **적당한 복잡성**: 너무 단순하거나 복잡하지 않은 중간 정도의 복잡성
- **좋은 조명**: 밝고 균일한 조명의 이미지

**피해야 할 이미지:**
- 너무 어둡거나 흐린 이미지
- 극도로 복잡하거나 혼잡한 이미지
- 텍스트가 주된 내용인 이미지
- 추상적이거나 패턴만 있는 이미지

### 2. 변형 타입 선택 가이드

#### `random` (랜덤 변형)
- **적용 시기**: 다양한 결과를 원할 때, 실험적인 변형을 원할 때
- **결과**: 예측 불가능하지만 창의적인 변형들

#### `rearrange` (객체 재배치)
- **적용 시기**: 기존 요소들의 배치만 바꾸고 싶을 때
- **결과**: 원본의 요소들이 다른 위치에 배치된 변형

#### `add` (객체 추가)
- **적용 시기**: 이미지에 새로운 요소를 추가하고 싶을 때
- **결과**: 새로운 객체나 요소가 자연스럽게 추가된 변형

#### `remove` (객체 제거)
- **적용 시기**: 불필요한 요소를 제거하고 싶을 때
- **결과**: 특정 객체가 제거되고 배경이 자연스럽게 메워진 변형

#### `style` (스타일 변경)
- **적용 시기**: 전체적인 분위기나 스타일을 바꾸고 싶을 때
- **결과**: 다른 화풍, 색조, 분위기의 변형

#### `composition` (구도 변경)
- **적용 시기**: 이미지의 전체적인 구성을 바꾸고 싶을 때
- **결과**: 다른 앵글, 크롭핑, 구성의 변형

### 3. 성능 최적화

#### 메모리 최적화
- **대용량 이미지**: 자동으로 적절한 크기로 최적화됨
- **배치 처리**: 메모리 사용량을 모니터링하여 자동 조절
- **캐싱**: 동일한 설정의 재생성 시 캐시된 결과 활용

#### 속도 최적화
```bash
# 병렬 처리로 배치 작업 가속화
--parallel 4  # CPU 코어 수에 맞게 조정

# 품질 임계값 조절로 속도 향상
--quality-threshold 0.6  # 낮은 값으로 설정하면 더 빠름

# 시도 횟수 제한으로 대기 시간 단축
--max-attempts 2
```

#### 품질 vs 속도 균형
```bash
# 빠른 생성 (품질 보다는 속도 우선)
--quality-threshold 0.5 --max-attempts 1

# 균형잡힌 설정 (기본값)
--quality-threshold 0.7 --max-attempts 3

# 고품질 생성 (시간이 걸리더라도 품질 우선)
--quality-threshold 0.9 --max-attempts 5
```

## 🔧 문제해결 가이드

### 자주 발생하는 문제

#### 1. 변형 생성 실패
**증상**: "변형 생성에 실패했습니다" 오류

**해결 방법**:
1. **API 키 확인**:
   ```bash
   export GEMINI_API_KEY="your-actual-api-key"
   ```
2. **인터넷 연결 확인**
3. **이미지 형식 확인**: 지원되는 형식(PNG, JPG, JPEG, WebP, BMP, TIFF)인지 확인
4. **이미지 크기 확인**: 너무 크거나 작지 않은지 확인

#### 2. 품질이 낮은 결과
**증상**: 흐리거나 부자연스러운 변형

**해결 방법**:
1. **품질 임계값 높이기**:
   ```bash
   --quality-threshold 0.8
   ```
2. **더 명확한 원본 이미지 사용**
3. **다른 변형 타입 시도**
4. **시드값을 바꿔가며 여러 번 시도**

#### 3. 처리 속도가 느림
**증상**: 변형 생성이 오래 걸림

**해결 방법**:
1. **이미지 크기 최적화**: 2048x2048 이하로 리사이즈
2. **변형 개수 조절**: 한 번에 너무 많은 변형 요청하지 않기
3. **병렬 처리 활용**:
   ```bash
   --parallel 4
   ```
4. **품질 임계값 조절**:
   ```bash
   --quality-threshold 0.6
   ```

#### 4. 메모리 부족
**증상**: "메모리가 부족합니다" 오류

**해결 방법**:
1. **배치 크기 줄이기**: 한 번에 처리하는 이미지 수 감소
2. **이미지 크기 줄이기**: 1024x1024 이하로 리사이즈
3. **병렬 프로세스 수 줄이기**:
   ```bash
   --parallel 1
   ```

### 오류 코드와 해결책

#### `API_KEY_ERROR`
- **원인**: Gemini API 키가 없거나 잘못됨
- **해결**: 올바른 API 키 설정

#### `INVALID_IMAGE_FORMAT`
- **원인**: 지원되지 않는 이미지 형식
- **해결**: PNG, JPG, WebP 등 지원되는 형식으로 변환

#### `NETWORK_ERROR`
- **원인**: 인터넷 연결 문제
- **해결**: 네트워크 연결 확인, 방화벽 설정 확인

#### `QUOTA_EXCEEDED`
- **원인**: Gemini API 사용량 한도 초과
- **해결**: API 사용량 확인, 잠시 후 재시도

#### `IMAGE_TOO_LARGE`
- **원인**: 이미지가 너무 큼
- **해결**: 이미지 크기를 2048x2048 이하로 리사이즈

## 📁 지원되는 형식

### 입력 이미지 형식
- **PNG** (.png)
- **JPEG** (.jpg, .jpeg)
- **WebP** (.webp)
- **BMP** (.bmp)
- **TIFF** (.tiff, .tif)

### 출력 이미지 형식
- **PNG** (기본값, 무손실 압축)
- **JPEG** (더 작은 파일 크기)
- **WebP** (최적의 압축률)

### 권장 이미지 사양
- **해상도**: 512x512 ~ 2048x2048 픽셀
- **파일 크기**: 최대 20MB
- **색상**: RGB 컬러 모드
- **비트 깊이**: 8비트/채널

## 💡 실용적인 활용 예시

### 1. 소셜 미디어 콘텐츠 제작
```bash
# Instagram용 다양한 변형 생성
python batch_nanobanana_cli.py --variation \
  --image profile_photo.jpg \
  --count 5 \
  --styles "style,composition" \
  --output-dir instagram_variants
```

### 2. 제품 사진 변형
```bash
# 제품 사진의 다양한 각도와 스타일
python batch_nanobanana_cli.py --variation \
  --image product.jpg \
  --variation-type rearrange \
  --count 8 \
  --quality-threshold 0.8 \
  --output-dir product_variations
```

### 3. 아트워크 스타일 실험
```bash
# 예술 작품의 다양한 스타일 탐색
python batch_nanobanana_cli.py --variation \
  --image artwork.jpg \
  --variation-type style \
  --count 10 \
  --seed 123 \
  --output-dir style_experiments
```

### 4. 배경 화면 컬렉션 생성
```bash
# 하나의 이미지로 다양한 배경 화면 생성
python batch_nanobanana_cli.py --variation \
  --image landscape.jpg \
  --styles "composition,style,add" \
  --count 15 \
  --output-dir wallpaper_collection
```

## 🚀 고급 기능

### 1. 품질 분석 시스템
- **자동 품질 평가**: 생성된 변형의 품질을 자동으로 분석
- **유사도 검사**: 원본과의 적절한 유사도 유지
- **다양성 평가**: 변형들 간의 다양성 측정
- **객체 무결성**: 중요 객체의 보존 여부 확인

### 2. 중복 방지 시스템
- **해시 기반 검사**: 동일하거나 매우 유사한 변형 자동 감지
- **임계값 설정**: 유사도 임계값 조정 가능
- **메모리 효율성**: 효율적인 중복 검사 알고리즘

### 3. 지능형 캐싱
- **결과 캐싱**: 동일한 설정의 재요청 시 캐시된 결과 반환
- **세션 지속성**: 프로그램 재시작 후에도 캐시 유지
- **자동 정리**: 오래된 캐시 자동 삭제

### 4. 적응형 품질 관리
- **성능 모니터링**: 시스템 성능에 따른 자동 설정 조정
- **동적 최적화**: 처리 속도와 품질의 자동 균형
- **리소스 관리**: 메모리 사용량 자동 최적화

## 📞 지원 및 커뮤니티

### 문제 신고
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discord**: 실시간 커뮤니티 지원
- **이메일**: 개인적인 지원 요청

### 기여 방법
- **코드 기여**: Pull Request 환영
- **문서 개선**: 가이드 및 튜토리얼 기여
- **번역**: 다국어 지원 기여
- **테스팅**: 베타 기능 테스트 참여

### 추가 자료
- **API 문서**: 개발자를 위한 상세한 API 참조
- **예제 갤러리**: 다양한 변형 생성 예시
- **튜토리얼 비디오**: 단계별 사용법 영상
- **FAQ**: 자주 묻는 질문과 답변

---

**참고**: 이 가이드는 지속적으로 업데이트됩니다. 최신 정보는 공식 문서를 확인해주세요.