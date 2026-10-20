#!/usr/bin/env python3
"""Opt-in failure notifications and conservative, history-preserving candidate cleanup.

Without --apply, only print a plan. Never evaluate candidate code, update main,
rewrite commits, or delete an unmerged candidate. Git credentials are step-scoped.
"""
import argparse
import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess

CANDIDATE = re.compile(r'automation/upstream-([1-9][0-9]*)-([1-9][0-9]*)')
MARKER = '<!-- openvsp-upstream-health-v1 -->'
TITLE = 'OpenVSP upstream candidate workflow needs attention'
GRACE_DAYS = 7


def git(*args, check=True, env=None):
    return subprocess.run(['git', *args], text=True, capture_output=True, check=check, env=env)


class GitHub:
    def __init__(self, repository):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository')
        self.repository = repository

    def api(self, path, method='GET', data=None):
        command = ['gh', 'api', f'repos/{self.repository}/{path}', '--method', method]
        if data is not None:
            command += ['--input', '-']
        result = subprocess.run(command, input=json.dumps(data) if data is not None else None,
                                text=True, capture_output=True, check=True)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def pages(self, path):
        rows, page = [], 1
        separator = '&' if '?' in path else '?'
        while True:
            result = self.api(f'{path}{separator}per_page=100&page={page}')
            rows.extend(result)
            if len(result) < 100:
                return rows
            page += 1


def failure_state(prepare, build, changed):
    allowed = {'success', 'failure', 'cancelled', 'skipped'}
    if prepare not in allowed or build not in allowed or changed not in ('true', 'false', ''):
        raise ValueError('Unrecognized workflow outcome')
    return (prepare != 'success' or build in {'failure', 'cancelled'} or changed == ''
            or (changed == 'true' and build != 'success'))


def notify(client, prepare, build, changed, run_id, apply=False):
    if not re.fullmatch(r'[1-9][0-9]*', run_id):
        raise ValueError('Invalid workflow run ID')
    failed = failure_state(prepare, build, changed)
    issues = [i for i in client.pages('issues?state=all&creator=github-actions%5Bbot%5D')
              if i.get('title') == TITLE and MARKER in (i.get('body') or '')
              and i.get('user', {}).get('login') == 'github-actions[bot]' and 'pull_request' not in i]
    if len(issues) > 1:
        raise ValueError('Multiple health issues; refusing to change an ambiguous issue')
    issue = issues[0] if issues else None
    body = (MARKER + '\n\n' + ('上游候选准备或验证失败。' if failed else '上游候选工作流已恢复。')
            + f'\n\n准备：`{prepare}`；验证：`{build}`；候选变化：`{changed or "unknown"}`。'
            + f'\n\n[查看运行与失败步骤](https://github.com/{client.repository}/actions/runs/{run_id})。'
            + '\n\n此流程不自动推进 main 或公开 Release。请检查日志、修复冲突或验证失败后重跑；'
              '恢复时本条状态会更新。')
    action = 'create' if failed and not issue else 'update' if failed else 'close' if issue and issue['state'] == 'open' else 'none'
    result = dict(action=action, failed=failed, run_id=run_id,
                  issue_number=issue['number'] if issue else None, applied=False)
    if apply and action != 'none':
        if action == 'create':
            issue = client.api('issues', 'POST', dict(title=TITLE, body=body,
                               assignees=[client.repository.split('/')[0]]))
            result['issue_number'] = issue['number']
        else:
            client.api(f'issues/{issue["number"]}', 'PATCH', dict(body=body,
                       state='open' if failed else 'closed',
                       **({'state_reason': 'completed'} if not failed else {})))
        result['applied'] = True
    return result


def candidate_plan(client, now=None):
    now = now or datetime.now(timezone.utc)
    active = {p.get('head', {}).get('ref') for p in client.pages('pulls?state=open')}
    rows = git('for-each-ref', '--format=%(refname:strip=3) %(objectname)',
               'refs/remotes/origin/automation/upstream-*').stdout.splitlines()
    plan = []
    for row in rows:
        name, sha = row.split()
        match = CANDIDATE.fullmatch(name)
        if not match or not re.fullmatch('[0-9a-f]{40}', sha):
            continue
        item = dict(branch=name, sha=sha, eligible=False, reason='unmerged')
        if name in active:
            item['reason'] = 'open pull request'
        elif git('merge-base', '--is-ancestor', sha, 'origin/main', check=False).returncode == 0:
            run = client.api(f'actions/runs/{match[1]}')
            created = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
            if run.get('path') != '.github/workflows/upstream-watch.yml':
                item['reason'] = 'unrecognized source workflow'
            elif int(run.get('run_attempt', 0)) < int(match[2]):
                item['reason'] = 'unrecognized source attempt'
            elif run.get('status') != 'completed':
                item['reason'] = 'source workflow still active'
            elif now - created < timedelta(days=GRACE_DAYS):
                item['reason'] = 'seven-day grace period'
            else:
                item.update(eligible=True, reason='merged; no open PR; grace period elapsed')
        plan.append(item)
    return plan


def remove_candidate(item, token):
    name, sha = item['branch'], item['sha']
    if not item.get('eligible') or not CANDIDATE.fullmatch(name) or not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('Invalid or ineligible candidate deletion')
    git('merge-base', '--is-ancestor', sha, 'origin/main')
    env = dict(os.environ, GIT_CONFIG_COUNT='2',
               GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
               GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + base64.b64encode(('x-access-token:' + token).encode()).decode(),
               GIT_CONFIG_KEY_1='core.hooksPath', GIT_CONFIG_VALUE_1='/dev/null')
    # This lease can only delete exactly the recorded ref, never rewrite history.
    git('push', f'--force-with-lease=refs/heads/{name}:{sha}', 'origin',
        f':refs/heads/{name}', env=env)


def cleanup(client, output, apply=False):
    plan = candidate_plan(client)
    output.parent.mkdir(parents=True, exist_ok=True)
    def save():
        output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    save()  # Retain branch -> SHA evidence even if an individual deletion fails.
    for item in plan:
        item['deleted'] = False
        if apply and item['eligible']:
            # Recheck PR usage immediately before the exact-ref lease deletion.
            if any(p.get('head', {}).get('ref') == item['branch'] for p in client.pages('pulls?state=open')):
                item.update(eligible=False, reason='open pull request appeared')
            else:
                remove_candidate(item, os.environ['GH_TOKEN'])
                item['deleted'] = True
        save()
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('notify', 'cleanup'))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('candidate-maintenance.json'))
    args = parser.parse_args()
    client = GitHub(os.environ['GITHUB_REPOSITORY'])
    if args.mode == 'notify':
        result = notify(client, os.environ['PREPARE_RESULT'], os.environ['BUILD_RESULT'],
                        os.environ['CANDIDATE_CHANGED'], os.environ['GITHUB_RUN_ID'], args.apply)
    else:
        result = cleanup(client, args.output, args.apply)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if summary := os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(summary, 'a', encoding='utf-8') as handle:
            handle.write('\nCandidate maintenance (' + ('apply' if args.apply else 'read-only plan') + '):\n\n```json\n' + text + '\n```\n')


if __name__ == '__main__':
    main()
