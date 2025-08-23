# 🤖 AI Agent 자동 활성화 프롬프트 가이드

## 📋 목적
AI 오케스트레이션 자동화 프로세스에서 Claude Code 에이전트들이 효과적으로 활성화되도록 하는 프롬프트 전략

---

## 🎯 핵심 에이전트 활성화 프롬프트

### 1. 코드 리뷰 자동화
```markdown
# 트리거 키워드
- "리뷰", "review", "코드 검토", "PR 확인"
- "버그 찾기", "문제점 분석", "개선점 제안"

# 최적화 프롬프트
"이 PR/코드를 iwl-code-reviewer 에이전트로 철저히 검토하고, 
보안/성능/가독성 측면에서 개선사항을 제시해주세요."
```

### 2. 복잡한 검색 작업
```markdown
# 트리거 키워드
- "깊이 조사", "comprehensive search", "모든 파일 검색"
- "패턴 찾기", "전체 코드베이스 분석"

# 최적화 프롬프트
"general-purpose 에이전트를 사용하여 이 주제에 대해 
다단계 검색을 수행하고 종합적인 결과를 제공해주세요."
```

### 3. API 문서화
```markdown
# 트리거 키워드
- "API 문서", "Swagger", "OpenAPI spec"
- "엔드포인트 문서화", "SDK 생성"

# 최적화 프롬프트
"api-documenter 에이전트로 이 API의 OpenAPI 3.0 스펙을 생성하고,
사용 예제와 함께 개발자 문서를 작성해주세요."
```

### 4. 프롬프트 최적화
```markdown
# 트리거 키워드
- "프롬프트 개선", "LLM 최적화", "더 나은 응답"
- "에이전트 성능 향상"

# 최적화 프롬프트
"prompt-engineer 에이전트를 사용하여 이 프롬프트를 
더 효과적으로 개선하고 체계적인 프롬프트 패턴을 적용해주세요."
```

---

## 🔄 자동화 워크플로우 통합

### GitHub Issue 기반 자동화
```yaml
# workflow.yaml 예시
name: AI Agent Automation
trigger: 
  - issue_created
  - pr_opened
  
steps:
  - name: Analyze Request
    prompt: |
      분석 단계:
      1. 이슈/PR 타입 파악
      2. 필요한 에이전트 자동 선택
      3. 병렬 실행 가능 작업 식별
      
  - name: Execute Agents
    parallel: true
    agents:
      - type: iwl-code-reviewer
        condition: "PR이거나 코드 변경 시"
      - type: api-documenter
        condition: "API 변경 시"
      - type: business-analyst
        condition: "메트릭/KPI 언급 시"
```

### 다중 AI 협업 패턴
```markdown
# Relay Pattern (릴레이 패턴)
"먼저 search-specialist로 정보를 수집한 후,
business-analyst로 분석하고,
최종적으로 ui-ux-designer로 대시보드를 설계해주세요."

# Parallel Pattern (병렬 패턴)
"동시에 다음 작업을 수행해주세요:
- backend-architect: API 설계
- api-documenter: 문서 생성
- prompt-engineer: 테스트 프롬프트 작성"

# Review Cycle Pattern (리뷰 사이클 패턴)
"코드 작성 → iwl-code-reviewer 검토 → 
수정 → 재검토 사이클을 자동으로 수행해주세요."
```

---

## 🛠 추가 권장 기능

### 1. Claude Code Templates 활용
```bash
# 에이전트 스택 빌더
npx claude-code-templates@latest --agent customer-support,code-reviewer

# 워크플로우 해시 활용
npx claude-code-templates@latest --workflow #auto-review-fix-cycle

# 분석 대시보드
npx claude-code-templates@latest --analytics --tunnel
```

### 2. MCP 서버 통합
```json
{
  "mcpServers": {
    "github": {
      "command": "mcp-server-github",
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "obsidian": {
      "command": "mcp-server-obsidian",
      "args": ["--vault", "/path/to/vault"]
    }
  }
}
```

### 3. Hook 자동화
```bash
# PR 생성 시 자동 리뷰
echo '#!/bin/bash
if [[ "$1" == "pr_created" ]]; then
  claude exec "iwl-code-reviewer로 PR #$2 리뷰"
fi' > ~/.claude/hooks/pr-auto-review.sh
```

### 4. 성능 모니터링
```javascript
// performance_tracker.js
const trackAgentPerformance = {
  beforeAgent: (agentType, task) => {
    console.time(`${agentType}_execution`);
    logToFile({ agent: agentType, task, startTime: Date.now() });
  },
  afterAgent: (agentType, result) => {
    console.timeEnd(`${agentType}_execution`);
    updateMetrics(agentType, result);
  }
};
```

---

## 📈 최적화 메트릭

### 추적할 KPI
1. **에이전트 활성화율**: 자동 vs 수동 실행 비율
2. **작업 완료 시간**: 에이전트별 평균 실행 시간
3. **병렬 처리 효율**: 동시 실행 에이전트 수
4. **오류율**: 에이전트 실패/재시도 빈도
5. **컨텍스트 효율성**: 토큰 사용량 대비 결과 품질

### 모니터링 명령
```bash
# 실시간 모니터링
npx claude-code-templates@latest --analytics

# 에이전트 통계
npx claude-code-templates@latest --command-stats

# Hook 효율성
npx claude-code-templates@latest --hook-stats
```

---

## 🚀 즉시 적용 가능한 개선사항

### 1. 현재 프로젝트에 추가할 프롬프트
```markdown
"모든 코드 변경 시 자동으로:
1. iwl-code-reviewer로 검토
2. 문제 발견 시 자동 수정
3. 수정 후 재검토
4. PR 코멘트 자동 생성"
```

### 2. 글로벌 에이전트 생성
```bash
# AI 오케스트레이션 전용 에이전트
npx claude-code-templates@latest --create-agent orchestra-conductor

# 설정 내용
{
  "name": "orchestra-conductor",
  "description": "Multi-AI coordination and automation",
  "capabilities": [
    "github_integration",
    "parallel_execution",
    "auto_review_cycle"
  ]
}
```

### 3. 자동화 체크리스트
- [ ] 각 AI CLI의 -p/exec 모드 프롬프트 템플릿화
- [ ] GitHub Webhook → 에이전트 자동 실행 설정
- [ ] 병렬 작업 식별 로직 구현
- [ ] 실시간 모니터링 대시보드 설정
- [ ] 에러 복구 및 재시도 메커니즘

---

## 📝 결론

효과적인 에이전트 활성화를 위해:
1. **명확한 트리거 키워드** 사용
2. **작업 타입별 에이전트 매핑** 정의
3. **병렬/순차 실행 패턴** 적용
4. **실시간 모니터링** 구축
5. **지속적인 프롬프트 최적화**

이를 통해 90% 이상의 작업을 자동화하고,
AI 협업 효율을 극대화할 수 있습니다.