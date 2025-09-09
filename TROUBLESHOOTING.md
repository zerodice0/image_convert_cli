# 🚨 NanoBanana 문제해결 가이드

문제가 발생했을 때 단계별로 해결할 수 있는 완전한 가이드입니다.

## 🔍 문제 진단 도구

### 1단계: 기본 상태 확인

```bash
# Python 버전 확인
python --version
python3 --version

# 패키지 설치 상태 확인
pip list | grep -E "(google-genai|Pillow|rich|tqdm)"

# API 키 설정 확인
echo $GEMINI_API_KEY

# 현재 디렉토리 및 권한 확인
pwd
ls -la
```

### 2단계: 연결 테스트

```bash
# 인터넷 연결 확인
ping -c 3 google.com

# Google AI API 연결 확인
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | head -10
```

### 3단계: 로그 분석

```bash
# 최근 로그 확인
tail -20 batch_nanobanana.log

# 오류 메시지 검색
grep -i error batch_nanobanana.log

# 처리 통계
grep -c "성공\|실패" batch_nanobanana.log
```

---

## 🐛 일반적인 문제들

### ❌ "모듈을 찾을 수 없습니다" 오류

**증상:**
```
ModuleNotFoundError: No module named 'google.genai'
ImportError: No module named 'PIL'
```

**해결책:**

1. **가상환경 확인**
```bash
# 가상환경 활성화 확인
which python
which pip

# 가상환경 재활성화
source nano_banana_env/bin/activate  # Linux/Mac
# 또는
nano_banana_env\Scripts\activate     # Windows
```

2. **패키지 재설치**
```bash
# 캐시 삭제 후 재설치
pip cache purge
pip install --force-reinstall -r requirements_cli.txt

# 개별 패키지 설치
pip install google-genai Pillow rich tqdm python-dotenv
```

3. **Python 경로 문제**
```bash
# Python 실행 파일 확인
which python3
/usr/bin/python3 --version

# 심볼릭 링크 생성 (필요시)
ln -s /usr/bin/python3 /usr/local/bin/python
```

---

### 🔑 API 키 관련 문제

**증상:**
```
❌ API key is required to proceed
❌ Invalid API key
❌ API key input cancelled or not available
```

**해결책:**

1. **API 키 유효성 확인**
```bash
# 키 길이 확인 (보통 39자)
echo $GEMINI_API_KEY | wc -c

# 키 형식 확인 (AIza로 시작)
echo $GEMINI_API_KEY | grep "^AIza"

# 새 키 발급 받기
echo "Google AI Studio에서 새 키를 발급받으세요: https://aistudio.google.com/"
```

2. **환경변수 설정**
```bash
# 임시 설정
export GEMINI_API_KEY="your-actual-api-key-here"

# 영구 설정 (.bashrc에 추가)
echo 'export GEMINI_API_KEY="your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# 설정 확인
env | grep GEMINI
```

3. **설정 파일 사용**
```bash
# 설정 파일 생성
mkdir -p ~/.nanobanana
echo "GEMINI_API_KEY=your-actual-api-key-here" > ~/.nanobanana/config
chmod 600 ~/.nanobanana/config

# 설정 파일 확인
cat ~/.nanobanana/config
ls -la ~/.nanobanana/config
```

---

### 📁 파일 및 폴더 문제

**증상:**
```
❌ Input directory does not exist
❌ Permission denied
❌ No supported image files found
```

**해결책:**

1. **경로 문제**
```bash
# 절대 경로 사용
realpath ./images  # 현재 상대 경로의 절대 경로 확인

# 경로 확인
ls -la /full/path/to/images/
file /path/to/image.jpg  # 파일 형식 확인
```

2. **권한 문제**
```bash
# 디렉토리 권한 확인
ls -ld /path/to/directory

# 권한 변경
chmod 755 /path/to/input/directory
chmod 775 /path/to/output/directory

# 소유자 변경 (필요시)
sudo chown -R $USER:$USER /path/to/directory
```

3. **파일 형식 문제**
```bash
# 지원되는 형식 확인
find ./images -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.webp" \)

# 파일 메타데이터 확인
identify *.jpg  # ImageMagick 사용
file *.png      # 파일 유형 확인
```

---

### 🌐 네트워크 연결 문제

**증상:**
```
❌ Connection timeout
❌ Network error
❌ SSL certificate error
```

**해결책:**

