#!/bin/bash
# 비즈니스 대량 이미지 처리 워크플로우
# 사용법: ./business_batch.sh [input_dir] [output_dir] [style]

set -e  # 오류 시 즉시 종료

# 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
CONFIG_FILE="$SCRIPT_DIR/../.nanobanana/config"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 매개변수 확인
if [ $# -lt 3 ]; then
    echo "사용법: $0 <입력폴더> <출력폴더> <스타일>"
    echo ""
    echo "스타일 옵션:"
    echo "  marketing  - 마케팅용 매력적인 이미지"
    echo "  product    - 제품 카탈로그용 깔끔한 이미지"
    echo "  social     - 소셜미디어용 생동감 있는 이미지"
    echo "  luxury     - 럭셔리 브랜드용 고급스러운 이미지"
    echo "  minimal    - 미니멀한 디자인 이미지"
    echo ""
    echo "예시: $0 ./raw_images ./processed marketing"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"
STYLE="$3"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/batch_${STYLE}_${TIMESTAMP}.log"

# API 키 확인
if [ -z "$GEMINI_API_KEY" ] && [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ API 키가 설정되지 않았습니다."
    echo "다음 중 하나를 선택하세요:"
    echo "1. export GEMINI_API_KEY='your-api-key'"
    echo "2. echo 'GEMINI_API_KEY=your-api-key' > $CONFIG_FILE"
    exit 1
fi

# 입력 디렉토리 확인
if [ ! -d "$INPUT_DIR" ]; then
    echo "❌ 입력 디렉토리가 존재하지 않습니다: $INPUT_DIR"
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 스타일별 프롬프트 설정
case "$STYLE" in
    marketing)
        PROMPT="이 이미지를 매력적이고 시선을 끄는 마케팅 이미지로 변환해주세요. 밝고 생동감 있게 만들어주세요."
        ;;
    product)
        PROMPT="이 제품 이미지를 깔끔하고 전문적인 카탈로그용 사진으로 변환해주세요. 제품의 디테일이 잘 보이도록 해주세요."
        ;;
    social)
        PROMPT="이 이미지를 소셜미디어에 적합한 트렌디하고 생동감 있는 스타일로 변환해주세요."
        ;;
    luxury)
        PROMPT="이 이미지를 고급스럽고 세련된 럭셔리 브랜드 이미지로 변환해주세요. 우아하고 프리미엄한 느낌으로 만들어주세요."
        ;;
    minimal)
        PROMPT="이 이미지를 깔끔하고 미니멀한 디자인 스타일로 변환해주세요. 심플하고 모던한 느낌으로 만들어주세요."
        ;;
    *)
        echo "❌ 지원되지 않는 스타일: $STYLE"
        echo "지원되는 스타일: marketing, product, social, luxury, minimal"
        exit 1
        ;;
esac

# 이미지 파일 개수 확인
IMAGE_COUNT=$(find "$INPUT_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.bmp" -o -iname "*.tiff" \) | wc -l)

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "❌ 입력 디렉토리에 이미지 파일이 없습니다: $INPUT_DIR"
    exit 1
fi

echo "🍌 비즈니스 배치 이미지 처리 시작"
echo "================================"
echo "📁 입력: $INPUT_DIR"
echo "📁 출력: $OUTPUT_DIR"
echo "🎨 스타일: $STYLE"
echo "🖼️  이미지 수: $IMAGE_COUNT개"
echo "📝 로그: $LOG_FILE"
echo "💬 프롬프트: $PROMPT"
echo ""

# 확인 메시지
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "작업이 취소되었습니다."
    exit 0
fi

# 시작 시간 기록
START_TIME=$(date)
echo "⏰ 시작 시간: $START_TIME" | tee -a "$LOG_FILE"

# CLI 실행 (설정 파일이 있으면 사용)
CLI_COMMAND="python batch_nanobanana_cli.py \
    --input-dir \"$INPUT_DIR\" \
    --output-dir \"$OUTPUT_DIR\" \
    --prompt \"$PROMPT\" \
    --concurrent 2 \
    --format png \
    --log-file \"$LOG_FILE\" \
    --quiet"

if [ -f "$CONFIG_FILE" ]; then
    CLI_COMMAND="$CLI_COMMAND --config \"$CONFIG_FILE\""
fi

# 처리 실행
echo "🚀 이미지 처리 중..." | tee -a "$LOG_FILE"
if eval "$CLI_COMMAND"; then
    END_TIME=$(date)
    echo "✅ 처리 완료!" | tee -a "$LOG_FILE"
    echo "⏰ 완료 시간: $END_TIME" | tee -a "$LOG_FILE"
    
    # 결과 통계
    PROCESSED_COUNT=$(find "$OUTPUT_DIR" -name "*_generated.png" | wc -l)
    echo "📊 처리 결과: $PROCESSED_COUNT/$IMAGE_COUNT 개 성공" | tee -a "$LOG_FILE"
    
    # 결과 폴더 정보
    echo ""
    echo "📁 결과 폴더: $OUTPUT_DIR"
    echo "📝 로그 파일: $LOG_FILE"
    
    # 첫 번째 결과 이미지 표시 (GUI 환경에서)
    if command -v xdg-open &> /dev/null; then
        FIRST_IMAGE=$(find "$OUTPUT_DIR" -name "*_generated.png" | head -1)
        if [ -n "$FIRST_IMAGE" ]; then
            echo "🖼️  첫 번째 결과 미리보기를 열고 있습니다..."
            xdg-open "$FIRST_IMAGE" 2>/dev/null &
        fi
    fi
    
else
    echo "❌ 처리 중 오류가 발생했습니다." | tee -a "$LOG_FILE"
    echo "📝 자세한 내용은 로그를 확인하세요: $LOG_FILE"
    exit 1
fi

echo ""
echo "🎉 비즈니스 배치 처리가 완료되었습니다!"