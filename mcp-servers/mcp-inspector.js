#!/usr/bin/env node

/**
 * MCP 서버 도구명 확인 스크립트
 */

const { spawn } = require('child_process');

class MCPInspector {
    constructor(serverCommand, serverArgs, serverName) {
        this.serverCommand = serverCommand;
        this.serverArgs = serverArgs;
        this.serverName = serverName;
        this.serverProcess = null;
    }

    async inspectServer() {
        console.log(`\n🔍 ${this.serverName} 서버 검사 시작...`);
        
        this.serverProcess = spawn(this.serverCommand, this.serverArgs, {
            stdio: ['pipe', 'pipe', 'inherit']
        });

        return new Promise((resolve) => {
            let hasOutput = false;
            
            this.serverProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log(`${this.serverName} 출력:`, output);
                hasOutput = true;
            });

            // 도구 목록 요청
            const listToolsMessage = {
                jsonrpc: "2.0",
                id: 1,
                method: "tools/list"
            };

            setTimeout(() => {
                if (this.serverProcess && !this.serverProcess.killed) {
                    this.serverProcess.stdin.write(JSON.stringify(listToolsMessage) + '\n');
                    console.log(`📝 ${this.serverName}에 도구 목록 요청 전송`);
                }
            }, 3000);

            // 서버 정보 요청
            const initMessage = {
                jsonrpc: "2.0",
                id: 0,
                method: "initialize",
                params: {
                    protocolVersion: "2024-11-05",
                    capabilities: {},
                    clientInfo: {
                        name: "test-client",
                        version: "1.0.0"
                    }
                }
            };

            setTimeout(() => {
                if (this.serverProcess && !this.serverProcess.killed) {
                    this.serverProcess.stdin.write(JSON.stringify(initMessage) + '\n');
                    console.log(`🔧 ${this.serverName}에 초기화 요청 전송`);
                }
            }, 5000);

            // 10초 후 정리
            setTimeout(() => {
                this.stop();
                resolve(hasOutput);
            }, 10000);
        });
    }

    stop() {
        if (this.serverProcess) {
            this.serverProcess.kill();
            console.log(`🛑 ${this.serverName} 서버 종료됨`);
        }
    }
}

async function inspectAllServers() {
    const servers = [
        {
            command: 'npx',
            args: ['-y', '@modelcontextprotocol/server-memory'],
            name: 'Memory'
        },
        {
            command: 'npx', 
            args: ['-y', '@upstash/context7-mcp'],
            name: 'Context7'
        }
    ];

    console.log('🔍 MCP 서버들의 도구명 확인을 시작합니다...\n');

    for (const server of servers) {
        const inspector = new MCPInspector(server.command, server.args, server.name);
        try {
            await inspector.inspectServer();
        } catch (error) {
            console.error(`❌ ${server.name} 검사 실패:`, error);
        }
        
        // 서버 간 대기
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    console.log('\n✅ 모든 서버 검사 완료');
    process.exit(0);
}

if (require.main === module) {
    inspectAllServers();
}