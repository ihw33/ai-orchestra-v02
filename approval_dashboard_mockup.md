# 📱 승인 대시보드 UI 목업

## 데스크톱 버전 (터미널)
```
╔══════════════════════════════════════════════════════════════════════╗
║                    🎯 THOMAS 승인 대기 큐                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ ┌──────────────────────────────────────────────────────────────────┐ ║
║ │ Issue #42: [Tycoon] Project Tycoon 게임화 대시보드 시스템        │ ║
║ │ ChatGPT 리서치 요청 - Football Manager와 픽셀 타이쿤 분석       │ ║
║ │                                                                  │ ║
║ │ [✅ 승인]  [⏸️ 보류]  [❌ 거절]  [💬 코멘트]                   │ ║
║ └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║ ┌──────────────────────────────────────────────────────────────────┐ ║
║ │ PR #49: [리서치] Project Tycoon 게임 벤치마킹                   │ ║
║ │ ChatGPT 작업 지시서 - 45분 소요 예상, 표준 템플릿 적용         │ ║
║ │                                                                  │ ║
║ │ [✅ 승인]  [⏸️ 보류]  [❌ 거절]  [💬 코멘트]                   │ ║
║ └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║ ┌──────────────────────────────────────────────────────────────────┐ ║
║ │ Issue #47: [Mobile] iPhone 대시보드 접근                        │ ║
║ │ 모바일 웹 인터페이스 구축 - Tailscale/ngrok 보안 접근           │ ║
║ │                                                                  │ ║
║ │ [✅ 승인]  [⏸️ 보류]  [❌ 거절]  [💬 코멘트]                   │ ║
║ └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║ 키보드: [1-3] 선택 | [A]pprove | [H]old | [R]eject | [C]omment       ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 모바일 버전 (iPhone)

### 리스트 뷰
```
┌─────────────────────────────┐
│ 🎯 승인 대기 (3)        ⚙️  │
├─────────────────────────────┤
│                             │
│ #42 Project Tycoon 🎮       │
│ ChatGPT 리서치 요청         │
│ ─────────────────────────   │
│ ✅ 승인  ⏸️ 보류  ❌ 거절   │
│                             │
│ ─────────────────────────── │
│                             │
│ #49 게임 벤치마킹 📊        │
│ 45분 리서치 작업            │
│ ─────────────────────────   │
│ ✅ 승인  ⏸️ 보류  ❌ 거절   │
│                             │
│ ─────────────────────────── │
│                             │
│ #47 Mobile Dashboard 📱     │
│ iPhone 접근 시스템          │
│ ─────────────────────────   │
│ ✅ 승인  ⏸️ 보류  ❌ 거절   │
│                             │
└─────────────────────────────┘
```

### 카드 스와이프 뷰
```
┌─────────────────────────────┐
│         < 1 / 3 >           │
├─────────────────────────────┤
│                             │
│   Issue #42                 │
│   ━━━━━━━━━━━━━━━━━━━━━    │
│                             │
│   🎮 Project Tycoon         │
│   게임화 대시보드            │
│                             │
│   ChatGPT에게 Football      │
│   Manager와 픽셀 타이쿤      │
│   게임 리서치 요청           │
│                             │
│   예상시간: 45분            │
│   담당: ChatGPT (Cursor)    │
│                             │
│ ┌─────────────────────────┐ │
│ │      ✅ 승인하기        │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │      ⏸️ 보류하기        │ │
│ └─────────────────────────┘ │
│                             │
│ ← 스와이프: 거절  승인: → │
└─────────────────────────────┘
```

## 웹 버전 (반응형)

### HTML/CSS 구조
```html
<div class="approval-card">
  <div class="issue-header">
    <span class="issue-number">#42</span>
    <span class="issue-title">Project Tycoon 게임화 대시보드</span>
  </div>
  <div class="issue-summary">
    ChatGPT 리서치 요청 - Football Manager와 픽셀 타이쿤 분석
  </div>
  <div class="action-buttons">
    <button class="btn-approve">✅ 승인</button>
    <button class="btn-hold">⏸️ 보류</button>
    <button class="btn-reject">❌ 거절</button>
    <button class="btn-comment">💬 코멘트</button>
  </div>
</div>
```

### 스타일 (Tailwind CSS)
```css
.approval-card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-4;
}

.issue-header {
  @apply flex items-center gap-2 mb-2;
}

.issue-number {
  @apply text-blue-600 font-mono font-bold;
}

.issue-title {
  @apply text-lg font-semibold;
}

.issue-summary {
  @apply text-gray-600 dark:text-gray-400 mb-4;
}

.action-buttons {
  @apply flex gap-2 flex-wrap;
}

.btn-approve {
  @apply bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded;
}

.btn-hold {
  @apply bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded;
}

.btn-reject {
  @apply bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded;
}

.btn-comment {
  @apply bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded;
}
```

## 기능 명세

### 버튼 동작
- **승인**: `gh issue comment {number} -b "✅ 승인되었습니다"` + 라벨 변경
- **보류**: `gh issue comment {number} -b "⏸️ 보류"` + 라벨 'on-hold'
- **거절**: `gh issue comment {number} -b "❌ 거절"` + 이슈 close
- **코멘트**: 텍스트 입력 모달 → `gh issue comment`

### 실시간 업데이트
- WebSocket으로 새 이슈/PR 추가
- 승인/거절 시 즉시 리스트에서 제거
- 알림 배지 카운트 업데이트

### 우선순위 표시
- 🔴 Critical: 빨간 테두리
- 🟡 Important: 노란 테두리  
- 🟢 Normal: 기본
- 🔵 Info: 파란 테두리