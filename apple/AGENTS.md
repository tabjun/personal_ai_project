# AGENTS.md - Codex/Claude Code 공용 작업 지침서

## 목적

이 문서는 이 저장소(`apple/` 하위)에서 Codex와 Claude Code가 매 세션 반드시 따라야 하는
강제 규칙을 정의하는 **단일 source of truth**다. `CLAUDE.md`는 별도 규칙을 담지 않고 이
파일을 가리키는 참조 스텁이다. 규칙을 고칠 때는 이 문서만 고치면 되고, `CLAUDE.md`는
건드릴 필요가 없다(Claude Code 전용 예외가 있다면 그 파일에만 남긴다).

도구별 사설 memory는 보조 정보일 뿐이다. source of truth는 저장소 문서다:
`AGENTS.md`(영구 규칙, Claude Code는 `CLAUDE.md` 스텁을 거쳐 진입) → `process.md`(현재 단계) →
`state.md`(요청 단위 완료 체크) → `history.md`(이력) → `conversation_l2_cache.md`(최근 요청
원문).

### 문서별 역할 (겹치지 않게 유지)

각 문서는 아래 역할 하나만 맡는다. 새 내용을 적을 때 이 표로 어느 파일에 쓸지 먼저 판단한다.

| 문서 | 역할 | 갱신 주체 | 형식 |
| :--- | :--- | :--- | :--- |
| `README.md` | 프로젝트 전체 설명(무엇인지, 왜 하는지) — 거의 안 바뀜 | 사용자+AI | 서술 |
| `AGENTS.md`/`CLAUDE.md` | 항상 적용되는 영구 규칙(source of truth) | 사용자 승인 후 AI | 서술 |
| `process.md` | 분석 단계별 To-Do(무엇을 할 것인가, 단계/실험 단위) | AI | `[x]`/`[ ]` + 서술 |
| `state.md` | **사용자 요청 단위로 "실행됐는가"만** 체크(분석 내용 서술 없음) | AI(요청마다 자동 갱신) | `[x]`/`[ ]`/`[~]` 표 |
| `history.md` | 완료된 작업의 이력(무엇을·왜·어떻게·결과) | AI | 표 |
| `conversation_l2_cache.md` | 사용자 요청 **원문** 보존(최근 20개, 요약 안 함) | AI | 표 |

`process.md`와 `state.md`를 혼동하지 않는다 — `process.md`는 "이 분석을 어떤 순서로 할
것인가"이고, `state.md`는 "사용자가 요청한 각각의 일이 끝났는가"다. 전자는 단계가
바뀔 때만 갱신되고, 후자는 매 요청마다 갱신된다.

이 문서는 **압축 유지가 원칙**이다. 새 사건이 생겨도 문단을 계속 붙이지 않는다. 한 시점
상태는 `process.md`로, 사건 이력은 `history.md`로 보낸다. 여기 남기는 건 "항상 적용되는
짧은 규칙"뿐이다. append 전에 기존 항목과 중복인지 먼저 확인하고, 중복이면 새로 쓰지 않고
기존 항목의 날짜만 갱신한다.

---

## 0. 항상 먼저 읽을 문서

새 세션이 시작되면: `AGENTS.md`(이 파일, Claude Code는 `CLAUDE.md` 스텁을 거쳐 여기로 옴) →
`process.md` → `state.md`(미완료 요청 확인) → `history.md` 최근 섹션 →
`conversation_l2_cache.md` 최근 항목.

---

## 1. Claude ↔ Codex 병행 사용

- 규칙 파일은 이 문서 하나(`AGENTS.md`)뿐이다. Claude Code는 자동으로 읽는 `CLAUDE.md`가
  이 파일을 가리키는 스텁이라 결과적으로 같은 규칙을 본다. 어느 도구로 시작해도 같은
  규칙을 이어받는다.