1. **기본 연결 확인**
```bash
# DNS 확인
nslookup generativelanguage.googleapis.com

# 방화벽 확인
sudo ufw status  # Ubuntu
firewall-cmd --list-all  # CentOS/RHEL

# 프록시 설정 확인
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

2. **SSL 인증서 문제**
```bash
# 인증서 업데이트
sudo apt-get update && sudo apt-get install ca-certificates  # Ubuntu
sudo yum update ca-certificates  # CentOS

# 시간 동기화
sudo ntpdate -s time.nist.gov
```

3. **네트워크 도구로 확인**
```bash
# 연결 테스트
telnet generativelanguage.googleapis.com 443

# HTTP 상태 확인
curl -I https://generativelanguage.googleapis.com/

# 상세 연결 정보
curl -v https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY
```

---

### 🐌 성능 관련 문제

**증상:**
- 처리 속도가 매우 느림
- 메모리 부족 오류
- CPU 사용률 100%

**해결책:**

1. **이미지 최적화**
```bash
# 이미지 크기 확인
identify -format "%f: %wx%h %b\n" *.jpg

# 이미지 리사이즈 (ImageMagick)
mogrify -resize 1920x1080\> *.jpg  # 큰 이미지만 리사이즈
mogrify -quality 85 *.jpg         # 품질 조정

# 용량 큰 파일 찾기
find . -name "*.jpg" -size +5M -exec ls -lh {} \;
```

2. **시스템 리소스 모니터링**
```bash
# 메모리 사용량
free -h
ps aux | grep python

# CPU 사용량
top -p $(pgrep -f batch_nanobanana)
htop  # 설치되어 있는 경우

# 디스크 공간
df -h
du -sh ./output_directory
```

3. **처리 옵션 조정**
```bash
# 동시 처리 수 줄이기
python batch_nanobanana_cli.py ... --concurrent 1

# 출력 형식 변경 (용량 절약)
python batch_nanobanana_cli.py ... --format jpg

# 배치 처리 (한 번에 적은 수량)
# 큰 폴더를 작은 단위로 나누어 처리
```

---

### 🖥️ GUI 관련 문제

**증상:**
- GUI가 실행되지 않음
- 버튼이 반응하지 않음
- 화면이 깨져 보임

**해결책:**

1. **GUI 라이브러리 확인**
```bash
# Tkinter 설치 확인
python -c "import tkinter; print('Tkinter available')"

# GUI 환경 확인 (Linux)
echo $DISPLAY
xdpyinfo | grep resolution
```

2. **디스플레이 문제**
```bash
# X11 포워딩 (SSH 연결 시)
ssh -X username@hostname

# 가상 디스플레이 (헤드리스 환경)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

3. **권한 문제**
```bash
# 디스플레이 권한
xhost +local:

# 사용자 그룹 확인
groups $USER
```

---

## 🔧 플랫폼별 해결책

### 🐧 Linux

**Ubuntu/Debian:**
```bash
# 패키지 관리자로 Python 설치
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk

# 의존성 설치
sudo apt install build-essential libssl-dev libffi-dev
```

**CentOS/RHEL:**
```bash
# EPEL 저장소 활성화
sudo yum install epel-release

# Python 및 도구 설치
sudo yum install python3 python3-pip python3-tkinter

# 개발 도구
sudo yum groupinstall "Development Tools"
```

**Arch Linux:**
```bash
# 패키지 설치
sudo pacman -S python python-pip tk

# AUR 헬퍼로 추가 패키지 (필요시)
yay -S python-google-genai
```

### 🍎 macOS

**Homebrew 사용:**
```bash
# Homebrew 설치 확인
brew --version

# Python 설치
brew install python python-tk

# 경로 문제 해결
export PATH="/usr/local/opt/python/libexec/bin:$PATH"
```

**권한 문제:**
```bash
# Gatekeeper 우회
sudo spctl --master-disable  # 임시로만 사용

# 인증되지 않은 앱 실행 허용
sudo xattr -rd com.apple.quarantine /path/to/app
```

### 🪟 Windows

**PowerShell 관리자 모드:**
```powershell
# 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 가상환경 활성화
.\nano_banana_env\Scripts\Activate.ps1

# 경로 문제
$env:PATH += ";C:\Python39\Scripts"
```

**WSL 사용:**
```bash
# WSL에서 GUI 앱 실행 (WSL2 + WSLg)
export DISPLAY=:0

# X11 서버 설치 (VcXsrv 등)
echo "Windows에서 X11 서버를 실행하세요"
```

