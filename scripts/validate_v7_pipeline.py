#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[1]
def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)
required = [
    'workspace/01_PRDs','workspace/02_SDDs','workspace/03_Feature_Tickets','workspace/04_TDD_Red_Tests','workspace/05_QA_Audit_Logs','workspace/06_Project_Repos','workspace/07_Finalization',
    'rules/arthur_single_model_gpt5mini.md','rules/model_map.md','scripts/one_click_install.sh'
]
missing=[p for p in required if not (ROOT/p).exists()]
if missing:
    fail('Missing required paths:\n'+'\n'.join(missing))
if 'Arthur = GPT-5 mini under Hermes' not in (ROOT/'rules/arthur_single_model_gpt5mini.md').read_text(encoding='utf-8'):
    fail('Arthur single-model policy must set Arthur = GPT-5 mini under Hermes')
manifest_path=ROOT/'manifest.json'
if manifest_path.exists():
    data=json.loads(manifest_path.read_text(encoding='utf-8'))
    if data.get('arthur',{}).get('model')!='GPT-5 mini':
        fail('manifest Arthur model must be GPT-5 mini')
print('PASS: V7 namespaced pipeline validated.')
print('PASS: Arthur single-model GPT-5 mini policy validated.')
