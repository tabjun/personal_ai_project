# personal_ai_project

개인 AI 프로젝트들을 한 저장소에서 관리하는 루트 저장소다. 현재는 크게 두 영역을 포함한다.

## 프로젝트 개요

1. `quantitative_trading`
   - 금융 시계열 연구, 실험 노트북, 파이프라인, 보고서 자동화가 들어 있는 메인 연구 프로젝트다.
   - 학교 서버의 Jupyter 커널, uv venv, 연구 문서 규칙을 기준으로 운영한다.

2. `resum`
   - 이력서, 자기소개서, 관련 자료를 관리하는 문서 중심 프로젝트다.
   - 민감한 개인정보 파일은 `.gitignore`로 제한하고 템플릿/가이드만 남긴다.

## 서버 환경과 Web VS Code

이 저장소는 학교 JupyterHub 서버 환경에서도 사용한다. 브라우저에서 서버 파일과 터미널을 직접 다루기 위해 `code-server` 기반 Web VS Code 유틸리티를 함께 관리한다.

- 위치: `tools/vscode/`
- 상세 문서: `tools/vscode/README.md`
- 기본 접속 주소: `https://stat5.kmu.ac.kr:9500/user/std_jun99120/proxy/9999/`

기본 명령:

```bash
~/personal_ai_project/tools/vscode/start-vscode.sh start
~/personal_ai_project/tools/vscode/start-vscode.sh status
~/personal_ai_project/tools/vscode/start-vscode.sh stop
```

특정 프로젝트를 바로 열고 싶으면 `start` 뒤에 경로를 넘긴다.

```bash
~/personal_ai_project/tools/vscode/start-vscode.sh start ~/personal_ai_project/quantitative_trading
```

## 왜 저장소에 커밋했나

- 홈 디렉터리 루트에 두면 개인 환경 파일과 섞여 Git 추적 범위가 흐려진다.
- `quantitative_trading` 외 다른 프로젝트에서도 같은 웹 VS Code 런처를 재사용할 수 있다.
- 실행 방법, 저장 경로, 상태 파일 위치를 문서와 함께 버전관리해야 서버 재시작 후에도 복구가 쉽다.
