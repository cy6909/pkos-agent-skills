#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

market_path = ROOT / '.agents/plugins/marketplace.json'
manifest_path = ROOT / 'plugins/pkos/.codex-plugin/plugin.json'

for p in [market_path, manifest_path]:
    if not p.exists():
        errors.append(f'missing required file: {p.relative_to(ROOT)}')

try:
    market = json.loads(market_path.read_text(encoding='utf-8'))
    if market.get('name') != 'pkos-agent-skills':
        errors.append('marketplace name must be pkos-agent-skills')
    if not market.get('plugins'):
        errors.append('marketplace has no plugins')
except Exception as e:
    errors.append(f'invalid marketplace json: {e}')

try:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for key in ['name', 'version', 'description', 'skills']:
        if not manifest.get(key):
            errors.append(f'plugin manifest missing {key}')
    prompts = manifest.get('interface', {}).get('defaultPrompt', [])
    if not isinstance(prompts, list) or len(prompts) > 3:
        errors.append('plugin interface.defaultPrompt must contain at most 3 prompts')
    elif any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in prompts):
        errors.append('each plugin interface.defaultPrompt must be a string of at most 128 characters')
except Exception as e:
    errors.append(f'invalid plugin manifest json: {e}')

skill_root = ROOT / 'plugins/pkos/skills'
skills = sorted(skill_root.glob('*/SKILL.md'))
if not skills:
    errors.append('no SKILL.md files found')

notion_language_marker = 'NOTION_WRITE_LANGUAGE=zh-CN'
notion_contract_path = ROOT / 'plugins/pkos/references/notion-tool-contract.md'
if not notion_contract_path.exists():
    errors.append('missing shared Notion tool contract')
else:
    notion_contract = notion_contract_path.read_text(encoding='utf-8')
    for required in [
        notion_language_marker,
        'accurate, natural, easy-to-understand Simplified Chinese',
        'Keep machine contracts and precision-sensitive values verbatim',
        'Read back every affected title, property value, and page section',
    ]:
        if required not in notion_contract:
            errors.append(f'Notion tool contract missing required language rule: {required}')

for p in skills:
    text = p.read_text(encoding='utf-8')
    if notion_language_marker not in text:
        errors.append(f'{p.relative_to(ROOT)} missing {notion_language_marker}')
    if not text.startswith('---\n'):
        errors.append(f'{p.relative_to(ROOT)} missing YAML frontmatter')
        continue
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        errors.append(f'{p.relative_to(ROOT)} invalid frontmatter block')
        continue
    fm = m.group(1)
    name = re.search(r'^name:\s*(.+)$', fm, re.M)
    desc = re.search(r'^description:\s*(.+)$', fm, re.M)
    if not name or not desc:
        errors.append(f'{p.relative_to(ROOT)} requires name + description')
    elif name.group(1).strip() != p.parent.name:
        errors.append(f'{p.relative_to(ROOT)} name does not match directory')

required_docs = [
    'README.md', 'README.zh-CN.md',
    'docs/en/SPEC.md', 'docs/zh-CN/SPEC.md',
    'docs/en/INSTALL.md', 'docs/zh-CN/INSTALL.md',
    'docs/en/NOTION-MCP.md', 'docs/zh-CN/NOTION-MCP.md'
]
for rel in required_docs:
    if not (ROOT / rel).exists():
        errors.append(f'missing bilingual doc: {rel}')

if errors:
    print('PKOS validation failed:')
    for e in errors:
        print(f'- {e}')
    sys.exit(1)

print(f'PKOS validation OK: {len(skills)} skills, marketplace + plugin manifests valid.')
