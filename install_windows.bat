@echo off
title NanoBanana 이미지 생성기 설치

echo.
echo ========================================
echo   🍌 NanoBanana 이미지 생성기 설치
echo ========================================
echo.

echo 📦 Python 버전 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다!
    echo 💡 https://python.org 에서 Python을 먼저 설치해주세요.
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python이 설치되어 있습니다!
echo.

echo 🔧 가상환경 생성 중...
python -m venv nano_banana_env
if %errorlevel% neq 0 (
    echo ❌ 가상환경 생성 실패
    pause
    exit /b 1
)

echo 📋 가상환경 활성화 중...
call nano_banana_env\Scripts\activate.bat

echo 📦 필요한 패키지 설치 중...
python -m pip install --upgrade pip
pip install google-genai Pillow

if %errorlevel% neq 0 (
    echo ❌ 패키지 설치 실패
    echo 💡 인터넷 연결을 확인하고 다시 시도해주세요.
    pause
    exit /b 1
)

echo.
echo ✅ 설치 완료!
echo 🚀 이제 run_windows.bat 파일을 실행하면 프로그램이 시작됩니다!
echo.
pause