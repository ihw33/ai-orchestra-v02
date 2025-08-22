#!/usr/bin/env python3
"""
Auto-grader for AI Orchestra v02
Tests predefined scenarios against the system
"""

import argparse
import yaml
import sys
import subprocess
import time
from pathlib import Path

def run_scenario(scenario):
    """Run a single test scenario"""
    name = scenario.get('name', 'unnamed')
    pane = scenario.get('pane', '%3')
    task_id = scenario.get('task_id', 'test')
    command = scenario.get('command')
    expected = scenario.get('expected', 'OK')
    timeout_ack = scenario.get('timeout_ack', 5)
    timeout_run = scenario.get('timeout_run', 10)
    timeout_eot = scenario.get('timeout_eot', 30)
    
    cmd = [
        'python', 'main.py',
        '--pane', pane,
        '--task', task_id,
        '--cmd', command,
        '--timeout-ack', str(timeout_ack),
        '--timeout-run', str(timeout_run),
        '--timeout-eot', str(timeout_eot)
    ]
    
    if scenario.get('skip_idempotency'):
        cmd.append('--skip-idempotency')
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_eot + 5
        )
        
        # Check if expected string is in output
        output = result.stdout + result.stderr
        
        if expected == 'OK':
            success = result.returncode == 0 and 'EOT OK' in output
        elif expected == 'FAIL':
            success = result.returncode != 0
        elif expected.startswith('NO_'):
            success = expected in output
        else:
            success = expected in output
            
        return {
            'name': name,
            'success': success,
            'output': output[:200],  # First 200 chars
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'name': name,
            'success': False,
            'output': 'TIMEOUT',
            'returncode': -1
        }
    except Exception as e:
        return {
            'name': name,
            'success': False,
            'output': str(e),
            'returncode': -1
        }

def main():
    parser = argparse.ArgumentParser(description='Auto-grade AI Orchestra scenarios')
    parser.add_argument(
        '--scenarios',
        required=True,
        help='YAML file with test scenarios'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Load scenarios
    try:
        with open(args.scenarios, 'r') as f:
            data = yaml.safe_load(f)
            scenarios = data.get('scenarios', [])
    except Exception as e:
        print(f"❌ Failed to load scenarios: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run each scenario
    results = []
    for scenario in scenarios:
        if args.verbose:
            print(f"Running: {scenario.get('name', 'unnamed')}...")
        result = run_scenario(scenario)
        results.append(result)
        if args.verbose:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['name']}")
    
    # Print summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nAUTO-GRADE {passed}/{total} passed")
    
    # Print failures (max 3 lines)
    failures = [r for r in results if not r['success']]
    for i, fail in enumerate(failures[:3]):
        print(f"  ❌ {fail['name']}: {fail['output'][:50]}...")
    
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()