# 🚀 NanoBanana 빠른 참조 가이드

자주 사용하는 명령어와 설정을 한눈에 볼 수 있는 치트시트입니다.

## 📌 핵심 명령어

### GUI 버전 (초보자)
```bash
# 실행
python batch_nanobanana_gui.py
python run_app.py

# Windows
run_windows.bat

# Mac  
./run_mac.sh
```

### CLI 버전 (고급자)
```bash
# 기본 실행
python batch_nanobanana_cli.py -i 입력폴더 -o 출력폴더 -p "프롬프트"

# 도움말
python batch_nanobanana_cli.py --help

# 테스트 실행
python batch_nanobanana_cli.py -i test -o output -p "test" --dry-run
```

---

## 🔑 API 키 설정

| 방법 | 명령어 | 보안 |
|------|--------|------|
| 환경변수 (권장) | `export GEMINI_API_KEY="key"` | ⭐⭐⭐ |
| 설정파일 | `echo "GEMINI_API_KEY=key" > ~/.nanobanana/config` | ⭐⭐ |
| 대화형 입력 | 프로그램 실행 시 입력 | ⭐⭐ |
| 명령행 인수 | `--api-key "key"` | ⭐ |

**영구 설정:**
```bash
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

---

## ⚙️ CLI 옵션 요약

### 필수 옵션
| 옵션 | 단축형 | 설명 | 예시 |
|------|--------|------|------|
| `--input-dir` | `-i` | 입력 폴더 | `-i ./photos` |
| `--output-dir` | `-o` | 출력 폴더 | `-o ./results` |
| `--prompt` | `-p` | AI 프롬프트 | `-p "아티스틱하게 변환"` |

### 선택 옵션
| 옵션 | 단축형 | 기본값 | 설명 |
|------|--------|--------|------|
| `--format` | `-f` | png | 출력 형식 (png,jpg,webp) |
| `--concurrent` | | 1 | 동시 처리 수 |
| `--config` | `-c` | | 설정 파일 경로 |
| `--log-file` | `-l` | | 로그 파일 경로 |
| `--dry-run` | | | 테스트 실행 |
| `--verbose` | `-v` | | 상세 로그 |
| `--quiet` | `-q` | | 조용한 모드 |

---

## 🎨 인기 프롬프트 템플릿

### 기본 스타일
```bash
"이 이미지를 예술적이고 아름다운 작품으로 변환해주세요"
"이 사진을 전문적인 포트레이트로 변환해주세요"
"이 풍경을 숨막히도록 아름다운 장면으로 변환해주세요"
```

### 특정 스타일
```bash
"이 사진을 따뜻한 빈티지 필름 카메라 스타일로 변환해주세요"
"이 이미지를 부드러운 수채화 스타일로 변환해주세요"
"이 사진을 드라마틱하고 영화 같은 분위기로 변환해주세요"
```

### 비즈니스용
```bash
"이 제품 사진을 고급스럽고 매력적인 마케팅 이미지로 변환해주세요"
"이 이미지를 깔끔하고 전문적인 카탈로그용 사진으로 변환해주세요"
"이 사진을 소셜미디어에 적합한 트렌디한 스타일로 변환해주세요"
```

---

## 🛠️ 실용 명령어 예시

### 개인 사용
```bash
# 가족 사진 변환
python batch_nanobanana_cli.py \
  -i ~/Photos/family \
  -o ~/Photos/family_ai \
  -p "따뜻하고 아름다운 가족 사진으로 변환"

# 여행 사진 변환  
python batch_nanobanana_cli.py \
  -i ./vacation_photos \
  -o ./vacation_artistic \
  -p "여행의 추억이 담긴 드라마틱한 작품으로 변환" \
  --format jpg
```

### 비즈니스 사용
```bash
# 제품 카탈로그
python batch_nanobanana_cli.py \
  -i ./product_raw \
  -o ./product_catalog \
  -p "전문적이고 깔끔한 제품 카탈로그 이미지로 변환" \
  --concurrent 2 \
  --quiet

# 마케팅 소재
python batch_nanobanana_cli.py \
  -i ./marketing_raw \
  -o ./marketing_final \
  -p "시선을 끄는 매력적인 마케팅 이미지로 변환" \
  --log-file marketing.log
```

### 크리에이터 워크플로우
```bash
# 다중 스타일 테스트
python workflows/creator_multistyle.py \
  photo.jpg \
  --preset artistic \
  --output ./style_tests

# 개인 사진 처리기 (GUI)
python workflows/personal_photos.py

