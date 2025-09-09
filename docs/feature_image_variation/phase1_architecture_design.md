# Phase 1: 아키텍처 설계 및 핵심 모듈 구현

## 📋 개요
이미지 변형 생성 기능의 핵심 아키텍처를 설계하고, 기본적인 변형 생성 로직을 구현하는 단계입니다.

## 🎯 목표
- ImageVariationProcessor 클래스 설계 및 구현
- 변형 생성 로직 및 프롬프트 엔진 개발
- 기존 ImageProcessor와의 통합 인터페이스 구현
- 변형 스타일 및 파라미터 정의 시스템

## 🏗️ 아키텍처 설계

### 1. ImageVariationProcessor 클래스
```python
class ImageVariationProcessor(ImageProcessor):
    """이미지 변형 생성을 위한 전문 프로세서"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image-preview"):
        super().__init__(api_key, model)
        self.variation_engine = VariationEngine()
        self.prompt_generator = VariationPromptGenerator()
    
    def generate_variations(self, image_path: Path, count: int, 
                          variation_type: str = "random") -> List[Dict]:
        """이미지의 다양한 변형을 생성"""
        pass
```

### 2. VariationEngine 클래스
```python
class VariationEngine:
    """변형 로직의 핵심 엔진"""
    
    VARIATION_TYPES = {
        'random': '임의 변형',
        'object_rearrange': '객체 재배치',
        'object_add': '객체 추가',
        'object_remove': '객체 제거',
        'style_change': '스타일 변경',
        'composition': '구도 변경'
    }
    
    def create_variation_prompt(self, base_image: Image, variation_id: int) -> str:
        """변형별 고유 프롬프트 생성"""
        pass
```

### 3. VariationPromptGenerator 클래스
```python
class VariationPromptGenerator:
    """변형 프롬프트 생성 전문 클래스"""
    
    def __init__(self):
        self.object_templates = self._load_object_templates()
        self.style_templates = self._load_style_templates()
        self.composition_templates = self._load_composition_templates()
    
    def generate_prompt(self, variation_type: str, seed: int) -> str:
        """변형 타입과 시드에 따른 프롬프트 생성"""
        pass
```

## 🔧 구현 세부사항

### 1. 변형 타입 정의
- **Object Rearrangement**: 기존 객체들의 위치 변경
- **Object Addition**: 새로운 객체 추가
- **Object Removal**: 기존 객체 제거
- **Style Modification**: 전체적인 스타일 변경
- **Composition Change**: 화면 구도 변경

### 2. 프롬프트 템플릿 시스템
```python
PROMPT_TEMPLATES = {
    'object_rearrange': [
        "Rearrange the objects in this image: move the {object1} to the {position1} and place the {object2} {position2}",
        "Reorganize the composition by repositioning the {object1} and {object2} while keeping the same style",
        "Change the layout by moving {object1} to {direction} and adjusting other elements accordingly"
    ],
    'object_add': [
        "Add a {new_object} to this scene in a natural way that fits the composition",
        "Include additional {object_type} elements to enhance the scene",
        "Insert {count} {objects} into the image while maintaining the original atmosphere"
    ],
    'object_remove': [
        "Remove the {target_object} from this image and fill the space naturally",
        "Take out {object_list} while preserving the overall composition",
        "Clean up the image by removing {unwanted_elements}"
    ]
}
```

### 3. 변형 품질 보장
- **Diversity Score**: 변형 간 차이점 측정
- **Quality Check**: 생성된 이미지의 품질 검증
- **Duplication Prevention**: 중복 결과 방지 알고리즘

## 🔗 기존 시스템과의 통합

### 1. batch_nanobanana_core.py 확장
- ImageProcessor 클래스 상속
- 기존 배치 처리 로직 재사용
- 설정 관리 시스템 활용

### 2. 새로운 메서드 추가
```python
# batch_nanobanana_core.py에 추가할 메서드들
def process_single_variation(self, image_path: Path, variation_prompt: str, 
                           output_path: Path) -> Dict[str, any]:
    """단일 변형 처리"""

def process_variation_batch(self, image_path: Path, count: int, 
                          output_dir: Path, variation_type: str = "random") -> Dict[str, any]:
    """변형 배치 처리"""
```

## 📊 성능 고려사항

### 1. 메모리 최적화
- 이미지 로딩 최적화
- 배치 처리 시 메모리 관리
- 중간 결과물 캐싱

### 2. API 호출 최적화
- 동시 요청 수 제한
- 재시도 로직 구현
- 에러 처리 강화

## 🗂️ 파일 구조
```
batch_nanobanana_core.py
├── ImageProcessor (기존)
├── ImageVariationProcessor (신규)
├── VariationEngine (신규)
├── VariationPromptGenerator (신규)
└── ConfigManager (기존 활용)
```

## ✅ 완료 기준
- [ ] ImageVariationProcessor 클래스 구현 완료
- [ ] VariationEngine 기본 로직 구현
- [ ] 프롬프트 템플릿 시스템 구축
- [ ] 기존 시스템과의 통합 테스트 통과
- [ ] 단일 이미지 변형 생성 기능 동작 확인

## 🔄 다음 단계
Phase 2에서는 이 핵심 모듈을 활용하여 GUI 인터페이스를 확장하게 됩니다.