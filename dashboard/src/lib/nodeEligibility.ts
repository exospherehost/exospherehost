/**
 * Eligibility of a node that has not been picked up by a worker yet.
 *
 * `enqueue_after` is the stored epoch-millisecond instant after which the state manager
 * lets a worker pick the state up (`enqueue_after <= now` on the server). It explains a delay;
 * it does not promise execution at that instant.
 */
export type NodeEligibility =
  /** The eligibility time is still ahead of the viewer's clock. */
  | { kind: 'scheduled'; at: Date }
  /** The eligibility time has passed and the node is still waiting for a worker. */
  | { kind: 'waiting'; at: Date };

export interface NodeEligibilityInput {
  status: string;
  enqueue_after?: number | null;
}

/** Only states a worker has not claimed yet can be waiting on an eligibility time. */
const WAITING_STATUSES: ReadonlySet<string> = new Set(['CREATED']);

/**
 * Classify a node's stored eligibility time against an injected clock.
 * Returns null when nothing should be shown: the node is not waiting to be picked up,
 * or the record carries no usable timestamp (older records, missing field, 0, NaN).
 */
export function getNodeEligibility(
  details: NodeEligibilityInput | null | undefined,
  nowMs: number,
): NodeEligibility | null {
  if (!details || !WAITING_STATUSES.has(details.status)) return null;

  const at = details.enqueue_after;
  if (typeof at !== 'number' || !Number.isFinite(at) || at <= 0) return null;

  return at > nowMs ? { kind: 'scheduled', at: new Date(at) } : { kind: 'waiting', at: new Date(at) };
}

/**
 * Render an instant in the viewer's locale and timezone with an explicit zone label.
 * Formatting is display-only; the wire representation stays epoch milliseconds.
 */
export function formatEligibilityTime(at: Date, locale?: string, timeZone?: string): string {
  return at.toLocaleString(locale, { timeZone, timeZoneName: 'short' });
}
