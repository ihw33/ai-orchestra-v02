#!/usr/bin/env node

/**
 * Context7 MCP 서버 테스트 스크립트
 */

const { spawn } = require('child_process');

class Context7MCPTester {
    constructor() {
        this.serverProcess = null;
    }

    async startServer() {
        console.log('📚 Context7 MCP 서버 시작...');
        
        this.serverProcess = spawn('npx', ['-y', '@upstash/context7-mcp'], {
            stdio: ['pipe', 'pipe', 'inherit']
        });

        return new Promise((resolve, reject) => {
            let serverReady = false;
            
            this.serverProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log('서버 출력:', output);
                
                if (output.includes('running') || output.includes('ready')) {
                    serverReady = true;
                }
            });

            this.serverProcess.on('error', (error) => {
                console.error('❌ 서버 시작 실패:', error);
                reject(error);
            });

            // 10초 후 서버 준비 확인
            setTimeout(() => {
                if (serverReady) {
                    console.log('✅ Context7 MCP 서버가 시작되었습니다');
                    resolve();
                } else {
                    console.log('⚠️ 서버 상태 불확실하지만 계속 진행');
                    resolve();
                }
            }, 10000);
        });
    }

    async testDocumentationFetch() {
        console.log('🧪 문서 조회 테스트...');
        
        // Context7 문서 조회 메시지
        const queryMessage = {
            jsonrpc: "2.0",
            id: 1,
            method: "tools/call",
            params: {
                name: "fetch_documentation",
                arguments: {
                    query: "react hooks useState",
                    source: "react"
                }
            }
        };

        try {
            this.serverProcess.stdin.write(JSON.stringify(queryMessage) + '\n');
            console.log('✅ React 문서 조회 테스트 전송');

            // Node.js 문서 조회
            const nodeQuery = {
                jsonrpc: "2.0",
                id: 2,
                method: "tools/call",
                params: {
                    name: "fetch_documentation", 
                    arguments: {
                        query: "fs.readFile",
                        source: "nodejs"
                    }
                }
            };

            this.serverProcess.stdin.write(JSON.stringify(nodeQuery) + '\n');
            console.log('✅ Node.js 문서 조회 테스트 전송');

        } catch (error) {
            console.error('❌ 테스트 실패:', error);
        }
    }

    async stop() {
        if (this.serverProcess) {
            this.serverProcess.kill();
            console.log('🛑 Context7 서버 종료됨');
        }
    }
}

// 테스트 실행
async function runTest() {
    const tester = new Context7MCPTester();
    
    try {
        await tester.startServer();
        await tester.testDocumentationFetch();
        
        // 15초 후 종료
        setTimeout(async () => {
            await tester.stop();
            process.exit(0);
        }, 15000);
        
    } catch (error) {
        console.error('❌ 테스트 실패:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    runTest();
}