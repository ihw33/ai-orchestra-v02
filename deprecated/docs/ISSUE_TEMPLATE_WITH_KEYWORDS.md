# 📝 이슈 템플릿 (키워드 강화 버전)

## 🎯 목표
[한 줄로 명확한 목표]

## 🎭 페르소나: [speedster/perfectionist/critic/minimalist/balanced]
- **특성**: [페르소나 특징]
- **목표 시간**: [예상 시간]
- **작업 스타일**: [스타일 설명]

## 🔷 Node-DAG-Executor 구조

### 📊 워크플로우: [Parallel/Relay/Pipeline]
```
[DAG 다이어그램]
예시:
    [ANALYZE]
        ↓
   ┌────┴────┐
[IMPLEMENT] [TEST]
   └────┬────┘
        ↓
    [DEPLOY]
```

### 🔹 노드 정의

#### Node 1: [NODE_NAME]
- **타입**: [ANALYZE_CODE/WRITE_FUNCTION/TEST/etc]
- **실행자**: [Gemini/Claude/Codex/PM]
- **입력**: [입력 데이터]
- **출력**: [예상 출력]
- **페르소나 지시**: [구체적 지시]
- **예상 시간**: [시간]

#### Node 2: [NODE_NAME]
- **타입**: [타입]
- **실행자**: [AI 이름]
- **입력**: [입력]
- **출력**: [출력]
- **페르소나 지시**: [지시]
- **예상 시간**: [시간]

### 🚀 페르소나별 AI 지시사항

#### Gemini ([페르소나])
```
[구체적 지시사항]
```

#### Claude ([페르소나])
```
[구체적 지시사항]
```

#### Codex ([페르소나])
```
[구체적 지시사항]
```

## 📋 체크리스트
- [ ] [작업 1]
- [ ] [작업 2]
- [ ] [작업 3]
- [ ] [작업 4]

## ✅ 완료 조건
1. [측정 가능한 완료 조건 1]
2. [측정 가능한 완료 조건 2]
3. [측정 가능한 완료 조건 3]

## 🚀 실행 명령
```bash
# 이 이슈 번호로 바로 실행
python3 multi_ai_orchestrator.py [ISSUE_NUMBER]
# 또는 직접 실행
./pm_direct_workflow.sh "제목" "설명"
```

## 🏷️ 키워드
[해시태그 섹션 - 자동/수동 추가]
#키워드1 #키워드2 #키워드3

---

### 📌 라벨 추천 (GitHub Labels)
```bash
# 자동 추천 실행
python3 issue_keyword_recommender.py

# 추천 라벨 (프로세스)
- [ ] analysis
- [ ] research
- [ ] implementation
- [ ] testing
- [ ] documentation

# DAG 패턴
- [ ] parallel
- [ ] relay
- [ ] pipeline
```

### #️⃣ 해시태그 추천 (본문용)
```
# 주제 태그
#백업시스템 #자동화 #모니터링 #API #데이터베이스

# 기술 태그
#python #javascript #bash #docker #kubernetes

# 플랫폼 태그
#macOS #windows #linux
```

---

## 사용 예시

### 1. 분석 작업
```yaml
목표: "시스템 성능 분석 및 개선점 도출"
페르소나: perfectionist
워크플로우: parallel
라벨: analysis, research, documentation
해시태그: #성능분석 #최적화 #모니터링
```

### 2. 버그 수정
```yaml
목표: "긴급 버그 수정"
페르소나: speedster
워크플로우: relay
라벨: testing, implementation
해시태그: #버그수정 #핫픽스 #긴급
```

### 3. 기능 개발
```yaml
목표: "새 기능 구현"
페르소나: balanced
워크플로우: pipeline
라벨: implementation, testing, documentation
해시태그: #신기능 #개발 #API
```