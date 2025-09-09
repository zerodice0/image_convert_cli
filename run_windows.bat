@echo off
title NanoBanana 이미지 생성기

echo.
echo ========================================
echo   🍌 NanoBanana 이미지 생성기 시작
echo ========================================
echo.

if not exist "nano_banana_env" (
    echo ❌ 아직 설치되지 않았습니다!
    echo 💡 먼저 install_windows.bat을 실행해주세요.
    echo.
    pause
    exit /b 1
)

echo 🚀 프로그램 시작 중...
call nano_banana_env\Scripts\activate.bat
python batch_nanobanana_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 프로그램 실행 중 오류가 발생했습니다.
    echo 💡 install_windows.bat을 다시 실행해보세요.
    echo.
    pause
)

echo.
echo 프로그램이 종료되었습니다.
pause