---

## 📊 로그 분석 및 디버깅

### 로그 레벨별 정보

**INFO 레벨:**
```bash
# 정상 처리 과정
grep "INFO" batch_nanobanana.log | tail -10

# 처리 통계
grep "성공\|완료" batch_nanobanana.log | wc -l
```

**WARNING 레벨:**
```bash
# 경고 메시지 확인
grep "WARNING\|WARN" batch_nanobanana.log

# 스킵된 파일들
grep "skipping\|exists" batch_nanobanana.log
```

**ERROR 레벨:**
```bash
# 오류 메시지 분석
grep "ERROR" batch_nanobanana.log | sort | uniq -c

# 특정 오류 패턴
grep -E "(timeout|connection|permission)" batch_nanobanana.log
```

### 디버깅 모드 실행

```bash
# 상세 로그 활성화
python batch_nanobanana_cli.py ... --verbose --log-file debug.log

# Python 디버거 모드
python -u batch_nanobanana_cli.py ... 2>&1 | tee debug_output.log

# 단계별 처리 확인
python batch_nanobanana_cli.py ... --dry-run --verbose
```

---

## 🆘 긴급 복구 가이드

### 환경 완전 재설정

```bash
#!/bin/bash
# emergency_reset.sh

echo "🚨 긴급 환경 재설정 시작"

# 1. 기존 가상환경 제거
rm -rf nano_banana_env

# 2. 새 가상환경 생성
python3 -m venv nano_banana_env
source nano_banana_env/bin/activate

# 3. pip 업그레이드
pip install --upgrade pip

# 4. 패키지 재설치
pip install -r requirements_cli.txt

# 5. 권한 설정
chmod +x batch_nanobanana_cli.py

# 6. 테스트 실행
echo "✅ 재설정 완료. 테스트 실행 중..."
python batch_nanobanana_cli.py --help

echo "🎉 환경 재설정 완료!"
```

### 백업에서 복구

```bash
# 설정 파일 백업
cp ~/.nanobanana/config ~/.nanobanana/config.backup.$(date +%Y%m%d)

# 프로젝트 파일 백업
tar -czf nanobanana_backup_$(date +%Y%m%d).tar.gz \
    batch_nanobanana*.py requirements*.txt *.md

# 백업에서 복구
tar -xzf nanobanana_backup_YYYYMMDD.tar.gz
```

---

## 🔍 고급 문제해결

### API 응답 분석

```bash
# API 응답 헤더 확인
curl -I "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"

# 상세 API 호출 로그
export PYTHONPATH="$PYTHONPATH:."
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from google import genai
client = genai.Client(api_key='$GEMINI_API_KEY')
print('API 연결 성공')
"
```

### 메모리 사용량 프로파일링

```python
# memory_profile.py
import psutil
import time
from memory_profiler import profile

@profile
def process_images():
    # 실제 이미지 처리 코드
    pass

# 실행: python -m memory_profiler memory_profile.py
```

### 성능 벤치마킹

```bash
# 처리 시간 측정
time python batch_nanobanana_cli.py -i test -o output -p "test" --dry-run

# 상세 성능 분석
python -m cProfile -o profile_output.prof batch_nanobanana_cli.py ...
python -c "import pstats; pstats.Stats('profile_output.prof').sort_stats('cumulative').print_stats(10)"
```

---

## 📞 추가 도움이 필요한 경우

### 버그 리포트 작성

**포함해야 할 정보:**
1. 운영체제 및 버전
2. Python 버전
3. 패키지 버전 (`pip freeze`)
4. 실행한 명령어
5. 오류 메시지 전문
6. 로그 파일 (민감한 정보 제거 후)

### 로그 민감정보 제거

```bash
# API 키 제거
sed 's/AIza[A-Za-z0-9_-]*/[API_KEY_HIDDEN]/g' batch_nanobanana.log > sanitized.log

# 경로 정보 일반화
sed 's|/home/[^/]*/|/home/user/|g' sanitized.log > final_log.txt
```

### 커뮤니티 자원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Stack Overflow**: `nanobanana` 태그로 질문
- **Discord/Slack**: 실시간 도움말 (커뮤니티가 있는 경우)

---

이 문제해결 가이드로도 해결되지 않는 문제가 있다면, 
위의 정보를 포함해서 GitHub 이슈나 커뮤니티에 문의해주세요! 🙂