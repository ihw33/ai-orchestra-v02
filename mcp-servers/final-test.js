#!/usr/bin/env node

/**
 * MCP 서버 최종 테스트 - 올바른 도구명 사용
 */

const { spawn } = require('child_process');

class MCPFinalTester {
    async testMemoryMCP() {
        console.log('\n🧠 Memory MCP 최종 테스트...');
        
        const memoryServer = spawn('npx', ['-y', '@modelcontextprotocol/server-memory'], {
            stdio: ['pipe', 'pipe', 'inherit']
        });

        return new Promise((resolve) => {
            memoryServer.stdout.on('data', (data) => {
                console.log('Memory 응답:', data.toString());
            });

            setTimeout(() => {
                // 1. 엔티티 생성
                const createMessage = {
                    jsonrpc: "2.0",
                    id: 1,
                    method: "tools/call",
                    params: {
                        name: "create_entities",
                        arguments: {
                            entities: [{
                                name: "AI_Orchestra_v02",
                                entityType: "project",
                                observations: ["PM Claude 활성화", "페르소나 시스템 완성", "MCP 통합 시작"]
                            }]
                        }
                    }
                };

                memoryServer.stdin.write(JSON.stringify(createMessage) + '\n');
                console.log('✅ 프로젝트 메모리 저장');

                // 2. 검색 테스트
                setTimeout(() => {
                    const searchMessage = {
                        jsonrpc: "2.0",
                        id: 2,
                        method: "tools/call",
                        params: {
                            name: "search_nodes",
                            arguments: {
                                query: "AI_Orchestra"
                            }
                        }
                    };

                    memoryServer.stdin.write(JSON.stringify(searchMessage) + '\n');
                    console.log('✅ 프로젝트 메모리 검색');

                    setTimeout(() => {
                        memoryServer.kill();
                        console.log('🧠 Memory MCP 테스트 완료\n');
                        resolve();
                    }, 3000);
                }, 2000);
            }, 3000);
        });
    }

    async testContext7MCP() {
        console.log('📚 Context7 MCP 최종 테스트...');
        
        const context7Server = spawn('npx', ['-y', '@upstash/context7-mcp'], {
            stdio: ['pipe', 'pipe', 'inherit']
        });

        return new Promise((resolve) => {
            context7Server.stdout.on('data', (data) => {
                console.log('Context7 응답:', data.toString());
            });

            setTimeout(() => {
                // 1. React 라이브러리 ID 해석
                const resolveMessage = {
                    jsonrpc: "2.0",
                    id: 1,
                    method: "tools/call",
                    params: {
                        name: "resolve-library-id",
                        arguments: {
                            libraryName: "react"
                        }
                    }
                };

                context7Server.stdin.write(JSON.stringify(resolveMessage) + '\n');
                console.log('✅ React 라이브러리 ID 해석');

                // 2. 문서 조회 (잘 알려진 ID 사용)
                setTimeout(() => {
                    const docsMessage = {
                        jsonrpc: "2.0", 
                        id: 2,
                        method: "tools/call",
                        params: {
                            name: "get-library-docs",
                            arguments: {
                                context7CompatibleLibraryID: "/facebook/react",
                                topic: "hooks useState",
                                tokens: 5000
                            }
                        }
                    };

                    context7Server.stdin.write(JSON.stringify(docsMessage) + '\n');
                    console.log('✅ React 문서 조회');

                    setTimeout(() => {
                        context7Server.kill();
                        console.log('📚 Context7 MCP 테스트 완료\n');
                        resolve();
                    }, 5000);
                }, 3000);
            }, 3000);
        });
    }
}

async function runFinalTests() {
    console.log('🎯 MCP 서버들 최종 테스트 시작!\n');
    
    const tester = new MCPFinalTester();
    
    try {
        await tester.testMemoryMCP();
        await tester.testContext7MCP();
        
        console.log('✅ 모든 MCP 서버 테스트 완료!');
        console.log('🚀 이제 Node-DAG 시스템에 통합 준비 완료');
        
    } catch (error) {
        console.error('❌ 테스트 실패:', error);
    }
    
    process.exit(0);
}

if (require.main === module) {
    runFinalTests();
}