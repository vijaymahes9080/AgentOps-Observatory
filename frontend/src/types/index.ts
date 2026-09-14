export type PageView = 
  | 'overview'
  | 'live_runs'
  | 'run_detail'
  | 'tool_inventory'
  | 'incidents'
  | 'policy_violations'
  | 'redaction_events'
  | 'cost_energy'
  | 'n8n_view'
  | 'mcp_view'
  | 'exports';

export interface MetricsOverview {
  total_runs: number;
  open_incidents: number;
  total_policy_violations: number;
  total_redactions: number;
  total_tokens: number;
  total_cost_usd: number;
  total_energy_kwh: number;
  total_carbon_gco2eq: number;
  compliance_rate_percent: number;
}

export interface AgentRunSummary {
  run_id: string;
  agent_name: string;
  goal?: string;
  status: string;
  is_partial: boolean;
  missing_reasons: string[];
  total_events: number;
  total_duration_ms: number;
  total_tokens: number;
  total_cost_usd: number;
  total_energy_kwh: number;
  total_carbon_gco2eq: number;
  policy_violation_count: number;
  redaction_count: number;
  created_at: string;
}

export interface RunEventItem {
  event_id: string;
  parent_id?: string;
  event_type: string;
  source: string;
  actor: string;
  name?: string;
  status: string;
  duration_ms: number;
  payload: Record<string, any>;
  current_hash: string;
  prev_hash: string;
  timestamp: string;
}

export interface RunDetail extends AgentRunSummary {
  missing_telemetry_reasons: string[];
  events: RunEventItem[];
}

export interface TimelineItem {
  event_id: string;
  name: string;
  type: string;
  status: string;
  offset_ms: number;
  duration_ms: number;
  has_error: boolean;
  is_orphan: boolean;
  parent_id?: string;
}

export interface TraceNodeData {
  id: string;
  event_type: string;
  name: string;
  parent_id?: string;
  status: string;
  duration_ms: number;
  start_time: string;
  offset_ms: number;
  children: string[];
  has_error: boolean;
  is_partial_orphan: boolean;
}

export interface TraceGraphData {
  run_id: string;
  root_nodes: string[];
  nodes: Record<string, TraceNodeData>;
  edges: Array<{ source: string; target: string; relation: string }>;
  timeline: TimelineItem[];
  total_duration_ms: number;
  is_partial: boolean;
  missing_telemetry_warnings: string[];
  failed_node_ids: string[];
}

export interface PolicyViolation {
  violation_id: string;
  run_id: string;
  event_id?: string;
  rule_id: string;
  rule_name: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  evidence: string;
  remediation: string;
  confidence: number;
  timestamp: string;
}

export interface RedactionAuditItem {
  audit_id: string;
  run_id: string;
  event_id?: string;
  redaction_type: string;
  masked_placeholder: string;
  location: string;
  policy_version: string;
  character_count: number;
  timestamp: string;
}

export interface IncidentItem {
  incident_id: string;
  run_id: string;
  title: string;
  summary: string;
  severity: string;
  resolved: boolean;
  resolution_notes?: string;
  timestamp: string;
}

export interface ToolInventoryItem {
  name: string;
  source: string;
  call_count: number;
  avg_duration_ms: number;
}
