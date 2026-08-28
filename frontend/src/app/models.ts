export interface HealthInfo {
  status: string;
  samplePath: string;
  parserScript?: string | null;
  usingLocalParser?: boolean;
}

export interface DomainInfo {
  id: string;
  label: string;
  status: string;
}

export interface RunInfo {
  id: string;
  domain: string;
  sourcePath: string;
  status: string;
  createdAt: string;
  eventCount: number;
}

export interface Kpis {
  totalRequests: number;
  completedResponses: number;
  unmatchedCount: number;
  matchRate: number | null;
  avgDurationSeconds: number | null;
  p95DurationSeconds: number | null;
  maxDurationSeconds: number | null;
}

export interface HourlyRow {
  hour: string;
  started: number;
  completed: number;
  avgDurationSeconds: number | null;
  matchRate: number | null;
  completionGap: number;
}

export interface RequestTypeRow {
  requestType: string;
  count: number;
  percent: number;
}

export interface DealRow {
  groupId: string;
  tradeCount: number;
  minDurationSeconds: number | null;
  maxDurationSeconds: number | null;
  avgDurationSeconds: number | null;
}

export interface IssueRow {
  kind: string;
  eventId: string;
  displayId: string;
  summary: string;
}

export interface Metrics {
  category: string | null;
  kpis: Kpis;
  hourly: HourlyRow[];
  requestTypes: RequestTypeRow[];
  perDeal: DealRow[];
  issues: IssueRow[];
}

export interface EventItem {
  id: string;
  domain: string;
  displayId: string;
  groupId: string;
  category: string;
  workflow: string;
  requestType: string;
  status: string;
  outcome: string | null;
  start: string | null;
  end: string | null;
  durationSeconds: number | null;
  requestCount: number;
  responseCount: number;
  requestFiles: string[];
  responseFiles: string[];
  requestPayload: string | null;
  responsePayload: string | null;
}

export interface Hop {
  timestamp: string | null;
  thread: string | null;
  service: string | null;
  workflow: string | null;
  level: string | null;
  summary: string;
  payload: string | null;
  sourceFile: string;
  gapSeconds: number | null;
}

export interface EventQuery {
  category?: string;
  status?: string;
  dealId?: string;
  hour?: string;
  q?: string;
}
