# 📱 Mobile Dashboard 작업 지시서

## Issue #47: iPhone 대시보드 시스템

---

## 🎨 ChatGPT (Cursor CLI) - 기획 담당

### 작업 지시
```bash
cursor exec "다음 모바일 대시보드를 기획해주세요:

1. **사용자 시나리오**
   - Thomas가 iPhone에서 프로젝트 상태 확인
   - 외출 중 긴급 PR 승인
   - 알림 받고 즉시 의사결정

2. **UI/UX 설계**
   - 모바일 최적화 레이아웃
   - 원터치 승인 시스템
   - 스와이프 제스처 활용

3. **화면 구성**
   - 메인 대시보드 (게임 상태)
   - PR/Issue 리스트
   - 빠른 승인 화면
   - 팀 모니터링

4. **알림 전략**
   - Critical: 즉시 푸시
   - Important: 배지 알림
   - Info: 대시보드 표시

결과물: MOBILE_UX_DESIGN.md 파일 생성"
```

### 예상 산출물
- 와이어프레임 설명
- 사용자 플로우
- 인터랙션 패턴
- 알림 우선순위

---

## 🔧 Codex CLI - 기술 검토 담당

### 작업 지시
```bash
codex exec "다음 모바일 시스템의 기술적 가능성을 검토해주세요:

## 요구사항
1. **웹 서버**
   - FastAPI/Flask 경량 서버
   - WebSocket 실시간 통신
   - GitHub API 프록시

2. **보안**
   - Tailscale VPN vs ngrok 터널
   - OAuth 2.0 인증
   - 세션 관리

3. **프론트엔드**
   - React/Vue 반응형 SPA
   - PWA 지원
   - 오프라인 캐싱

4. **인프라**
   - Docker 컨테이너화
   - 자동 배포 파이프라인
   - 모니터링 시스템

## 검토 항목
- 구현 난이도 (1-10)
- 예상 개발 시간
- 보안 리스크
- 필요 리소스
- 대안 솔루션

결과물: MOBILE_TECH_REVIEW.md 파일 생성"
```

### 예상 산출물
- 아키텍처 다이어그램
- 기술 스택 추천
- 보안 체크리스트
- 구현 로드맵

---

## 📊 PM Claude - 종합 보고

### Thomas 보고 내용
1. **ChatGPT 기획안 요약**
2. **Codex 기술 검토 요약**
3. **추천 진행 방안**
4. **리스크 및 대안**
5. **예상 일정 및 리소스**

---

## 🚀 실행 명령

### 1. ChatGPT에게 지시 (터미널 1)
```bash
cursor exec < chatgpt_mobile_planning.txt
```

### 2. Codex에게 지시 (터미널 2)
```bash
codex exec < codex_tech_review.txt
```

### 3. 결과 수집 후 Thomas 보고
```bash
cat MOBILE_UX_DESIGN.md MOBILE_TECH_REVIEW.md > MOBILE_PROPOSAL.md
```

---

## ⏰ 예상 일정
- ChatGPT 기획: 30분
- Codex 검토: 30분
- PM 종합: 15분
- **총 소요시간**: 1시간 15분

Thomas 승인 대기 중...