#!/bin/bash

echo ""
echo "========================================"
echo "  🍌 NanoBanana 이미지 생성기 시작"
echo "========================================"
echo ""

if [ ! -d "nano_banana_env" ]; then
    echo "❌ 아직 설치되지 않았습니다!"
    echo "💡 먼저 ./install_mac.sh를 실행해주세요."
    exit 1
fi

echo "🚀 프로그램 시작 중..."
source nano_banana_env/bin/activate
python batch_nanobanana_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 프로그램 실행 중 오류가 발생했습니다."
    echo "💡 ./install_mac.sh를 다시 실행해보세요."
    echo ""
fi

echo ""
echo "프로그램이 종료되었습니다."