import { test } from 'node:test';
import assert from 'node:assert/strict';
import { getNodeEligibility, formatEligibilityTime } from './nodeEligibility.ts';

// Fake clock: every case injects `now` instead of reading Date.now(), so no real timers run.
const NOW_MS = Date.UTC(2026, 0, 15, 12, 0, 0); // 2026-01-15T12:00:00Z

test('future delayed CREATED node is scheduled for its stored eligibility time', () => {
  const at = NOW_MS + 90 * 60 * 1000;
  const result = getNodeEligibility({ status: 'CREATED', enqueue_after: at }, NOW_MS);
  assert.deepEqual(result, { kind: 'scheduled', at: new Date(at) });
});

test('past-due CREATED node is reported as eligible and waiting, not as scheduled', () => {
  const at = NOW_MS - 5 * 60 * 1000;
  const result = getNodeEligibility({ status: 'CREATED', enqueue_after: at }, NOW_MS);
  assert.deepEqual(result, { kind: 'waiting', at: new Date(at) });
});

test('an eligibility time equal to now counts as eligible (matches the server-side <= pick-up rule)', () => {
  const result = getNodeEligibility({ status: 'CREATED', enqueue_after: NOW_MS }, NOW_MS);
  assert.equal(result?.kind, 'waiting');
});

test('old record without the field shows nothing (no Invalid Date, no epoch zero)', () => {
  assert.equal(getNodeEligibility({ status: 'CREATED' }, NOW_MS), null);
  assert.equal(getNodeEligibility({ status: 'CREATED', enqueue_after: undefined }, NOW_MS), null);
  assert.equal(getNodeEligibility({ status: 'CREATED', enqueue_after: null }, NOW_MS), null);
  assert.equal(getNodeEligibility({ status: 'CREATED', enqueue_after: 0 }, NOW_MS), null);
  assert.equal(getNodeEligibility({ status: 'CREATED', enqueue_after: Number.NaN }, NOW_MS), null);
});

test('already queued, running or finished nodes carry no waiting message', () => {
  const at = NOW_MS + 60 * 1000;
  for (const status of ['QUEUED', 'EXECUTED', 'SUCCESS', 'ERRORED', 'TIMEDOUT', 'CANCELLED', 'PRUNED', 'NEXT_CREATED_ERROR'] as const) {
    assert.equal(getNodeEligibility({ status, enqueue_after: at }, NOW_MS), null, status);
  }
});

test('missing details yield nothing', () => {
  assert.equal(getNodeEligibility(null, NOW_MS), null);
  assert.equal(getNodeEligibility(undefined, NOW_MS), null);
});

test('the same instant renders in the viewer timezone with a zone label, never re-persisted', () => {
  const at = new Date(Date.UTC(2026, 0, 15, 23, 30, 0)); // near a day boundary
  const utc = formatEligibilityTime(at, 'en-US', 'UTC');
  const tokyo = formatEligibilityTime(at, 'en-US', 'Asia/Tokyo');
  const la = formatEligibilityTime(at, 'en-US', 'America/Los_Angeles');
  assert.match(utc, /UTC/);
  assert.match(tokyo, /GMT\+9|JST/);
  assert.match(la, /PST|GMT-8/);
  // Different calendar days for the same instant; the instant itself is unchanged.
  assert.match(tokyo, /1\/16\/2026/);
  assert.match(la, /1\/15\/2026/);
  assert.equal(at.getTime(), Date.UTC(2026, 0, 15, 23, 30, 0));
});
