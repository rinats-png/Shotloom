"""Draft/final, price expiry, expense gates and human QA — no provider calls."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import copy
import json
import shutil
import subprocess
import uuid

import pytest
import yaml

from shotloom.cli import main
from shotloom.compiler import compile_episode
from shotloom.contracts import contract_hash
from shotloom.costing import cost_for, risk_for, build_plan
from shotloom.io import ShotloomError, load_project, read_state
from shotloom.production import (authorize_quote, import_quote, prepare_request,
                                 production_status, record_stage, reserved_total,
                                 settle_failed_request, void_unsubmitted_authorization)
from shotloom.state import CRITERIA, review_attempt, select_attempt, sum_spend


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'projects'
    assert main(['init', '--slug', 'draft-demo', '--title', 'Draft Demo', '--out', str(root)]) == 0
    path = root / 'draft-demo'
    p = yaml.safe_load((path / 'project.yaml').read_text())
    p['budget'].update({'currency': 'USD', 'max_total': 500.0, 'max_per_attempt': 100.0})
    p['policy']['rights_cleared'] = True
    (path / 'project.yaml').write_text(yaml.safe_dump(p, allow_unicode=True, sort_keys=False))
    p, e = load_project(path, 'EP01')
    compile_episode(path, p, e)
    return path, p, e, {'approvals': [], 'spend': [], 'episodes': {}}


def fake_quote(shot_duration, res='720p', model='kling-3', credits=11.7, phase='preview', *, now=None, draft=False):
    now = now or datetime.now(timezone.utc)
    return {
        'provider': 'higgscheap', 'model': model, 'phase': phase,
        'account_alias': 'test_account', 'checked_at': now.isoformat(),
        'final_resolution': res, 'effective_usd_per_credit': '0.03',
        'dry_run': {
            'dry_run': True, 'valid': True, 'model': model,
            'price': {'unit': 'credits', 'tasks': 1, 'total': credits, 'per_task': credits},
            'state': {'params': {'resolution': res, 'duration': shot_duration,
                                 'aspect': '16:9', 'audio': False, 'draft': draft},
                      'slots': {'start': 0, 'end': 0, 'refs': 0, 'video': 0}}
        },
    }


def test_cost_estimates_5s_and_risks(project):
    assert cost_for('higgscheap', 'seedance-2-5', '480p', 5, audio=True) == Decimal('0.441')
    assert cost_for('higgscheap', 'kling-3', '1080p', 5, audio=False) == Decimal('0.45')
    with pytest.raises(ShotloomError):
        cost_for('higgscheap', 'kling-3', '480p', 5)
    _, p, e, _ = project
    p['budget']['max_total'] = 9999
    plan = build_plan(p, e, provider='higgscheap', model='kling-3')
    assert plan['planning_only'] and plan['shots']
    assert any(s['strategy'] == 'direct' for s in plan['shots'])
    test_shot = copy.deepcopy(e['shots'][0])
    test_shot['production'] = {'risk_tags': ['fight']}
    assert risk_for(test_shot)[0] == 'complex'
    with pytest.raises(ShotloomError):
        risk_for({'production': {'risk_tags': ['unsupported_flag']}})


def test_bad_quote_expired_and_untrusted_inputs(project):
    _, p, e, st = project
    sid = e['shots'][0]['id']
    q = fake_quote(int(e['shots'][0]['duration_s']), now=datetime.now(timezone.utc) - timedelta(hours=1))
    with pytest.raises(ShotloomError, match='veraltet'):
        import_quote(p, e, st, sid, q)
    q = fake_quote(int(e['shots'][0]['duration_s']))
    q['dry_run']['price']['tasks'] = 3
    with pytest.raises(ShotloomError):
        import_quote(p, e, st, sid, q)
    q = fake_quote(int(e['shots'][0]['duration_s']), res='1080p', phase='final', model='seedance-2-5', draft=True)
    with pytest.raises(ShotloomError, match='Draft'):
        import_quote(p, e, st, sid, q)


def test_human_per_attempt_approval_and_budget(project):
    _, p, e, st = project
    sid = e['shots'][0]['id']
    q = import_quote(p, e, st, sid, fake_quote(int(e['shots'][0]['duration_s'])))
    with pytest.raises(ShotloomError, match='Zustimmung'):
        authorize_quote(p, e, st, q['id'], 'Human', False)
    a = authorize_quote(p, e, st, q['id'], 'Human', True)
    assert a['status'] == 'reserved'
    assert reserved_total(st) > 0
    with pytest.raises(ShotloomError, match='bereits'):
        authorize_quote(p, e, st, q['id'], 'Human', True)
    with pytest.raises(ShotloomError):
        void_unsubmitted_authorization(st, q['id'], 'Human', False)
    void_unsubmitted_authorization(st, q['id'], 'Human', True)
    assert reserved_total(st) == 0
    with pytest.raises(ShotloomError):
        void_unsubmitted_authorization(st, q['id'], 'Human', True)


def test_prepare_mcp_handoff_never_executes(project):
    root, p, e, st = project
    sid = e['shots'][0]['id']
    q = import_quote(p, e, st, sid, fake_quote(int(e['shots'][0]['duration_s'])))
    authorize_quote(p, e, st, q['id'], 'Human', True)
    r = prepare_request(root, p, e, st, q['id'])
    assert r['execution_status'] == 'PREPARED_NOT_SUBMITTED'
    assert r['execute_automatically'] is False
    assert r['operation'] == 'AGENT_MCP_HANDOFF'
    assert r['body']['actual_media_ids'] == 'REQUIRED_FROM_PROVIDER_BEFORE_SUBMISSION'
    assert (root / f"compiled/EP01/requests/{q['id']}.json").is_file()
    modified = copy.deepcopy(e)
    modified['shots'][0]['dramatic_intent'] = 'Different story'
    with pytest.raises(ShotloomError, match='ungültig'):
        prepare_request(root, p, modified, st, q['id'])


def test_failing_paid_job_is_reconciled_without_video(project):
    _, p, e, st = project
    sid = e['shots'][0]['id']
    q = import_quote(p, e, st, sid, fake_quote(int(e['shots'][0]['duration_s'])))
    authorize_quote(p, e, st, q['id'], 'Human', True)
    result = settle_failed_request(p, e, st, q['id'], '0.10', 'fake-failure-id', 'Provider moderation')
    assert result['status'] == 'failed' and sum_spend(st) == 0.1
    assert reserved_total(st) == 0
    with pytest.raises(ShotloomError):
        settle_failed_request(p, e, st, q['id'], 0, 'fake-failure-id', 'duplicate')


def test_higgsfield_finalize_draft_cannot_be_faked(project):
    root, p, e, st = project
    sid = e['shots'][0]['id']
    current = datetime.now(timezone.utc)
    draft_id = str(uuid.uuid4())
    entry = {'provider': 'higgsfield_api', 'model': 'seedance-2-5',
             'account_alias': 'account-1', 'phase': 'finalize', 'checked_at': current.isoformat(),
             'draft_request_id': draft_id, 'acknowledge_published_rate_not_live': True,
             'estimated_usd': str(Decimal(str(e['shots'][0]['duration_s'])) * Decimal('0.6518'))}
    q = import_quote(p, e, st, sid, entry)
    authorize_quote(p, e, st, q['id'], 'Human', True)
    with pytest.raises(ShotloomError, match='Kein aktueller'):
        prepare_request(root, p, e, st, q['id'])
    node = st.setdefault('episodes', {}).setdefault('EP01', {}).setdefault(sid, {'attempts': [], 'selected': None})
    preview = {'phase': 'preview', 'draft': True, 'provider': 'higgsfield_api', 'model': 'seedance-2-5',
               'account_alias': 'account-1', 'contract_hash': contract_hash(p, e),
               'provider_request_id': draft_id, 'provider_created_at': (current - timedelta(days=8)).isoformat(),
               'review': {'passed': True}}
    node['attempts'].append(preview)
    with pytest.raises(ShotloomError, match='abgelaufen'):
        prepare_request(root, p, e, st, q['id'])
    preview['provider_created_at'] = (current - timedelta(hours=1)).isoformat()
    preview['provider_expires_at'] = (current - timedelta(minutes=1)).isoformat()
    with pytest.raises(ShotloomError, match='abgelaufen'):
        prepare_request(root, p, e, st, q['id'])
    preview['provider_expires_at'] = (current + timedelta(hours=2)).isoformat()
    response = prepare_request(root, p, e, st, q['id'])
    assert response['body'] == {'draft_id': draft_id, 'resolution': '1080p'}
    assert response['linked_preview_request_id'] == draft_id
    assert response['execute_automatically'] is False
    data = production_status(p, e, st, now=current)
    assert data['drafts'][0]['expired'] is False
    preview['account_alias'] = 'wrong-account'
    with pytest.raises(ShotloomError, match='Kein aktueller'):
        prepare_request(root, p, e, st, q['id'])


def test_preview_not_selectable(project):
    _, p, e, st = project
    sid = e['shots'][0]['id']
    node = st.setdefault('episodes', {}).setdefault('EP01', {}).setdefault(sid, {'attempts': [], 'selected': None})
    node['attempts'].append({'phase': 'preview', 'contract_hash': contract_hash(p, e), 'review': None})
    scores = dict.fromkeys(CRITERIA, 5)
    assert review_attempt(st, e['id'], sid, 1, scores, 'Human', [])['passed']
    with pytest.raises(ShotloomError, match='Vorschau'):
        select_attempt(st, e['id'], sid, 1, contract_hash(p, e))


def test_cli_plan_and_reconciliation(project, tmp_path):
    root, p, e, st = project
    args = ['--project', str(root), '--episode', e['id']]
    assert main(['cost-plan', *args, '--model', 'kling-3', '--write']) == 0
    assert (root / f'compiled/{e["id"]}/cost_plan_REFERENCE_ONLY.json').exists()
    quote_path = tmp_path / 'price.json'
    quote_path.write_text(json.dumps(fake_quote(int(e['shots'][0]['duration_s']))))
    assert main(['quote-import', *args, '--shot', e['shots'][0]['id'], '--file', str(quote_path)]) == 0
    q = read_state(root)['production']['quotes'][0]
    assert main(['stage-authorize', *args, '--quote-id', q['id'], '--by', 'Human', '--confirmed']) == 0
    assert main(['stage-request', *args, '--quote-id', q['id']]) == 0
    assert main(['stage-failure', *args, '--quote-id', q['id'], '--actual-usd', '0',
                 '--provider-request-id', 'test-nocharge', '--reason', 'Provider returned no output']) == 0
    assert main(['production-status', *args]) == 0


def test_real_ffmpeg_preview_then_full_hd_and_no_preview_selection(project, tmp_path):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('ffmpeg or ffprobe missing')
    root, p, e, st = project
    sid = e['shots'][0]['id']
    def clip(width, height):
        path = tmp_path / f'{width}x{height}.mp4'
        subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi',
                        '-i', f'color=c=gray:s={width}x{height}:r=24', '-t', '5.04',
                        '-c:v', 'mpeg4', '-q:v', '7', str(path)], check=True)
        return path
    low = clip(1280, 720)
    q1 = import_quote(p, e, st, sid, fake_quote(5))
    authorize_quote(p, e, st, q1['id'], 'Human', True)
    prepare_request(root, p, e, st, q1['id'])
    result1 = record_stage(root, p, e, st, q1['id'], low, '0.35', 'provider-preview-001')
    assert result1['phase'] == 'preview' and result1['media']['height'] == 720
    with pytest.raises(ShotloomError, match='Vorschau'):
        select_attempt(st, e['id'], sid, 1, contract_hash(p, e))
    q2 = import_quote(p, e, st, sid, fake_quote(5, res='1080p', phase='final', credits=15))
    authorize_quote(p, e, st, q2['id'], 'Human', True)
    with pytest.raises(ShotloomError, match='geprüfter Preview'):
        prepare_request(root, p, e, st, q2['id'])
    review_attempt(st, e['id'], sid, 1, dict.fromkeys(CRITERIA, 5), 'Human', [])
    prepared2 = prepare_request(root, p, e, st, q2['id'])
    assert prepared2['linked_preview_request_id'] == 'provider-preview-001'
    high = clip(1920, 1080)
    result2 = record_stage(root, p, e, st, q2['id'], high, '0.45', 'provider-final-001')
    assert result2['phase'] == 'final'
    review_attempt(st, e['id'], sid, 2, dict.fromkeys(CRITERIA, 5), 'Human', [])
    select_attempt(st, e['id'], sid, 2, contract_hash(p, e))
    assert st['episodes']['EP01'][sid]['selected'] == 2
    assert sum_spend(st) == 0.80
    assert reserved_total(st) == 0
