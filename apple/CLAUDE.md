# CLAUDE.md - Claude Code 작업 지침서

**규칙 본문은 [`AGENTS.md`](AGENTS.md)를 source of truth로 본다.** 이 파일은 Claude Code가
세션 시작 시 자동으로 읽는 파일명(`CLAUDE.md`)만 맞추기 위한 참조 스텁이다 — Codex가 읽는
`AGENTS.md`와 규칙을 물리적으로 두 곳에 중복 관리하지 않기 위함이다.

새 세션이 시작되면 이 파일 대신 `AGENTS.md` → `process.md` → `history.md` 최근 섹션 →
`conversation_l2_cache.md` 최근 항목 순으로 읽는다.

Claude Code 전용 차이점(Codex와 다른 점)이 생기면 여기에만 적는다. 현재는 없음 — 전부
`AGENTS.md`를 따른다.
