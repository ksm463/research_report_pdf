# 연구 보고서 PDF 생성기

이 프로젝트는 연구 보고서를 자동으로 PDF 형식으로 만들어주는 Python 기반의 간단한 도구입니다. CSV 파일로부터 데이터를 읽어오고, 이미지 프레임과 결합해 보기 좋은 형태의 PDF 문서를 생성할 수 있습니다. Docker를 이용해 환경 설정을 간단하게 하고, 어디서든 같은 방식으로 실행할 수 있도록 구성했습니다.

## 주요 기능

* **자동 PDF 생성:** CSV 파일의 데이터를 기반으로 PDF 보고서를 자동으로 생성합니다.
* **유연한 페이지 레이아웃:** 여백, 섹션 비율, 프레임 경계 등을 설정 파일을 통해 자유롭게 조정할 수 있습니다.
* **예시 이미지 삽입:** 보고서에 예시 이미지 프레임을 삽입할 수 있습니다.
* **설정 파일 기반 구성:** `config.ini` 파일을 사용하여 경로, 파라미터, 비율 등을 간단히 관리할 수 있습니다.
* **글꼴 사용자 지정:** 전문적인 보고서 형식을 위해 사용자 정의 글꼴(TTF) 사용이 가능합니다.
* **Topcut 모드:** PDF에서 상단 프레임이 필요 없는 모드를 지원합니다.
* **통합 문서 모드:** 여러 페이지를 포함한 하나의 PDF 파일을 생성하는 모드를 지원합니다.
* **Docker 환경 지원:** 애플리케이션 및 모든 종속성이 Docker 컨테이너에 포함되어 있어 설정 및 배포가 간단합니다.

## 작성 예시
![Image](https://github.com/user-attachments/assets/85017bf9-69ca-4065-be85-ede830c3f34e)
* 위 예시에 나온 파일 이름과 영상 이미지는 예시를 위해 생성된 이미지로 실제와 무관합니다.

## 준비 사항

* **Docker:** 시스템에 Docker가 설치되어 있어야 합니다.
* **CSV 데이터:** 다음 열을 포함하는 CSV 파일을 준비하세요.
    * `주차`: 주차 번호 (정수)
    * `할당일`: 할당 날짜 (YYYY-MM-DD 형식)
    * `작업자 이름(영문)`: 작업자의 이름
    * `직책`: 작업자의 직책
    * `파일명`: 관련된 비디오 또는 이미지 파일명
    * `요일` : 작업 요일 (월화수목금)
* **비디오 또는 이미지**: CSV 데이터의 파일명과 일치하는 비디오 또는 이미지를 준비하세요.
* **글꼴 파일:** 사용자 정의 TTF 글꼴 파일(예: `NanumGothic.ttf`)을 지정된 글꼴 디렉터리에 배치하세요.

## 설치 및 사용 방법

### 1. 저장소 클론

```bash
git clone <your_repository_url>
cd research_report_pdf
```

### 2. config.ini 설정
`src/research_report/` 디렉터리 내의 `config.ini` 파일을 수정하여 시스템의 경로 및 환경설정에 맞게 조정하세요.
- PATHS: PDF_PATH, CSV_PATH, VIDEO_PATH, IMAGE_PATH, FONT_PATH, LOG_PATH 등 경로 설정
- PARAMETERS: START_WEEK, TARGET_WEEK, MAX_ROWS, FRAME_BOUNDARY, TOPCUT_MODE, TOTAL_DOCUMENT, VIDEO_MODE 조정
- PAGE_SIZE: 페이지 크기 설정 (기본값: A4)
- RATIOS: 여백, 상단, 중간, 하단 섹션의 비율 설정
- TOP_RATIOS, MIDDLE_RATIOS, BOTTOM_RATIOS: 표 열 너비 및 이미지 비율 조정

### 3. Docker 이미지 빌드
아래 명령어로 build_docker.sh를 실행하여 Docker 이미지를 빌드하세요.

```bash
sh build_docker.sh
```

### 4. Docker 컨테이너 실행
빌드가 완료된 뒤에 run_docker.sh로 컨테이너를 실행하세요.

```bash
sh run_docker.sh
```

### 5. PDF 생성
터미널에서 `src/research_report/` 경로로 이동하여 `main.py`를 실행하세요

```bash
cd src/research_report
python main.py
```

* 생성된 PDF 파일은 `config.ini` 파일에서 설정된 `PDF_PATH` 위치에 저장됩니다.
* 로그 파일은 `LOG_PATH`에 저장됩니다.


## 라이선스

[MIT License]

## 프로젝트 구조

```bash
research_report_pdf/
├── src/
│   └── research_report/
│       ├── calculator.py    # 레이아웃 계산 및 이미지 병합 로직
│       ├── config.ini       # 경로 및 설정값을 담는 구성 파일
│       ├── frames.py        # 프레임 설정 및 콘텐츠 생성
│       ├── logger.py        # 로깅 모듈 설정
│       └── main.py          # PDF 생성 메인 스크립트
├── Dockerfile                # Docker 구성 파일
└── README.md                 # 프로젝트 문서(본 파일)
```

