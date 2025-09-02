#!/bin/bash

# AI Orchestra v02 - 불필요한 파일 정리 스크립트
# 날짜: 2025-01-02
# 목적: 어댑터 패턴으로 구현되지 않은 파일들을 deprecated/로 이동

echo "🧹 AI Orchestra v02 파일 정리 시작..."

# deprecated 디렉토리가 없으면 생성
mkdir -p deprecated/scripts
mkdir -p deprecated/applescripts
mkdir -p deprecated/shell_scripts
mkdir -p deprecated/docs
mkdir -p deprecated/temp_files

# 1. Python 스크립트 이동 (어댑터 패턴 없는 독립 실행 파일)
echo "📦 Python 스크립트 이동 중..."
python_files=(
    "ai_communicator.py"
    "async_orchestrator.py"
    "auto_task_handler.py"
    "cache_manager.py"
    "check_sessions.py"
    "click_and_type.py"
    "conversational_automation.py"
    "debug_iterm.py"
    "direct_applescript.py"
    "error_handler.py"
    "evolution_logger.py"
    "fix_auto_processor.py"
    "fix_github_integration.py"
    "fix_persona_integration.py"
    "focus_and_send.py"
    "force_enter.py"
    "improved_node_executor.py"
    "issue_keyword_recommender.py"
    "iterm2_api_test.py"
    "main.py"
    "main_mock.py"
    "manual_select_then_type.py"
    "mcp_executor.py"
    "metrics_system.py"
    "monitor_background_gemini.py"
    "node_executor.py"
    "node_system.py"
    "orchestrator.py"
    "original_code.py"
    "parallel_implementation_plan.py"
    "performance_test.py"
    "persona_training_system.py"
    "pm_auto_hook.py"
    "pm_auto_processor.py"
    "pm_monitor.py"
    "pm_orchestration_controller.py"
    "pm_task_executor.py"
    "process_engine.py"
    "process_issue_62.py"
    "realistic_parallel_plan.py"
    "relay_pipeline_system.py"
    "safe_send.py"
    "send_to_gemini.py"
    "send_to_gemini_correct.py"
    "send_to_gemini_final.py"
    "send_with_cr.py"
    "send_with_enter.py"
    "simple_test_iterm.py"
    "test_actions_node.py"
    "test_ai_execution.py"
    "test_context7_integration.py"
    "test_enhanced_workflow.py"
    "test_evolution.py"
    "test_persona_integration.py"
    "test_recursive_growth.py"
    "test_sc_integration.py"
    "trigger_system.py"
    "unified_orchestrator.py"
    "use_session_id.py"
    "workflow_definitions.py"
    "workflow_runner.py"
    "activate_and_send.py"
    "context7_auto_loader.py"
    "context7_node_executor.py"
    "final_attempt.py"
)

for file in "${python_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" deprecated/scripts/
        echo "  ✓ $file → deprecated/scripts/"
    fi
done

# master_orchestrator.py와 multi_ai_orchestrator.py는 이미 deprecated에 있으므로 루트에서 제거
if [ -f "master_orchestrator.py" ]; then
    rm "master_orchestrator.py"
    echo "  ✓ master_orchestrator.py 제거 (deprecated에 이미 존재)"
fi
if [ -f "multi_ai_orchestrator.py" ]; then
    rm "multi_ai_orchestrator.py"
    echo "  ✓ multi_ai_orchestrator.py 제거 (deprecated에 이미 존재)"
fi

# 2. AppleScript 파일 이동
echo "🍎 AppleScript 파일 이동 중..."
applescript_files=(
    "check_and_restart.applescript"
    "enforce_reporting.applescript"
    "fix_p0_issues.applescript"
    "orchestrate_4_claudes.applescript"
    "orchestrate_4_claudes_simple.applescript"
    "paste_to_gemini.applescript"
    "phase2_orchestrate.applescript"
    "redirect_llm_reporting.applescript"
    "restart_llm.applescript"
    "sc_implement_fixes.applescript"
    "sc_implement_step1.applescript"
    "send_english_only.applescript"
    "send_gemini_simple.applescript"
    "send_long_message.applescript"
    "send_native_iterm.applescript"
    "send_one_line.applescript"
    "send_slow.applescript"
    "send_to_gemini.applescript"
    "send_to_gemini_exact.applescript"
    "send_to_gemini_pane.applescript"
    "send_to_iterm_gemini.applescript"
    "send_via_keystrokes.applescript"
    "start_llm_server.applescript"
    "test_calculation.applescript"
)

