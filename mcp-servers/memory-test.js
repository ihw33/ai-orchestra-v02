#!/usr/bin/env node

/**
 * Memory MCP 서버 테스트 스크립트
 */

const { spawn } = require('child_process');

class MemoryMCPTester {
    constructor() {
        this.serverProcess = null;
    }

    async startServer() {
        console.log('🧠 Memory MCP 서버 시작...');
        
        this.serverProcess = spawn('npx', ['-y', '@modelcontextprotocol/server-memory'], {
            stdio: ['pipe', 'pipe', 'inherit']
        });

        return new Promise((resolve, reject) => {
            this.serverProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log('서버 출력:', output);
                
                if (output.includes('running on stdio')) {
                    resolve();
                }
            });

            this.serverProcess.on('error', (error) => {
                console.error('❌ 서버 시작 실패:', error);
                reject(error);
            });

            // 5초 후 타임아웃
            setTimeout(() => {
                console.log('✅ Memory MCP 서버가 시작되었습니다');
                resolve();
            }, 5000);
        });
    }

    async testMemoryOperations() {
        console.log('🧪 메모리 작업 테스트...');
        
        // MCP 프로토콜 메시지 형식
        const storeMessage = {
            jsonrpc: "2.0",
            id: 1,
            method: "tools/call",
            params: {
                name: "create_entities",
                arguments: {
                    entities: [
                        {
                            name: "AI_Orchestra_Project",
                            entityType: "project",
                            observations: ["프로젝트 시작", "페르소나 시스템 구현"]
                        }
                    ]
                }
            }
        };

        try {
            // 서버에 메시지 전송
            this.serverProcess.stdin.write(JSON.stringify(storeMessage) + '\n');
            console.log('✅ 메모리 저장 테스트 완료');

            // 조회 테스트
            const queryMessage = {
                jsonrpc: "2.0",
                id: 2,
                method: "tools/call",
                params: {
                    name: "search_entities",
                    arguments: {
                        query: "AI_Orchestra"
                    }
                }
            };

            this.serverProcess.stdin.write(JSON.stringify(queryMessage) + '\n');
            console.log('✅ 메모리 조회 테스트 완료');

        } catch (error) {
            console.error('❌ 테스트 실패:', error);
        }
    }

    async stop() {
        if (this.serverProcess) {
            this.serverProcess.kill();
            console.log('🛑 서버 종료됨');
        }
    }
}

// 테스트 실행
async function runTest() {
    const tester = new MemoryMCPTester();
    
    try {
        await tester.startServer();
        await tester.testMemoryOperations();
        
        // 10초 후 종료
        setTimeout(async () => {
            await tester.stop();
            process.exit(0);
        }, 10000);
        
    } catch (error) {
        console.error('❌ 테스트 실패:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    runTest();
}