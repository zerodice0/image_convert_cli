#!/bin/bash

echo ""
echo "========================================"
echo "  🍌 NanoBanana 이미지 생성기 설치"
echo "========================================"
echo ""

echo "📦 Python 버전 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다!"
    echo "💡 https://python.org 에서 Python을 먼저 설치해주세요."
    exit 1
fi

python3 --version
echo "✅ Python3가 설치되어 있습니다!"
echo ""

echo "🔧 가상환경 생성 중..."
python3 -m venv nano_banana_env

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성 실패"
    exit 1
fi

echo "📋 가상환경 활성화 중..."
source nano_banana_env/bin/activate

echo "📦 필요한 패키지 설치 중..."
python -m pip install --upgrade pip
pip install google-genai Pillow

if [ $? -ne 0 ]; then
    echo "❌ 패키지 설치 실패"
    echo "💡 인터넷 연결을 확인하고 다시 시도해주세요."
    exit 1
fi

echo ""
echo "✅ 설치 완료!"
echo "🚀 이제 ./run_mac.sh 명령으로 프로그램을 실행할 수 있습니다!"
echo ""