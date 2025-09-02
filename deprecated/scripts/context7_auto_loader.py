#!/usr/bin/env python3
"""
Context7 Auto Loader - package.json 기반 자동 문서 로딩 시스템
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from mcp_executor import MCPExecutor
from node_system import NodeType, NodeState

class Context7AutoLoader:
    """Context7 자동 문서 로더"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mcp_executor = MCPExecutor()
        self.docs_cache = {}  # 문서 캐시
        self.cache_ttl = timedelta(hours=1)  # 1시간 캐시
        
        # 주요 npm 패키지와 Context7 라이브러리 ID 매핑
        self.library_mapping = {
            "react": "react",
            "next": "next.js",
            "@next/font": "next.js",
            "vue": "vue",
            "nuxt": "nuxt",
            "svelte": "svelte",
            "sveltekit": "@sveltejs/kit",
            "express": "express",
            "fastify": "fastify",
            "nestjs": "@nestjs/core",
            "@nestjs/common": "@nestjs/core",
            "axios": "axios",
            "prisma": "@prisma/client",
            "@prisma/client": "@prisma/client",
            "tailwindcss": "tailwindcss",
            "typescript": "typescript",
            "vite": "vite",
            "vitest": "vitest",
            "jest": "jest",
            "@testing-library/react": "@testing-library/react",
            "zod": "zod",
            "react-hook-form": "react-hook-form",
            "@tanstack/react-query": "@tanstack/react-query",
            "zustand": "zustand",
            "redux": "redux",
            "@reduxjs/toolkit": "@reduxjs/toolkit",
        }
    
    def find_package_json(self, start_path: str = ".") -> Optional[Path]:
        """package.json 파일 찾기"""
        current = Path(start_path).resolve()
        
        # 현재 디렉토리부터 상위로 탐색
        while current != current.parent:
            package_json = current / "package.json"
            if package_json.exists():
                self.logger.info(f"📦 package.json 발견: {package_json}")
                return package_json
            current = current.parent
        
        self.logger.warning("package.json을 찾을 수 없습니다")
        return None
    
    def parse_dependencies(self, package_json_path: Path) -> Dict[str, str]:
        """package.json에서 의존성 파싱"""
        try:
            with open(package_json_path, 'r') as f:
                data = json.load(f)
            
            deps = {}
            
            # dependencies와 devDependencies 모두 확인
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    deps.update(data[dep_type])
            
            self.logger.info(f"📋 발견된 의존성: {len(deps)}개")
            return deps
            
        except Exception as e:
            self.logger.error(f"package.json 파싱 실패: {e}")
            return {}
    
    def get_context7_libraries(self, dependencies: Dict[str, str]) -> List[str]:
        """의존성에서 Context7 지원 라이브러리 추출"""
        context7_libs = []
        
        for dep_name, version in dependencies.items():
            # 기본 패키지명으로 매칭
            base_name = dep_name.split('/')[0] if '/' in dep_name else dep_name
            
            if dep_name in self.library_mapping:
                lib_id = self.library_mapping[dep_name]
                context7_libs.append({
                    "package": dep_name,
                    "version": version,
                    "context7_id": lib_id
                })
                self.logger.info(f"✅ Context7 지원: {dep_name} → {lib_id}")
            elif base_name in self.library_mapping:
                lib_id = self.library_mapping[base_name]
                context7_libs.append({
                    "package": dep_name,
                    "version": version,
                    "context7_id": lib_id
                })
                self.logger.info(f"✅ Context7 지원: {dep_name} → {lib_id}")
        
        return context7_libs
    
    def load_docs_for_library(self, library_info: Dict) -> Optional[Dict]:
        """특정 라이브러리의 문서 로드"""
        lib_id = library_info["context7_id"]
        cache_key = f"{lib_id}_{library_info['version']}"
        
        # 캐시 확인
        if cache_key in self.docs_cache:
            cached = self.docs_cache[cache_key]
            if datetime.now() - cached["timestamp"] < self.cache_ttl:
                self.logger.info(f"📚 캐시에서 로드: {lib_id}")
                return cached["docs"]
        
        # Context7에서 문서 가져오기
        self.logger.info(f"🔄 Context7에서 {lib_id} 문서 로드 중...")
        
        # 1. 라이브러리 ID 해석
        resolve_node = NodeState(
            id=f"resolve_{lib_id}",
            type=NodeType.MCP_CONTEXT7_RESOLVE,
            input_data={"library_name": library_info["context7_id"]}
        )
        
        resolve_result = self.mcp_executor.execute_mcp_node(resolve_node)
        
        if not resolve_result.get("success"):
            self.logger.error(f"라이브러리 ID 해석 실패: {lib_id}")
            return None
        
        # 2. 문서 조회
        # resolve 결과에서 실제 라이브러리 ID 추출
        libraries = resolve_result.get("libraries", {})
        if not libraries:
            self.logger.warning(f"라이브러리를 찾을 수 없음: {lib_id}")
            return None
        
        # 첫 번째 매칭된 라이브러리 사용
        actual_lib_id = None
        
        # 다양한 응답 형식 처리
        if isinstance(libraries, dict):
            # result 안에 있는 경우
            if 'result' in libraries:
                lib_result = libraries['result']
                if isinstance(lib_result, list) and len(lib_result) > 0:
                    actual_lib_id = lib_result[0] if isinstance(lib_result[0], str) else lib_result[0].get('id')
            # 직접 libraries 안에 있는 경우
            elif 'libraries' in libraries:
                lib_list = libraries['libraries']
                if isinstance(lib_list, list) and len(lib_list) > 0:
                    actual_lib_id = lib_list[0] if isinstance(lib_list[0], str) else lib_list[0].get('id')
        elif isinstance(libraries, list) and len(libraries) > 0:
            actual_lib_id = libraries[0] if isinstance(libraries[0], str) else libraries[0].get('id')
        
        # 라이브러리 ID가 없으면 기본값 사용
        if not actual_lib_id:
            self.logger.warning(f"Context7 응답 파싱 실패, 기본 ID 사용: {lib_id}")
            actual_lib_id = f"/{lib_id.replace('.', '/')}"  # 기본 형식으로 변환
        
        docs_node = NodeState(
            id=f"docs_{lib_id}",
            type=NodeType.MCP_CONTEXT7_DOCS,
            input_data={
                "library_id": actual_lib_id,
                "topic": "overview api hooks components",  # 주요 토픽
                "tokens": 10000  # 충분한 토큰
            }
        )
        
        docs_result = self.mcp_executor.execute_mcp_node(docs_node)
        
        if docs_result.get("success"):
            # 캐시에 저장
            self.docs_cache[cache_key] = {
                "timestamp": datetime.now(),
                "docs": docs_result.get("documentation", {})
            }
            self.logger.info(f"✅ {lib_id} 문서 로드 완료")
            return docs_result.get("documentation", {})
        
        return None
    
    def auto_load_all_docs(self, project_path: str = ".") -> Dict[str, Any]:
        """프로젝트의 모든 의존성 문서 자동 로드"""
        results = {
            "loaded": [],
            "failed": [],
            "total_libraries": 0
        }
        
        # 1. package.json 찾기
        package_json = self.find_package_json(project_path)
        if not package_json:
            return results
        
        # 2. 의존성 파싱
        dependencies = self.parse_dependencies(package_json)
        
        # 3. Context7 지원 라이브러리 추출
        context7_libs = self.get_context7_libraries(dependencies)
        results["total_libraries"] = len(context7_libs)
        
        # 4. 각 라이브러리 문서 로드
        for lib_info in context7_libs:
            docs = self.load_docs_for_library(lib_info)
            if docs:
                results["loaded"].append({
                    "library": lib_info["package"],
                    "version": lib_info["version"],
                    "docs_loaded": True
                })
            else:
                results["failed"].append(lib_info["package"])
        
        # 5. 결과 요약
        self.logger.info(f"""
📊 Context7 문서 로드 완료:
- 성공: {len(results['loaded'])}개
- 실패: {len(results['failed'])}개
- 전체: {results['total_libraries']}개
        """)
        
        return results
    
    def get_docs_for_code_generation(self, library_name: str) -> Optional[Dict]:
        """코드 생성시 특정 라이브러리 문서 가져오기"""
        # 캐시에서 먼저 확인
        for cache_key, cached in self.docs_cache.items():
            if library_name in cache_key:
                if datetime.now() - cached["timestamp"] < self.cache_ttl:
                    return cached["docs"]
        
        # 없으면 새로 로드
        lib_info = {
            "context7_id": self.library_mapping.get(library_name, library_name),
            "version": "latest"
        }
        return self.load_docs_for_library(lib_info)
    
    def suggest_api_usage(self, library: str, api_name: str) -> Optional[str]:
        """특정 API 사용법 제안"""
        docs = self.get_docs_for_code_generation(library)
        if not docs:
            return None
        
        # 문서에서 API 검색 (간단한 구현)
        docs_text = str(docs)
        if api_name in docs_text:
            # API 주변 컨텍스트 추출
            start = docs_text.find(api_name)
            end = min(start + 500, len(docs_text))
            context = docs_text[start:end]
            return f"📖 {library} - {api_name} 사용법:\n{context}"
        
        return None
    
    def check_breaking_changes(self, old_version: str, new_version: str, library: str) -> List[str]:
        """버전 간 Breaking Changes 확인"""
        warnings = []
        
        # 주요 라이브러리별 알려진 Breaking Changes (간단한 예시)
        breaking_changes = {
            "react": {
                "17": ["useEffect cleanup 타이밍"],
                "18": ["자동 배치", "Suspense 변경", "StrictMode 동작"]
            },
            "next.js": {
                "13": ["App Router 도입", "Image 컴포넌트 변경"],
                "14": ["Server Actions", "Partial Prerendering"]
            }
        }
        
        if library in breaking_changes:
            major_old = old_version.split('.')[0].replace('^', '').replace('~', '')
            major_new = new_version.split('.')[0].replace('^', '').replace('~', '')
            
            if major_old != major_new:
                changes = breaking_changes.get(library, {}).get(major_new, [])
                for change in changes:
                    warnings.append(f"⚠️ {library} {major_old} → {major_new}: {change}")
        
        return warnings


# 테스트
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    loader = Context7AutoLoader()
    
    print("🚀 Context7 자동 문서 로더 테스트")
    print("=" * 50)
    
    # 1. 자동 문서 로드 테스트
    results = loader.auto_load_all_docs("/Users/m4_macbook/Projects/personal-journal-hub")
    
    # 2. 특정 라이브러리 문서 가져오기
    react_docs = loader.get_docs_for_code_generation("react")
    if react_docs:
        print("\n✅ React 문서 로드 성공")
    
    # 3. API 사용법 제안
    usage = loader.suggest_api_usage("react", "useState")
    if usage:
        print(usage[:200] + "...")
    
    # 4. Breaking Changes 확인
    warnings = loader.check_breaking_changes("^17.0.0", "^18.0.0", "react")
    for warning in warnings:
        print(warning)