#!/usr/bin/env python3
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
text = (ROOT/'SoftwareHouse/company/budget_policy.yaml').read_text(encoding='utf-8')
cap = int(re.search(r'default_monthly_cap_usd:\s*(\d+)', text).group(1))
section = re.search(r'per_agent_caps(?:_usd)?:\n(?P<body>(?:\s{4}[A-Za-z0-9_-]+:\s*\d+\n)+)', text)
if not section:
    print('FAIL: no per-agent cap section'); sys.exit(1)
total = sum(int(x) for x in re.findall(r':\s*(\d+)\s*$', section.group('body'), flags=re.M))
if total > cap:
    print(f'FAIL: per-agent cap total {total} exceeds global cap {cap}'); sys.exit(1)
print(f'PASS: budget cap sanity validated ({total} <= {cap})')