# 비즈니스 배치 처리
./workflows/business_batch.sh ./raw ./processed luxury
```

---

## 📁 지원 파일 형식

### 입력 형식
- **이미지**: PNG, JPG, JPEG, WebP, BMP, TIFF
- **경로**: 절대경로 권장, 상대경로 가능

### 출력 형식
- **PNG** (기본): 최고 품질, 큰 용량
- **JPG**: 작은 용량, 압축 손실
- **WebP**: 최신 형식, 효율적 압축

### 출력 파일명 패턴
```
원본파일명_generated.확장자

예시:
cat.jpg → cat_generated.png
photo.png → photo_generated.jpg
```

---

## 🚨 빠른 문제해결

### 일반적인 오류
| 오류 메시지 | 해결책 |
|-------------|--------|
| `No module named 'google.genai'` | `pip install google-genai` |
| `API key is required` | API 키 설정 확인 |
| `Input directory does not exist` | 경로 확인, 절대경로 사용 |
| `Permission denied` | `chmod 755 폴더` |
| `No supported image files found` | 이미지 파일 확인 |

### 성능 최적화
| 문제 | 해결책 |
|------|--------|
| 느린 처리 | `--concurrent 2-4` |
| 메모리 부족 | 이미지 크기 줄이기 |
| 큰 출력 파일 | `--format jpg` |
| API 제한 | 처리량 줄이기 |

### 즉시 확인 명령어
```bash
# 환경 상태 확인
python --version && pip list | grep genai

# API 연결 테스트
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | head -1

# 권한 확인
ls -la ./input_folder && ls -la ./output_folder

# 메모리 확인
free -h

# 로그 확인
tail -5 batch_nanobanana.log
```

---

## 🔧 실용 스크립트

### 일일 자동 처리 스크립트
```bash
#!/bin/bash
# daily_process.sh

export GEMINI_API_KEY="your-key"
TODAY=$(date +%Y%m%d)

python batch_nanobanana_cli.py \
  -i "/data/incoming" \
  -o "/data/processed/$TODAY" \
  -p "전문적이고 아름다운 이미지로 변환" \
  --concurrent 2 \
  --log-file "/logs/processing_$TODAY.log" \
  --quiet

echo "처리 완료: $(date)"
```

### 크론탭 설정 (매일 오전 9시)
```bash
0 9 * * * /path/to/daily_process.sh
```

### 배치 파일 (Windows)
```batch
@echo off
set GEMINI_API_KEY=your-key
python batch_nanobanana_cli.py -i "C:\Images\Input" -o "C:\Images\Output" -p "아티스틱 변환" --quiet
pause
```

---

## 📊 성능 참고 수치

### 처리 시간 (대략적)
| 이미지 크기 | 수량 | 예상 시간 |
|-------------|------|-----------|
| 1MP | 10장 | 2-3분 |
| 5MP | 10장 | 5-8분 |
| 10MP | 10장 | 10-15분 |
| 1MP | 100장 | 20-30분 |

### 시스템 요구사항
| 항목 | 최소 | 권장 |
|------|------|------|
| RAM | 4GB | 8GB+ |
| 디스크 | 1GB | 10GB+ |
| CPU | 2코어 | 4코어+ |
| 네트워크 | 1Mbps | 10Mbps+ |

---

## 🔗 관련 링크

| 항목 | 링크 |
|------|------|
| Google AI Studio | https://aistudio.google.com/ |
| Python 다운로드 | https://python.org/downloads/ |
| 문제 신고 | GitHub Issues |
| 전체 가이드 | [USAGE_GUIDE.md](USAGE_GUIDE.md) |
| 문제해결 | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

---

## 💡 팁과 요령

### 효율적인 워크플로우
1. **소량 테스트** → 프롬프트 최적화 → 대량 처리
2. **드라이런 모드**로 먼저 확인
3. **로그 파일** 활용하여 결과 분석
4. **배치 스크립트**로 반복 작업 자동화

### 프롬프트 작성 팁
- 구체적이고 명확하게 작성
- 원하는 스타일, 색감, 분위기 포함
- 2-3문장으로 간결하게
- 예술가 이름이나 스타일 참조 활용

### 보안 베스트 프랙티스
- API 키는 환경변수로 관리
- 설정 파일 권한을 600으로 설정
- 공개 저장소에 키 업로드 금지
- 주기적으로 키 교체

---

**🍌 이 참조 가이드를 북마크해두고 필요할 때마다 활용하세요!**