for file in "${applescript_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" deprecated/applescripts/
        echo "  ✓ $file → deprecated/applescripts/"
    fi
done

# 3. Shell 스크립트 이동
echo "🐚 Shell 스크립트 이동 중..."
shell_files=(
    "auto_report_demo.sh"
    "bts_ai_mixed.sh"
    "bts_greetings.sh"
    "github_gemini_demo.sh"
    "monitor_gemini.sh"
    "pm_monitor.sh"
    "pm_start.sh"
    "pm_workflow.sh"
    "pr29_solution.sh"
    "quick_start.sh"
    "run_orchestra.sh"
    "simple_test.sh"
    "speed_test.sh"
    "start_test.sh"
    "test_ai_template.sh"
    "test_persona_issue.sh"
    "test_single_persona.sh"
    "trigger_orchestration.sh"
    "update_docs_demo.sh"
)

for file in "${shell_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" deprecated/shell_scripts/
        echo "  ✓ $file → deprecated/shell_scripts/"
    fi
done

# 4. 임시/보고서 MD 파일 이동
echo "📝 임시 문서 파일 이동 중..."
md_files=(
    "BEFORE_AFTER_COMPARISON.md"
    "CODE_REVIEW_REPORT.md"
    "CONTEXT7_INTEGRATION.md"
    "ISSUE_34_SERVICE_REVIEW_REPORT.md"
    "ISSUE_63_ANALYSIS.md"
    "ISSUE_TEMPLATE_LEGO_SYSTEM.md"
    "ISSUE_TEMPLATE_WITH_KEYWORDS.md"
    "IWL_ORCHESTRA_SYSTEM_SUMMARY.md"
    "LABEL_HASHTAG_GUIDE.md"
    "OPTIMIZATION_COMPLETE.md"
    "PROJECT_STATUS_REPORT.md"
    "SYSTEM_EXECUTION_AUDIT.md"
    "issue_101_final_report.md"
    "issue_101_persona_assignment_20250902_145044.md"
)

for file in "${md_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" deprecated/docs/
        echo "  ✓ $file → deprecated/docs/"
    fi
done

# 5. 임시 파일들 이동
echo "🗑️ 임시 파일 이동 중..."
temp_files=(
    "cleanup_list.txt"
    "code_modification_approvals.json"
    "learned_dag_patterns.json"
    "learned_patterns.json"
    "metrics_lite.jsonl"
    "node_config.json"
    "orchestra_status.txt"
    "persona_assignment_results_20250902_141214.json"
    "pm_activity.log"
    "pm_status.json"
    "refactor_request.txt"
    "test_bg.txt"
    "test_claude.txt"
    "triggers.json"
    "gemini_expect.exp"
    "orchestra.log"
)

for file in "${temp_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" deprecated/temp_files/
        echo "  ✓ $file → deprecated/temp_files/"
    fi
done

echo ""
echo "✅ 파일 정리 완료!"
echo ""
echo "📊 정리 결과:"
echo "  - Python 스크립트: deprecated/scripts/"
echo "  - AppleScript: deprecated/applescripts/"
echo "  - Shell 스크립트: deprecated/shell_scripts/"
echo "  - 임시 문서: deprecated/docs/"
echo "  - 임시 파일: deprecated/temp_files/"
echo ""
echo "💡 다음 단계:"
echo "  1. deprecated/ 폴더 검토"
echo "  2. 필요한 기능 선별"
echo "  3. DDD 구조로 재구현"