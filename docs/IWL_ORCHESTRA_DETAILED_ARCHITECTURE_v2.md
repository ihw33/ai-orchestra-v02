# IWL Orchestra 상세 아키텍처 v2.0 (2025-08-28)

## 🏛️ IWL v5.0 Orchestra 전체 시스템 아키텍처

### 시스템 개요
IWL Orchestra는 교육 콘텐츠 관리와 AI 기반 학습을 통합한 차세대 교육 플랫폼입니다. 마이크로서비스 아키텍처를 채택하여 확장성과 유지보수성을 극대화했습니다.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         IWL Orchestra v5.0 Ecosystem                        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        사용자 인터페이스 레이어                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  웹 앱     │  │  모바일    │  │   API      │  │  관리자    │    │  │
│  │  │  (Next.js) │  │  (React    │  │  클라이언트 │  │  대시보드  │    │  │
│  │  │            │  │   Native)  │  │            │  │            │    │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │  │
│  └────────┼───────────────┼───────────────┼───────────────┼────────────┘  │
│           └───────────────┴───────────────┴───────────────┘                │
│                                    │                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Main Platform (iwl-v5-rebuild)                    │  │
│  │                            포트: 3000                                  │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │                      API Gateway Layer                        │   │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │  │
│  │  │  │  JWT     │  │  Rate    │  │  CORS    │  │  Request │   │   │  │
│  │  │  │  Auth    │→ │  Limiter │→ │  Handler │→ │  Router  │   │   │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │                    비즈니스 로직 레이어                         │   │  │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐│   │  │
│  │  │  │  사용자    │  │  콘텐츠    │  │  학습     │  │  결제  ││   │  │
│  │  │  │  관리      │  │  관리      │  │  경로     │  │  처리  ││   │  │
│  │  │  └────────────┘  └────────────┘  └────────────┘  └────────┘│   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │                     데이터 접근 레이어                          │   │  │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐│   │  │
│  │  │  │  Supabase  │  │  Prisma    │  │  Redis     │  │  S3    ││   │  │
│  │  │  │  Client    │  │  ORM       │  │  Cache     │  │  Store ││   │  │
│  │  │  └────────────┘  └────────────┘  └────────────┘  └────────┘│   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                      │                                   │
│                    ┌─────────────────┴─────────────────┐                │
│                    ↓                                   ↓                │
│  ┌─────────────────────────────┐   ┌─────────────────────────────┐    │
│  │   KB System (iwl-kb-system) │   │  LLM Service (ai-engine-hub) │    │
│  │         포트: 8002           │   │          포트: 8888          │    │
│  └──────────────┬───────────────┘   └────────────┬──────────────┘    │
└─────────────────┼──────────────────────────────────┼──────────────────┘
                  │                                   │
                  ↓                                   ↓