- **요청을 받을 때마다**: `conversation_l2_cache.md`에 새 인덱스로 요청 원문을 먼저 기록하고,
  같은 인덱스로 `state.md`에 `[ ]`(진행중) 행을 추가한다. 요청을 완료하면 `state.md`의 그
  행을 `[x]`로 갱신한다(중단/보류는 `[~]`).
- **세션 종료 전**: `history.md`에 수행 내용·산출물·다음 목표 한 행 추가, `process.md` 현재
  단계 갱신, `state.md`에 미완료로 남은 항목이 있으면 `[~]`와 비고로 정확히 표시. 방향
  전환이 있었으면 `conversation_l2_cache.md`에 요청 원문 그대로 추가(요약 금지).
- **세션 시작 시**: `process.md` 미완료 체크리스트 → `state.md`의 `[ ]`/`[~]` 행(무엇이
  안 끝났는지) → `history.md` 최근 완료 작업 → `conversation_l2_cache.md` 최근 선호·제약
  순으로 복원한다.

---

## 2. 영구 규칙

> 이 절은 프로젝트별 규칙을 채우는 자리다. 예: 데이터 수집 주기, 지표 정의 고정값,
> 보고서 형식, 커밋 메시지 규칙 등. 아래는 다른 프로젝트에서 검증된 항목 중 이 프로젝트에도
> 적용할 만한 것들의 예시이며, 필요에 맞게 고쳐 쓴다.

### 2.1 커밋 메시지 규칙

- 형식: `<type>(<scope>): <제목>` + 빈 줄 + `무엇을 왜` 본문 + 빈 줄 +
  `Co-Authored-By: <현재 모델명> <noreply@anthropic.com>`.
- 한 커밋에 성격(`feat`/`build`/`refactor`/`fix`/`chore`/`docs`/`test`/`style`/`perf`/`ci`)을
  섞지 않는다 — 여러 성격이면 커밋을 분리한다.

### 2.2 branch·Git 전달 규칙

- 사용자 지시 없으면 작업 브랜치에서만 커밋/푸시. `main`/`develop` 병합은 명시 요청 시만.
- **브랜치별 역할 분리**: 연구/분석 브랜치는 작업 지침 파일을 포함한 전량을 커밋한다.
  `develop`/`main`은 최종 결과물만 올라가는 브랜치라 아래 지침 파일 6종은 **존재 자체를
  제외**한다 — `AGENTS.md`, `CLAUDE.md`, `conversation_l2_cache.md`, `history.md`,
  `process.md`, `state.md`.
  > 이 규칙을 pre-commit 훅(`check_repo_policy.py`)으로 자동 강제할지는 아직 미결정이다
  > (2026-08-24, hookspath가 저장소 전체에 하나뿐이라 다른 프로젝트와 충돌 여지 있음).
  > 훅을 설치하기 전까지는 병합 시 수동으로 이 파일들을 제외한다.

### 2.3 새 파일보다 기존 파일을 우선한다

`AGENTS.md`(+ `CLAUDE.md` 스텁), `process.md`, `state.md`, `history.md`,
`conversation_l2_cache.md`를 먼저 확인하고, 새 파일보다 기존 파일 수정·확장을 우선한다.

---

## 3. 분석 설계 원칙

> 이 절도 프로젝트 성격에 맞게 채운다. 예시: 보고서에 포함할 항목, 데이터 검증 절차,
> 시각화 규칙 등.

---

## 4. 도구 전환 체크리스트

두 도구가 같은 `AGENTS.md`를 보므로(Claude Code는 `CLAUDE.md` 스텁을 거침) 규칙 드리프트
걱정 없이 전환 가능하다.

**Codex → Claude / Claude → Codex 공통**: 변경 파일 커밋/메모 → `history.md` 기록 →
`process.md` 다음 스텝 갱신 → `state.md`에 미완료 항목 정확히 표시. 새 세션은
`AGENTS.md`(또는 `CLAUDE.md` 스텁) → `process.md` → `state.md` → `history.md` →
`conversation_l2_cache.md` 순으로 복원한다. 어느 쪽 memory에만 남긴 결정도 반드시 저장소
파일에 남긴다.