```

### 🎯 사용자 인터페이스 레이어 상세

#### 웹 앱 (Next.js 15.4.2)
- **서버 사이드 렌더링 (SSR)**: SEO 최적화 및 초기 로딩 속도 개선
- **정적 사이트 생성 (SSG)**: 콘텐츠 페이지 사전 렌더링
- **Incremental Static Regeneration (ISR)**: 실시간 콘텐츠 업데이트
- **React 19.1.0**: 최신 Concurrent Features 활용
- **TypeScript 5**: 타입 안정성 보장

#### 모바일 앱 (React Native)
- **Cross-platform**: iOS/Android 동시 지원
- **Native 성능**: 네이티브 브릿지 최적화
- **오프라인 지원**: 로컬 캐싱 및 동기화
- **Push 알림**: FCM/APNS 통합

#### API 클라이언트
- **SDK 제공**: JavaScript, Python, Java SDK
- **OpenAPI 3.0**: Swagger 문서 자동 생성
- **GraphQL**: 유연한 데이터 쿼리 지원
- **WebSocket**: 실시간 통신 지원

#### 관리자 대시보드
- **실시간 모니터링**: 시스템 상태 및 메트릭
- **콘텐츠 관리**: WYSIWYG 에디터
- **사용자 분석**: 학습 패턴 및 진도 추적
- **A/B 테스팅**: 기능 실험 관리

### 🏗️ Main Platform 상세 구조

#### API Gateway Layer 세부 구성

##### JWT Authentication
```typescript
// JWT 토큰 구조
{
  header: {
    alg: "RS256",
    typ: "JWT"
  },
  payload: {
    sub: "user_id",
    email: "user@example.com",
    roles: ["student", "premium"],
    exp: 1735430400,
    iat: 1735344000
  },
  signature: "..."
}
```
- **토큰 수명**: Access Token 15분, Refresh Token 7일
- **토큰 검증**: RSA 공개키 검증
- **토큰 갱신**: 자동 갱신 메커니즘
- **블랙리스트**: Redis 기반 토큰 무효화

##### Rate Limiter (@upstash/ratelimit)
```typescript
// Rate Limiting 정책
{
  anonymous: "10 requests per minute",
  authenticated: "100 requests per minute", 
  premium: "1000 requests per minute",
  api_key: "10000 requests per hour"
}
```
- **Sliding Window**: 정확한 요청 제한
- **Token Bucket**: 버스트 트래픽 허용
- **IP 기반 제한**: DDoS 방어
- **사용자별 할당량**: 플랜별 차등 적용

##### CORS Handler
- **화이트리스트 도메인**: 사전 등록된 도메인만 허용
- **Preflight 캐싱**: OPTIONS 요청 최적화
- **Credentials 지원**: 쿠키/인증 헤더 전송
- **동적 Origin 검증**: 환경별 설정

##### Request Router
- **경로 매칭**: 정규식 기반 라우팅
- **미들웨어 체인**: 순차적 처리 파이프라인
- **에러 핸들링**: 중앙화된 에러 처리
- **Request ID**: 추적을 위한 고유 ID 생성

#### 비즈니스 로직 레이어 세부 기능

##### 사용자 관리
- **회원가입/로그인**: OAuth 2.0 (Google, GitHub, Kakao)
- **프로필 관리**: 아바타, 선호도, 학습 목표
- **권한 관리**: RBAC 기반 세밀한 권한 제어
- **계정 보안**: 2FA, 비밀번호 정책, 세션 관리

##### 콘텐츠 관리
- **콘텐츠 타입**: 텍스트, 비디오, 오디오, 인터랙티브
- **버전 관리**: 콘텐츠 히스토리 및 롤백
- **메타데이터**: 태그, 카테고리, 난이도, 예상 시간
- **콘텐츠 추천**: AI 기반 개인화 추천

##### 학습 경로
- **커리큘럼 설계**: 8x4 매트릭스 기반 모듈 구성
- **진도 추적**: 실시간 학습 진행률
- **적응형 학습**: 개인 수준에 맞는 난이도 조정
- **학습 분석**: 강점/약점 분석 및 피드백

##### 결제 처리
- **Stripe 통합**: 구독, 일회성 결제
- **결제 수단**: 카드, 계좌이체, 전자지갑
- **구독 관리**: 플랜 변경, 일시정지, 취소
- **인보이스**: 자동 생성 및 발송

#### 데이터 접근 레이어 상세

##### Supabase Client
```javascript
// Supabase 연결 설정
{
  url: process.env.NEXT_PUBLIC_SUPABASE_URL,
  anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
}
```
- **실시간 구독**: PostgreSQL Changes 리스닝
- **Row Level Security**: 데이터 접근 제어
- **Storage**: 파일 업로드 및 CDN 제공
- **Edge Functions**: 서버리스 함수 실행

##### Prisma ORM
```prisma
// 스키마 예시
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  profile   Profile?
  courses   Course[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```
- **타입 안전성**: TypeScript 자동 생성
- **마이그레이션**: 스키마 버전 관리
- **쿼리 최적화**: N+1 문제 자동 해결
- **트랜잭션**: ACID 보장

##### Redis Cache
- **세션 스토어**: 사용자 세션 정보
- **캐싱 전략**: Cache-Aside, Write-Through
- **TTL 관리**: 자동 만료 및 갱신
- **Pub/Sub**: 실시간 이벤트 전파

##### S3 Store
- **CDN 통합**: CloudFront 자동 무효화
- **멀티파트 업로드**: 대용량 파일 처리
- **버킷 정책**: 세밀한 접근 제어
- **라이프사이클**: 자동 아카이빙

## 📚 Knowledge Base System (KB) 상세 아키텍처

```
┌────────────────────────────────────────────────────────────────────┐
│                    iwl-kb-system (포트: 8002)                      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                      API 엔드포인트                           │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │ GET    /api/v1/knowledge/{id}     - 지식 조회            ││ │
│  │  │ POST   /api/v1/knowledge          - 지식 생성            ││ │
│  │  │ PUT    /api/v1/knowledge/{id}     - 지식 수정            ││ │
│  │  │ DELETE /api/v1/knowledge/{id}     - 지식 삭제            ││ │
│  │  │ POST   /api/v1/search/semantic    - 의미 검색            ││ │
│  │  │ POST   /api/v1/search/hybrid      - 하이브리드 검색       ││ │
│  │  │ GET    /api/v1/categories         - 카테고리 목록         ││ │
│  │  │ POST   /api/v1/embeddings/batch   - 배치 임베딩          ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────┘ │
```

### API 엔드포인트 상세 스펙

#### GET /api/v1/knowledge/{id}
```json
// Response
{
  "id": "kb_001",
  "title": "React Hooks 완벽 가이드",
  "content": "...",
  "metadata": {
    "author": "system",
    "category": "frontend",
    "tags": ["react", "hooks", "javascript"],
    "difficulty": "intermediate",
    "readTime": "15 min",
    "version": "2.0",
    "lastModified": "2025-08-28T10:00:00Z"
  },
  "embeddings": {
    "model": "text-embedding-ada-002",
    "vector": [0.023, -0.045, ...],
    "dimension": 1536
  },
  "relations": [
    {"type": "prerequisite", "target": "kb_000"},
    {"type": "related", "target": "kb_002"}
  ]
}
```

#### POST /api/v1/search/semantic
```json
// Request
{
  "query": "React 상태 관리 방법",
  "limit": 10,
  "filters": {
    "category": "frontend",
    "difficulty": ["beginner", "intermediate"]
  },
  "threshold": 0.7
}

// Response
{
  "results": [
    {
      "id": "kb_001",
      "score": 0.92,
      "title": "React Hooks 완벽 가이드",
      "snippet": "useState와 useReducer를 활용한...",
      "highlights": ["useState", "useReducer"]
    }
  ],
  "totalCount": 45,
  "processingTime": "23ms"
}
```

#### POST /api/v1/search/hybrid
```json
// 하이브리드 검색: 키워드 + 시맨틱 + 필터 결합
{
  "keyword": "React",
  "semantic": "상태 관리",
  "filters": {
    "dateRange": {
      "from": "2024-01-01",
      "to": "2025-12-31"
    }
  },
  "weights": {
    "keyword": 0.3,
    "semantic": 0.5,
    "metadata": 0.2
  }
}
```

#### POST /api/v1/embeddings/batch
```json
// 대량 임베딩 생성
{
  "documents": [
    {"id": "doc_1", "text": "내용1"},
    {"id": "doc_2", "text": "내용2"}
  ],
  "model": "text-embedding-ada-002",
  "options": {
    "normalize": true,
    "dimension": 1536
  }
}
```

### 핵심 컴포넌트 상세

#### FastAPI 서버 엔진
```python
# FastAPI 앱 구성
app = FastAPI(
    title="IWL Knowledge Base API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 미들웨어 스택
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
```

#### Pydantic 모델 검증
```python
# 데이터 모델 예시
class KnowledgeBase(BaseModel):
    id: str = Field(..., regex="^kb_[0-9]+$")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    metadata: Dict[str, Any]
    embeddings: Optional[List[float]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "kb_001",
                "title": "샘플 지식",
                "content": "상세 내용..."
            }
        }
```

#### Async IO 비동기 처리
```python
# 비동기 처리 예시
async def process_knowledge(knowledge_id: str):
    # 동시 실행
    results = await asyncio.gather(
        fetch_from_db(knowledge_id),
        generate_embeddings(knowledge_id),
        update_cache(knowledge_id),
        return_exceptions=True
    )
    return combine_results(results)
```

### 벡터 검색 엔진 상세

#### FAISS (Facebook AI Similarity Search)
- **용도**: 대규모 밀집 벡터 검색
- **인덱스 타입**: 
  - IVF (Inverted File): 클러스터링 기반
  - HNSW (Hierarchical Navigable Small World): 그래프 기반
  - LSH (Locality Sensitive Hashing): 해시 기반
- **성능**: 10억개 벡터에서 밀리초 단위 검색
- **GPU 가속**: CUDA 지원으로 10배 속도 향상

#### Annoy (Approximate Nearest Neighbors Oh Yeah)
- **용도**: 빠른 근사 최근접 이웃 검색
- **특징**:
  - 메모리 매핑: 대용량 인덱스 효율적 처리
  - 랜덤 프로젝션 트리: 공간 분할 최적화
  - 정적 인덱스: 읽기 전용 최적화
- **사용 사례**: 추천 시스템, 유사 문서 검색

#### ChromaDB
- **용도**: 임베딩 + 메타데이터 하이브리드 검색
- **특징**:
  - 자동 임베딩 생성
  - 메타데이터 필터링
  - 영속성 지원
  - 다중 컬렉션 관리
- **쿼리 언어**: SQL-like 문법 지원

#### Pinecone (Cloud)
- **용도**: 관리형 벡터 데이터베이스
- **특징**:
  - 실시간 인덱스 업데이트
  - 자동 스케일링
  - 글로벌 복제
  - 99.9% SLA 보장
- **가격**: 100만 벡터당 월 $70

### 데이터 영속성 레이어 상세

#### PostgreSQL 구성
```sql
-- 테이블 구조
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding_id UUID REFERENCES embeddings(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INT DEFAULT 1,
    is_published BOOLEAN DEFAULT false
);

-- 인덱스
CREATE INDEX idx_kb_metadata ON knowledge_base USING GIN(metadata);
CREATE INDEX idx_kb_title_trgm ON knowledge_base USING GIN(title gin_trgm_ops);
CREATE INDEX idx_kb_created_at ON knowledge_base(created_at DESC);

-- Full Text Search
CREATE INDEX idx_kb_fts ON knowledge_base USING GIN(to_tsvector('korean', content));
```

#### Redis 캐싱 전략
```python
# 캐싱 패턴
class CacheStrategy:
    # Cache-Aside 패턴
    async def get_with_cache(self, key: str):
        # 1. 캐시 확인
        cached = await redis.get(f"kb:{key}")
        if cached:
            return json.loads(cached)
        
        # 2. DB 조회
        data = await db.fetch(key)
        
        # 3. 캐시 저장 (TTL 1시간)
        await redis.setex(f"kb:{key}", 3600, json.dumps(data))
        return data
    
    # Write-Through 패턴
    async def update_with_cache(self, key: str, data: dict):
        # 1. DB 업데이트
        await db.update(key, data)
        
        # 2. 캐시 업데이트
        await redis.setex(f"kb:{key}", 3600, json.dumps(data))
        
        # 3. 관련 캐시 무효화
        await redis.delete(f"kb:list:*")
```

### 지식 처리 파이프라인 상세

#### 1. 입력 단계
- **지원 포맷**: TXT, MD, PDF, DOCX, HTML
- **문자 인코딩**: UTF-8 자동 감지 및 변환
- **메타데이터 추출**: 제목, 저자, 날짜 자동 파싱
- **검증**: 스팸 필터링, 중복 검사

#### 2. 전처리 단계
```python
def preprocess(text: str) -> str:
    # 정규화
    text = unicodedata.normalize('NFKC', text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수문자 처리
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    
    # 공백 정규화
    text = ' '.join(text.split())
    
    return text
```

#### 3. 청킹 단계
```python
class ChunkingStrategy:
    # 의미 기반 청킹
    def semantic_chunk(self, text: str, max_tokens: int = 512):
        sentences = text.split('.')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            tokens = len(tokenizer.encode(sentence))
            if current_tokens + tokens > max_tokens:
                chunks.append('.'.join(current_chunk))
                current_chunk = [sentence]
                current_tokens = tokens
            else:
                current_chunk.append(sentence)
                current_tokens += tokens
        
        return chunks
    
    # 슬라이딩 윈도우
    def sliding_window(self, text: str, window: int = 1000, overlap: int = 200):
        chunks = []
        for i in range(0, len(text), window - overlap):
            chunks.append(text[i:i + window])
        return chunks
```

#### 4. 임베딩 단계
```python
async def generate_embeddings(text: str):
    # OpenAI 임베딩
    response = await openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    
    # 정규화
    embedding = np.array(response['data'][0]['embedding'])
    normalized = embedding / np.linalg.norm(embedding)
    
    return normalized.tolist()
```

#### 5. 인덱싱 단계
```python
def index_knowledge(kb_id: str, embedding: List[float]):
    # FAISS 인덱싱
    faiss_index.add(np.array([embedding]))
    
    # Annoy 인덱싱
    annoy_index.add_item(kb_id, embedding)
    
    # ChromaDB 인덱싱
    chromadb.add(
        ids=[kb_id],
        embeddings=[embedding],
        metadatas=[{"source": "kb"}]
    )
```

#### 6. 저장 단계
- **트랜잭션 처리**: All-or-Nothing 보장
- **버전 관리**: 변경 이력 추적
- **백업**: 실시간 복제 및 스냅샷
- **감사 로그**: 모든 변경사항 기록

## 🤖 LLM Service (AI Engine Hub) 상세 아키텍처

```
┌────────────────────────────────────────────────────────────────────┐
│                    ai-engine-hub (포트: 8888)                      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                      API 엔드포인트                           │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │ POST  /api/v1/chat/completions    - 대화 생성            ││ │
│  │  │ POST  /api/v1/embeddings          - 임베딩 생성          ││ │
│  │  │ POST  /api/v1/analyze             - 콘텐츠 분석          ││ │
│  │  │ POST  /api/v1/generate            - 콘텐츠 생성          ││ │
│  │  │ POST  /api/v1/batch/process       - 배치 처리            ││ │
│  │  │ GET   /api/v1/models              - 모델 목록            ││ │
│  │  │ POST  /api/v1/fine-tune           - 파인튜닝 시작        ││ │
│  │  │ GET   /api/v1/usage/stats         - 사용량 통계          ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────┘ │
```

### API 엔드포인트 상세 구현

#### POST /api/v1/chat/completions
```python
@app.post("/api/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    """
    대화형 AI 응답 생성
    
    Parameters:
    - model: 사용할 AI 모델 (gpt-4, claude-3, gemini-pro)
    - messages: 대화 히스토리
    - temperature: 창의성 조절 (0.0 ~ 2.0)
    - max_tokens: 최대 응답 길이
    - stream: 스트리밍 응답 여부
    """
    
    # 모델 선택
    provider = select_provider(request.model)
    
    # 컨텍스트 증강
    enhanced_context = await enhance_context(
        messages=request.messages,
        kb_results=await kb_search(request.messages[-1].content)
    )
    
    # AI 호출
    response = await provider.complete(
        messages=enhanced_context,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    # 후처리
    filtered_response = await content_filter(response)
    
    # 캐싱
    await cache_response(request, filtered_response)
    
    return filtered_response
```

#### POST /api/v1/analyze
```python
@app.post("/api/v1/analyze")
async def analyze_content(request: AnalyzeRequest):
    """
    콘텐츠 분석 (감정, 주제, 요약 등)
    
    Analysis Types:
    - sentiment: 감정 분석 (positive, negative, neutral)
    - topics: 주제 추출
    - summary: 요약 생성
    - entities: 개체명 인식
    - keywords: 핵심 키워드 추출
    """
    
    results = {}
    
    if "sentiment" in request.analysis_types:
        results["sentiment"] = await analyze_sentiment(request.content)
    
    if "topics" in request.analysis_types:
        results["topics"] = await extract_topics(request.content)
    
    if "summary" in request.analysis_types:
        results["summary"] = await generate_summary(
            content=request.content,
            length=request.summary_length
        )
    
    return AnalysisResponse(**results)
```

#### POST /api/v1/generate
```python
@app.post("/api/v1/generate")
async def generate_content(request: GenerateRequest):
    """
    콘텐츠 생성 (교육 자료, 퀴즈, 설명 등)
    
    Content Types:
    - lesson: 교육 자료 생성
    - quiz: 퀴즈 문제 생성
    - explanation: 개념 설명 생성
    - exercise: 연습 문제 생성
    """
    
    # 템플릿 선택
    template = select_template(request.content_type)
    
    # 프롬프트 구성
    prompt = template.format(
        topic=request.topic,
        level=request.difficulty_level,
        style=request.writing_style
    )
    
    # 생성
    content = await generate_with_ai(
        prompt=prompt,
        model=request.model,
        constraints=request.constraints
    )
    
    # 품질 검증
    quality_score = await validate_quality(content)
    
    return GenerateResponse(
        content=content,
        quality_score=quality_score,
        metadata={
            "generated_at": datetime.now(),
            "model": request.model,
            "tokens_used": count_tokens(content)
        }
    )
```

#### POST /api/v1/batch/process
```python
@app.post("/api/v1/batch/process")
async def batch_process(request: BatchRequest):
    """
    대량 작업 처리 (비동기)
    
    Features:
    - 동시 처리: 최대 100개 작업 병렬 실행
    - 진행 상황: WebSocket을 통한 실시간 업데이트
    - 재시도: 실패한 작업 자동 재시도
    - 우선순위: 작업 우선순위 큐
    """
    
    # 작업 큐에 추가
    job_id = str(uuid.uuid4())
    
    for item in request.items:
        await job_queue.enqueue(
            job_id=job_id,
            task=item,
            priority=request.priority
        )
    
    # 백그라운드 처리 시작
    asyncio.create_task(process_batch_job(job_id))
    
    return {
        "job_id": job_id,
        "status": "queued",
        "total_items": len(request.items),
        "estimated_time": estimate_processing_time(request.items)
    }
```

### 보안 & 인증 레이어 상세

#### Bearer Token 인증
```python
class BearerTokenAuth:
    async def authenticate(self, token: str) -> User:
        # 토큰 검증
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
        
        # 사용자 조회
        user = await get_user(payload["sub"])
        
        # 권한 확인
        if not user.is_active:
            raise HTTPException(403, "Account deactivated")
        
        return user
```

#### API Key 검증
```python
async def validate_api_key(api_key: str) -> APIKeyInfo:
    # Redis에서 캐시 확인
    cached = await redis.get(f"api_key:{api_key}")
    if cached:
        return APIKeyInfo(**json.loads(cached))
    
    # DB 조회
    key_info = await db.api_keys.find_one({"key": api_key})
    
    if not key_info:
        raise HTTPException(401, "Invalid API key")
    
    # 만료 확인
    if key_info.expires_at < datetime.now():
        raise HTTPException(401, "API key expired")
    
    # 캐싱 (5분)
    await redis.setex(
        f"api_key:{api_key}",
        300,
        json.dumps(key_info.dict())
    )
    
    return APIKeyInfo(**key_info)
```

#### Rate Limiting 구현
```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(self, key: str, limit: int, window: int):
        """
        Sliding Window Log 알고리즘
        """
        now = time.time()
        pipeline = self.redis.pipeline()
        
        # 현재 윈도우 키
        window_key = f"rate_limit:{key}:{int(now // window)}"
        
        # 이전 윈도우 키
        prev_window_key = f"rate_limit:{key}:{int(now // window) - 1}"
        
        # 카운트 조회
        pipeline.get(prev_window_key)
        pipeline.get(window_key)
        prev_count, current_count = await pipeline.execute()
        
        # 가중 평균 계산
        prev_weight = 1 - ((now % window) / window)
        weighted_count = (
            int(prev_count or 0) * prev_weight +
            int(current_count or 0)
        )
        
        if weighted_count >= limit:
            raise HTTPException(429, "Rate limit exceeded")
        
        # 카운트 증가
        await self.redis.incr(window_key)
        await self.redis.expire(window_key, window * 2)
```

#### Quota 관리
```python
class QuotaManager:
    async def check_quota(self, user_id: str, tokens_required: int):
        """
        사용량 할당량 확인 및 차감
        """
        # 현재 사용량 조회
        usage = await db.usage.find_one({
            "user_id": user_id,
            "period": get_current_period()
        })
        
        # 플랜별 한도 확인
        plan = await get_user_plan(user_id)
        limit = PLAN_LIMITS[plan]
        
        if usage.tokens_used + tokens_required > limit:
            raise HTTPException(
                402,
                f"Quota exceeded. Used: {usage.tokens_used}, Limit: {limit}"
            )
        
        # 사용량 업데이트
        await db.usage.update_one(
            {"_id": usage.id},
            {"$inc": {"tokens_used": tokens_required}}
        )
```

### AI 프로바이더 오케스트레이터 상세

#### 프로바이더 라우터
```python
class ProviderRouter:
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleProvider(),
            "local": LocalProvider()
        }
        
    async def route(self, request: AIRequest) -> AIResponse:
        """
        최적 프로바이더 선택 및 라우팅
        """
        # 모델 → 프로바이더 매핑
        provider_name = self.get_provider_for_model(request.model)
        
        # 프로바이더 상태 확인
        if not await self.is_provider_healthy(provider_name):
            # 폴백 프로바이더 선택
            provider_name = self.select_fallback(provider_name)
        
        # 요청 실행
        provider = self.providers[provider_name]
        
        try:
            response = await provider.execute(request)
            
            # 메트릭 수집
            await self.record_metrics(
                provider=provider_name,
                latency=response.latency,
                tokens=response.tokens_used
            )
            
            return response
            
        except ProviderError as e:
            # 다른 프로바이더로 재시도
            return await self.retry_with_different_provider(request, e)
```

#### OpenAI 프로바이더
```python
class OpenAIProvider:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            max_retries=3,
            timeout=30.0
        )
    
    async def execute(self, request: AIRequest) -> AIResponse:
        """
        OpenAI API 호출
        """
        # 모델 매핑
        model_map = {
            "gpt-4": "gpt-4-turbo-preview",
            "gpt-3.5": "gpt-3.5-turbo-16k",
            "embedding": "text-embedding-ada-002"
        }
        
        if request.type == "completion":
            response = await self.client.chat.completions.create(
                model=model_map[request.model],
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
        
        elif request.type == "embedding":
            response = await self.client.embeddings.create(
                model=model_map["embedding"],
                input=request.input
            )
        
        return self.format_response(response)
```

#### Claude 프로바이더
```python
class AnthropicProvider:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def execute(self, request: AIRequest) -> AIResponse:
        """
        Anthropic Claude API 호출
        """
        # Claude 특화 처리
        if request.model == "claude-3-opus":
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=request.max_tokens,
                messages=self.convert_messages(request.messages),
                system=request.system_prompt
            )
        
        return self.format_response(response)
```

#### Gemini 프로바이더
```python
class GoogleProvider:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def execute(self, request: AIRequest) -> AIResponse:
        """
        Google Gemini API 호출
        """
        # Gemini 특화 기능
        generation_config = genai.GenerationConfig(
            temperature=request.temperature,
            top_p=request.top_p,
            max_output_tokens=request.max_tokens
        )
        
        # 멀티모달 지원
        if request.has_images:
            response = await self.model.generate_content_async(
                [request.text] + request.images,
                generation_config=generation_config
            )
        else:
            response = await self.model.generate_content_async(
                request.text,
                generation_config=generation_config
            )
        
        return self.format_response(response)
```

#### Local Models 프로바이더
```python
class LocalProvider:
    def __init__(self):
        self.models = {
            "llama": LlamaModel(),
            "mistral": MistralModel(),
            "qwen": QwenModel()
        }
    
    async def execute(self, request: AIRequest) -> AIResponse:
        """
        로컬 모델 실행 (Ollama, llama.cpp 등)
        """
        model = self.models[request.model]
        
        # GPU 할당
        device = await self.allocate_gpu()
        
        try:
            # 모델 로딩 (캐시됨)
            await model.load(device)
            
            # 추론 실행
            response = await model.generate(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            return response
            
        finally:
            # GPU 해제
            await self.release_gpu(device)
```

### 고급 기능 레이어 상세

#### 프롬프트 템플릿 관리
```python
class PromptTemplateManager:
    templates = {
        "education": {
            "lesson": """
            주제: {topic}
            난이도: {level}
            대상: {audience}
            
            위 정보를 바탕으로 교육 자료를 작성해주세요:
            1. 개념 설명 (쉬운 비유 포함)
            2. 핵심 포인트 3-5개
            3. 실습 예제
            4. 추가 학습 자료
            """,
            
            "quiz": """
            주제: {topic}
            문제 수: {count}
            난이도: {difficulty}
            
            객관식 문제를 생성해주세요:
            - 4지선다형
            - 정답과 해설 포함
            - 난이도별 분포
            """
        }
    }
    
    def get_template(self, category: str, type: str) -> str:
        return self.templates[category][type]
    
    def render(self, template: str, **kwargs) -> str:
        return template.format(**kwargs)
```

#### 컨텍스트 관리
```python
class ContextManager:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.contexts = {}  # 세션별 컨텍스트 저장
    
    async def build_context(self, session_id: str, new_message: str):
        """
        토큰 제한을 고려한 컨텍스트 구성
        """
        # 기존 컨텍스트 조회
        context = self.contexts.get(session_id, [])
        
        # KB에서 관련 정보 검색
        kb_results = await search_knowledge_base(new_message)
        
        # 컨텍스트 구성
        enhanced_context = [
            {"role": "system", "content": "당신은 교육 전문 AI입니다."},
            {"role": "system", "content": f"관련 지식: {kb_results}"}
        ]
        
        # 대화 히스토리 추가 (토큰 제한 고려)
        total_tokens = count_tokens(enhanced_context)
        
        for message in reversed(context):
            message_tokens = count_tokens([message])
            if total_tokens + message_tokens > self.max_tokens:
                break
            enhanced_context.append(message)
            total_tokens += message_tokens
        
        # 새 메시지 추가
        enhanced_context.append({"role": "user", "content": new_message})
        
        return enhanced_context
```

#### 메모리 관리
```python
class MemoryManager:
    """
    장기/단기 메모리 관리
    """
    def __init__(self):
        self.short_term = {}  # 세션 메모리
        self.long_term = {}   # 영구 메모리
    
    async def save_interaction(self, user_id: str, interaction: dict):
        """
        상호작용 저장
        """
        # 단기 메모리 (Redis)
        await redis.lpush(
            f"memory:short:{user_id}",
            json.dumps(interaction)
        )
        await redis.ltrim(f"memory:short:{user_id}", 0, 100)  # 최근 100개
        
        # 중요도 평가
        importance = await evaluate_importance(interaction)
        
        # 장기 메모리 저장 (중요도 높은 경우)
        if importance > 0.7:
            await db.long_term_memory.insert_one({
                "user_id": user_id,
                "interaction": interaction,
                "importance": importance,
                "timestamp": datetime.now()
            })
    
    async def recall(self, user_id: str, query: str):
        """
        관련 기억 검색
        """
        # 단기 메모리 검색
        recent = await redis.lrange(f"memory:short:{user_id}", 0, 10)
        
        # 장기 메모리 검색 (시맨틱 검색)
        relevant = await db.long_term_memory.find({
            "$text": {"$search": query},
            "user_id": user_id
        }).limit(5)
        
        return {
            "recent": [json.loads(r) for r in recent],
            "relevant": list(relevant)
        }
```

#### 스트리밍 처리
```python
class StreamingHandler:
    async def stream_response(self, generator, client_id: str):
        """
        Server-Sent Events (SSE) 스트리밍
        """
        async def event_generator():
            try:
                async for chunk in generator:
                    # 청크 포맷팅
                    event = {
                        "id": str(uuid.uuid4()),
                        "event": "message",
                        "data": chunk.content
                    }
                    
                    # SSE 포맷
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    # 클라이언트 연결 확인
                    if not await self.is_client_connected(client_id):
                        break
                
                # 종료 이벤트
                yield "event: done\ndata: {}\n\n"
                
            except Exception as e:
                # 에러 이벤트
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
```

#### 배치 처리
```python
class BatchProcessor:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue = asyncio.Queue()
    
    async def process_batch(self, items: List[dict]):
        """
        대량 작업 병렬 처리
        """
        # 작업 큐에 추가
        for item in items:
            await self.queue.put(item)
        
        # 워커 생성
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(min(len(items), self.max_concurrent))
        ]
        
        # 완료 대기
        await self.queue.join()
        
        # 워커 종료
        for worker in workers:
            worker.cancel()
```

#### 파인튜닝 관리
```python
class FineTuningManager:
    async def create_fine_tuning_job(self, dataset_id: str, base_model: str):
        """
        파인튜닝 작업 생성
        """
        # 데이터셋 검증
        dataset = await validate_dataset(dataset_id)
        
        # 파인튜닝 작업 생성
        job = await openai.fine_tuning.jobs.create(
            training_file=dataset.file_id,
            model=base_model,
            hyperparameters={
                "n_epochs": 3,
                "batch_size": 4,
                "learning_rate_multiplier": 0.1
            }
        )
        
        # DB에 작업 정보 저장
        await db.fine_tuning_jobs.insert_one({
            "job_id": job.id,
            "dataset_id": dataset_id,
            "base_model": base_model,
            "status": "created",
            "created_at": datetime.now()
        })
        
        # 모니터링 시작
        asyncio.create_task(self.monitor_job(job.id))
        
        return job
```

### 캐싱 & 최적화 레이어 상세

#### Redis 캐싱 구현
```python
class CacheLayer:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 3600  # 1시간
    
    def cache_key(self, request: dict) -> str:
        """
        요청 기반 캐시 키 생성
        """
        # 정규화
        normalized = {
            "model": request.get("model"),
            "messages": request.get("messages", [])[-1],  # 마지막 메시지만
            "temperature": round(request.get("temperature", 1.0), 1)
        }
        
        # 해시 생성
        return f"llm:cache:{hashlib.md5(json.dumps(normalized).encode()).hexdigest()}"
    
    async def get_cached_response(self, request: dict):
        """
        캐시된 응답 조회
        """
        key = self.cache_key(request)
        cached = await self.redis.get(key)
        
        if cached:
            # 캐시 히트 메트릭
            await self.redis.incr("cache:hits")
            return json.loads(cached)
        
        # 캐시 미스 메트릭
        await self.redis.incr("cache:misses")
        return None
    
    async def cache_response(self, request: dict, response: dict):
        """
        응답 캐싱
        """
        key = self.cache_key(request)
        
        # 캐시 가능 여부 확인
        if self.is_cacheable(request, response):
            await self.redis.setex(
                key,
                self.get_ttl(request),
                json.dumps(response)
            )
```

#### Response Cache 최적화
```python
class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.access_times = {}
        self.max_size = 1000
    
    def evict_lru(self):
        """
        LRU (Least Recently Used) 제거
        """
        if len(self.cache) >= self.max_size:
            oldest = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest]
            del self.access_times[oldest]
    
    async def get(self, key: str):
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    async def set(self, key: str, value: any):
        self.evict_lru()
        self.cache[key] = value
        self.access_times[key] = time.time()
```

## 🔄 KB ↔ LLM 서비스 통합 플로우 상세

### 통합 워크플로우 구현
```python
class IntegrationWorkflow:
    def __init__(self):
        self.kb_service = KBService()
        self.llm_service = LLMService()
        self.cache = CacheLayer()
    
    async def process_query(self, user_query: str, user_id: str):
        """
        사용자 질문 처리 전체 플로우
        """
        # 1. 캐시 확인
        cached = await self.cache.get_cached_response(user_query)
        if cached:
            return cached
        
        # 2. KB 검색
        kb_context = await self.kb_service.search(
            query=user_query,
            limit=5,
            threshold=0.7
        )
        
        # 3. 사용자 히스토리
        history = await self.get_user_history(user_id)
        
        # 4. 컨텍스트 구성
        enhanced_prompt = self.build_enhanced_prompt(
            query=user_query,
            context=kb_context,
            history=history
        )
        
        # 5. LLM 호출
        llm_response = await self.llm_service.generate(
            prompt=enhanced_prompt,
            model="gpt-4",
            temperature=0.7
        )
        
        # 6. 응답 후처리
        processed_response = await self.post_process(
            response=llm_response,
            query=user_query
        )
        
        # 7. KB 업데이트
        if self.should_update_kb(processed_response):
            await self.kb_service.add_knowledge(
                content=processed_response.content,
                metadata={
                    "source": "llm_generated",
                    "query": user_query,
                    "confidence": processed_response.confidence
                }
            )
        
        # 8. 캐싱
        await self.cache.cache_response(user_query, processed_response)
        
        # 9. 메트릭 수집
        await self.record_metrics(
            query=user_query,
            kb_hits=len(kb_context),
            llm_tokens=llm_response.tokens_used,
            total_latency=llm_response.latency
        )
        
        return processed_response
```

### KB → LLM 데이터 흐름 구현

#### Knowledge Retrieval
```python
class KnowledgeRetriever:
    async def retrieve(self, query: str, top_k: int = 5):
        """
        다단계 지식 검색
        """
        # 1단계: 빠른 키워드 매칭
        keyword_results = await self.keyword_search(query, limit=top_k * 2)
        
        # 2단계: 시맨틱 검색
        semantic_results = await self.semantic_search(query, limit=top_k * 2)
        
        # 3단계: 하이브리드 스코어링
        combined_results = self.combine_results(
            keyword_results,
            semantic_results,
            weights={"keyword": 0.3, "semantic": 0.7}
        )
        
        # 4단계: 리랭킹
        reranked = await self.rerank(query, combined_results)
        
        # 5단계: 컨텍스트 확장
        expanded = await self.expand_context(reranked[:top_k])
        
        return expanded
    
    async def semantic_search(self, query: str, limit: int):
        """
        벡터 유사도 기반 검색
        """
        # 쿼리 임베딩 생성
        query_embedding = await generate_embedding(query)
        
        # FAISS 검색
        distances, indices = self.faiss_index.search(
            np.array([query_embedding]),
            limit
        )
        
        # 결과 포맷팅
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            doc = await self.get_document(idx)
            results.append({
                "id": doc.id,
                "content": doc.content,
                "score": 1 / (1 + dist),  # 거리를 유사도로 변환
                "metadata": doc.metadata
            })
        
        return results
```

#### Context Enhancement
```python
class ContextEnhancer:
    def enhance(self, kb_results: List[dict], user_query: str):
        """
        검색 결과를 LLM용 컨텍스트로 변환
        """
        # 관련성 점수별 정렬
        sorted_results = sorted(
            kb_results,
            key=lambda x: x["score"],
            reverse=True
        )
        
        # 컨텍스트 구성
        context_parts = []
        
        for result in sorted_results:
            # 메타데이터 포함
            context_parts.append(f"""
            [출처: {result['metadata'].get('source', 'Unknown')}]
            [관련도: {result['score']:.2f}]
            내용: {result['content'][:500]}...
            """)
        
        # 시간적 관련성 추가
        recent_docs = self.get_recent_documents(hours=24)
        if recent_docs:
            context_parts.append("\n최근 업데이트된 정보:")
            context_parts.extend([doc.summary for doc in recent_docs[:3]])
        
        return "\n---\n".join(context_parts)
```

### LLM → KB 피드백 루프 구현

#### Knowledge Update
```python
class KnowledgeUpdater:
    async def update_from_llm(self, llm_response: dict, original_query: str):
        """
        LLM 응답을 KB에 저장
        """
        # 품질 평가
        quality_score = await self.evaluate_quality(llm_response)
        
        if quality_score > 0.8:  # 고품질 응답만 저장
            # 임베딩 생성
            embedding = await generate_embedding(llm_response["content"])
            
            # 자동 카테고리 분류
            category = await self.classify_category(llm_response["content"])
            
            # KB 저장
            knowledge_id = await self.kb_service.create({
                "title": self.generate_title(original_query),
                "content": llm_response["content"],
                "embedding": embedding,
                "metadata": {
                    "source": "llm_generated",
                    "model": llm_response["model"],
                    "quality_score": quality_score,
                    "category": category,
                    "tags": await self.extract_tags(llm_response["content"]),
                    "created_at": datetime.now()
                }
            })
            
            # 관계 설정
            await self.create_relations(knowledge_id, original_query)
            
            return knowledge_id
        
        return None
```

#### Learning Loop
```python
class LearningLoop:
    async def learn_from_feedback(self, interaction_id: str, feedback: dict):
        """
        사용자 피드백 기반 학습
        """
        # 상호작용 데이터 조회
        interaction = await self.get_interaction(interaction_id)
        
        # 피드백 분석
        if feedback["rating"] < 3:  # 부정적 피드백
            # 실패 원인 분석
            failure_reason = await self.analyze_failure(
                query=interaction["query"],
                response=interaction["response"],
                feedback=feedback
            )
            
            # KB 가중치 조정
            if failure_reason == "incorrect_context":
                await self.adjust_kb_weights(
                    used_documents=interaction["kb_documents"],
                    adjustment=-0.1
                )
            
            # 프롬프트 템플릿 개선
            if failure_reason == "poor_generation":
                await self.update_prompt_template(
                    template_id=interaction["template_id"],
                    feedback=feedback
                )
        
        else:  # 긍정적 피드백
            # 성공 패턴 강화
            await self.reinforce_success_pattern(
                documents=interaction["kb_documents"],
                template=interaction["template_id"]
            )
        
        # 메트릭 업데이트
        await self.update_learning_metrics(feedback)
```

### 실시간 동기화 구현

#### WebSocket 연결 관리
```python
class RealtimeSyncManager:
    def __init__(self):
        self.connections = {}
        self.subscriptions = defaultdict(set)
    
    async def handle_connection(self, websocket: WebSocket, client_id: str):
        """
        WebSocket 연결 처리
        """
        await websocket.accept()
        self.connections[client_id] = websocket
        
        try:
            while True:
                # 메시지 수신
                data = await websocket.receive_json()
                
                if data["type"] == "subscribe":
                    # 구독 추가
                    self.subscriptions[data["channel"]].add(client_id)
                    
                elif data["type"] == "update":
                    # 업데이트 전파
                    await self.broadcast_update(
                        channel=data["channel"],
                        payload=data["payload"]
                    )
                
        except WebSocketDisconnect:
            # 연결 종료 처리
            del self.connections[client_id]
            for channel in self.subscriptions:
                self.subscriptions[channel].discard(client_id)
    
    async def broadcast_update(self, channel: str, payload: dict):
        """
        구독자에게 업데이트 전파
        """
        for client_id in self.subscriptions[channel]:
            if client_id in self.connections:
                await self.connections[client_id].send_json({
                    "channel": channel,
                    "payload": payload,
                    "timestamp": datetime.now().isoformat()
                })
```

#### 이벤트 기반 업데이트
```python
class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)
    
    def on(self, event: str, handler: callable):
        """
        이벤트 핸들러 등록
        """
        self.handlers[event].append(handler)
    
    async def emit(self, event: str, data: dict):
        """
        이벤트 발생
        """
        for handler in self.handlers[event]:
            asyncio.create_task(handler(data))
    
    # 사용 예시
    async def setup_event_handlers(self):
        # KB 업데이트 시
        self.on("kb.updated", self.invalidate_cache)
        self.on("kb.updated", self.notify_llm_service)
        
        # LLM 응답 생성 시
        self.on("llm.generated", self.update_kb)
        self.on("llm.generated", self.record_metrics)
        
        # 캐시 무효화 시
        self.on("cache.invalidated", self.refresh_indexes)
```

## 📊 시스템 메트릭 & 모니터링 상세

### 메트릭 수집 시스템
```python
class MetricsCollector:
    def __init__(self):
        self.prometheus_client = PrometheusClient()
        self.metrics = {
            "kb_search_latency": Histogram("kb_search_latency_seconds"),
            "llm_response_time": Histogram("llm_response_time_seconds"),
            "cache_hit_rate": Gauge("cache_hit_rate"),
            "error_rate": Counter("error_total"),
            "active_connections": Gauge("active_connections")
        }
    
    async def record_kb_search(self, latency: float, hits: int):
        """
        KB 검색 메트릭 기록
        """
        self.metrics["kb_search_latency"].observe(latency)
        
        # 상세 메트릭
        await self.prometheus_client.push({
            "kb_search_hits": hits,
            "kb_search_latency": latency,
            "timestamp": time.time()
        })
    
    async def calculate_sla_metrics(self):
        """
        SLA 메트릭 계산
        """
        return {
            "uptime": await self.calculate_uptime(),
            "p50_latency": await self.get_percentile(50),
            "p95_latency": await self.get_percentile(95),
            "p99_latency": await self.get_percentile(99),
            "error_rate": await self.get_error_rate(),
            "throughput": await self.get_throughput()
        }
```

### 알림 시스템
```python
class AlertingSystem:
    def __init__(self):
        self.rules = [
            {
                "name": "high_latency",
                "condition": lambda m: m["p95_latency"] > 1.0,
                "severity": "warning",
                "message": "P95 latency exceeds 1 second"
            },
            {
                "name": "high_error_rate",
                "condition": lambda m: m["error_rate"] > 0.01,
                "severity": "critical",
                "message": "Error rate exceeds 1%"
            }
        ]
    
    async def check_alerts(self):
        """
        알림 규칙 확인
        """
        metrics = await self.get_current_metrics()
        
        for rule in self.rules:
            if rule["condition"](metrics):
                await self.send_alert(
                    rule["name"],
                    rule["severity"],
                    rule["message"]
                )
    
    async def send_alert(self, name: str, severity: str, message: str):
        """
        알림 발송
        """
        # Slack
        if severity == "critical":
            await send_slack_message(
                channel="#alerts-critical",
                text=f"🚨 {message}"
            )
        
        # Email
        await send_email(
            to=["ops@iwl.com"],
            subject=f"[{severity.upper()}] {name}",
            body=message
        )
        
        # PagerDuty
        if severity == "critical":
            await trigger_pagerduty(name, message)
```

## 🚀 배포 아키텍처 상세

### Docker 구성
```dockerfile
# Main Platform Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

### Kubernetes 배포
```yaml
# kb-system-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kb-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kb-system
  template:
    metadata:
      labels:
        app: kb-system
    spec:
      containers:
      - name: kb-system
        image: iwl/kb-system:latest
        ports:
        - containerPort: 8002
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: POSTGRES_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: postgres-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: cache-secret
              key: redis-url
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Auto-scaling 구성
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kb-system-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kb-system
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

## 🔐 보안 아키텍처 상세

### 네트워크 보안
```yaml
# VPC 구성
VPC:
  CIDR: 10.0.0.0/16
  Subnets:
    Public:
      - 10.0.1.0/24  # ALB
      - 10.0.2.0/24  # NAT Gateway
    Private:
      - 10.0.10.0/24  # Application
      - 10.0.11.0/24  # Database
    
Security Groups:
  ALB:
    Ingress:
      - Protocol: TCP
        Port: 443
        Source: 0.0.0.0/0
    Egress:
      - Protocol: TCP
        Port: 3000
        Destination: Application-SG
  
  Application:
    Ingress:
      - Protocol: TCP
        Port: 3000
        Source: ALB-SG
    Egress:
      - Protocol: TCP
        Port: 5432
        Destination: Database-SG
      - Protocol: TCP
        Port: 6379
        Destination: Cache-SG
```

### 인증/인가 구현
```python
class SecurityMiddleware:
    async def authenticate(self, request: Request):
        """
        다층 인증
        """
        # JWT 토큰 검증
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        try:
            # 토큰 디코딩
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            
            # 토큰 블랙리스트 확인
            if await redis.get(f"blacklist:{token}"):
                raise HTTPException(401, "Token revoked")
            
            # 사용자 조회
            user = await get_user(payload["sub"])
            
            # MFA 확인 (필요시)
            if user.mfa_enabled and not payload.get("mfa_verified"):
                raise HTTPException(401, "MFA required")
            
            request.state.user = user
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")
    
    async def authorize(self, request: Request, resource: str, action: str):
        """
        RBAC 기반 인가
        """
        user = request.state.user
        
        # 권한 확인
        permissions = await get_user_permissions(user.id)
        
        required_permission = f"{resource}:{action}"
        
        if required_permission not in permissions:
            raise HTTPException(403, f"Permission denied: {required_permission}")
```

### 암호화 구현
```python
class EncryptionService:
    def __init__(self):
        self.kms_client = boto3.client('kms')
        self.data_key_cache = {}
    
    async def encrypt_data(self, data: bytes, context: dict = None):
        """
        데이터 암호화 (Envelope Encryption)
        """
        # 데이터 키 생성
        response = self.kms_client.generate_data_key(
            KeyId=KMS_KEY_ID,
            KeySpec='AES_256',
            EncryptionContext=context or {}
        )
        
        # AES-256으로 데이터 암호화
        cipher = Cipher(
            algorithms.AES(response['Plaintext']),
            modes.GCM(os.urandom(12)),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'encrypted_data_key': base64.b64encode(response['CiphertextBlob']).decode(),
            'tag': base64.b64encode(encryptor.tag).decode()
        }
```

## 📈 확장 계획 상세

### Phase 1: MVP (현재)
- **아키텍처**: 모놀리식 → 마이크로서비스 전환 중
- **인프라**: 단일 리전, 단일 AZ
- **성능**: 100 RPS, P95 < 500ms
- **가용성**: 99.5% SLA

### Phase 2: 스케일링 (3개월)
- **아키텍처**: 완전한 마이크로서비스
- **인프라**: Multi-AZ, 읽기 복제본
- **성능**: 1,000 RPS, P95 < 200ms
- **가용성**: 99.9% SLA
- **기능**: A/B 테스팅, Feature Flags

### Phase 3: 엔터프라이즈 (6개월)
- **아키텍처**: Event-Driven, CQRS
- **인프라**: Multi-Region, Global CDN
- **성능**: 10,000 RPS, P95 < 100ms
- **가용성**: 99.99% SLA
- **기능**: ML 기반 자동 스케일링, Chaos Engineering

## 🎓 결론

IWL Orchestra는 현대적인 마이크로서비스 아키텍처와 AI 기술을 결합한 차세대 교육 플랫폼입니다. KB System과 LLM Service의 긴밀한 통합을 통해 개인화된 학습 경험을 제공하며, 확장 가능하고 안정적인 인프라를 통해 엔터프라이즈급 서비스를 제공합니다.