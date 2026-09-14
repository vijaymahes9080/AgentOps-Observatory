import {
  AgentRunSummary,
  IncidentItem,
  MetricsOverview,
  PolicyViolation,
  RedactionAuditItem,
  RunDetail,
  ToolInventoryItem,
  TraceGraphData
} from '../types';

export const MOCK_METRICS: MetricsOverview = {
  total_runs: 142,
  open_incidents: 2,
  total_policy_violations: 6,
  total_redactions: 54,
  total_tokens: 384500,
  total_cost_usd: 1.482,
  total_energy_kwh: 0.1424,
  total_carbon_gco2eq: 55.62,
  compliance_rate_percent: 97.4
};

export const MOCK_RUNS: AgentRunSummary[] = [
  {
    run_id: 'run-prod-8841a',
    agent_name: 'CustomerSupportSupervisor',
    goal: 'Triage customer billing ticket, query Postgres ledger, and summarize resolution',
    status: 'COMPLETED',
    is_partial: false,
    missing_reasons: [],
    total_events: 8,
    total_duration_ms: 1840,
    total_tokens: 4250,
    total_cost_usd: 0.0184,
    total_energy_kwh: 0.0018,
    total_carbon_gco2eq: 0.72,
    policy_violation_count: 0,
    redaction_count: 3,
    created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString()
  },
  {
    run_id: 'run-sec-9920b',
    agent_name: 'DevOpsAutoRemediator',
    goal: 'Analyze Kubernetes pod restart crash loop and propose cluster patch',
    status: 'FAILED',
    is_partial: false,
    missing_reasons: [],
    total_events: 11,
    total_duration_ms: 3210,
    total_tokens: 8940,
    total_cost_usd: 0.0412,
    total_energy_kwh: 0.0039,
    total_carbon_gco2eq: 1.54,
    policy_violation_count: 2,
    redaction_count: 8,
    created_at: new Date(Date.now() - 1000 * 60 * 18).toISOString()
  },
  {
    run_id: 'run-rag-3310c',
    agent_name: 'FinancialDocAnalyst',
    goal: 'Execute hybrid vector search over SEC 10-K filings and generate balance sheet summary',
    status: 'COMPLETED',
    is_partial: false,
    missing_reasons: [],
    total_events: 6,
    total_duration_ms: 980,
    total_tokens: 2890,
    total_cost_usd: 0.0125,
    total_energy_kwh: 0.0011,
    total_carbon_gco2eq: 0.43,
    policy_violation_count: 0,
    redaction_count: 1,
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString()
  },
  {
    run_id: 'run-mcp-4402d',
    agent_name: 'CodeRefactorMCPWorker',
    goal: 'Invoke MCP filesystem tool to refactor legacy authentication middleware',
    status: 'RUNNING',
    is_partial: false,
    missing_reasons: [],
    total_events: 5,
    total_duration_ms: 1420,
    total_tokens: 3500,
    total_cost_usd: 0.0152,
    total_energy_kwh: 0.0014,
    total_carbon_gco2eq: 0.58,
    policy_violation_count: 1,
    redaction_count: 2,
    created_at: new Date(Date.now() - 1000 * 60 * 2).toISOString()
  },
  {
    run_id: 'run-n8n-5511e',
    agent_name: 'HubSpotWebhookPipeline',
    goal: 'Trigger n8n workflow for incoming lead enrichment via verified HMAC webhook',
    status: 'COMPLETED',
    is_partial: false,
    missing_reasons: [],
    total_events: 4,
    total_duration_ms: 720,
    total_tokens: 1600,
    total_cost_usd: 0.0071,
    total_energy_kwh: 0.0007,
    total_carbon_gco2eq: 0.28,
    policy_violation_count: 0,
    redaction_count: 0,
    created_at: new Date(Date.now() - 1000 * 60 * 80).toISOString()
  }
];

export const MOCK_RUN_DETAIL: Record<string, RunDetail> = {
  'run-prod-8841a': {
    ...MOCK_RUNS[0],
    missing_telemetry_reasons: [],
    events: [
      {
        event_id: 'evt-8841a-01',
        event_type: 'AGENT_START',
        source: 'agent_sdk',
        actor: 'CustomerSupportSupervisor',
        name: 'Supervisor Task Initiation',
        status: 'SUCCESS',
        duration_ms: 45,
        payload: { task: 'Triage ticket #49281', customer_id: 'cust_9921' },
        current_hash: '9a4f2e18bc73841a55cd91e8432bca609472e3a1f49618bfae34510bc87293e1',
        prev_hash: '0000000000000000000000000000000000000000000000000000000000000000',
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString()
      },
      {
        event_id: 'evt-8841a-02',
        parent_id: 'evt-8841a-01',
        event_type: 'MODEL_CALL',
        source: 'openai_adapter',
        actor: 'CustomerSupportSupervisor',
        name: 'Intent Classification (GPT-4o)',
        status: 'SUCCESS',
        duration_ms: 620,
        payload: {
          model: 'gpt-4o',
          tokens_prompt: 420,
          tokens_completion: 120,
          temperature: 0.2
        },
        current_hash: 'a71e22394cba819283f65e219ba3884b2c892bfeaa99381741289cf29188e4a9',
        prev_hash: '9a4f2e18bc73841a55cd91e8432bca609472e3a1f49618bfae34510bc87293e1',
        timestamp: new Date(Date.now() - 1000 * 60 * 5 + 50).toISOString()
      },
      {
        event_id: 'evt-8841a-03',
        parent_id: 'evt-8841a-02',
        event_type: 'TOOL_CALL',
        source: 'mcp_postgres',
        actor: 'CustomerSupportSupervisor',
        name: 'tools/call: query_invoice_status',
        status: 'SUCCESS',
        duration_ms: 280,
        payload: {
          tool_name: 'query_invoice_status',
          server: 'mcp-postgres-prod',
          masked_args: { customer_email: '[REDACTED:EMAIL]', invoice_id: 'inv_4920' }
        },
        current_hash: '3f928e182390abff71829e84716294a81726354891a27e8172948bcda81923e8',
        prev_hash: 'a71e22394cba819283f65e219ba3884b2c892bfeaa99381741289cf29188e4a9',
        timestamp: new Date(Date.now() - 1000 * 60 * 5 + 680).toISOString()
      },
      {
        event_id: 'evt-8841a-04',
        parent_id: 'evt-8841a-01',
        event_type: 'MODEL_CALL',
        source: 'openai_adapter',
        actor: 'CustomerSupportSupervisor',
        name: 'Customer Response Synthesis',
        status: 'SUCCESS',
        duration_ms: 810,
        payload: {
          model: 'gpt-4o',
          tokens_prompt: 1850,
          tokens_completion: 460,
          temperature: 0.3
        },
        current_hash: '882c91823ab49817e17281923749812739182739182739182739182739182739',
        prev_hash: '3f928e182390abff71829e84716294a81726354891a27e8172948bcda81923e8',
        timestamp: new Date(Date.now() - 1000 * 60 * 5 + 980).toISOString()
      },
      {
        event_id: 'evt-8841a-05',
        parent_id: 'evt-8841a-01',
        event_type: 'AGENT_END',
        source: 'agent_sdk',
        actor: 'CustomerSupportSupervisor',
        name: 'Supervisor Task Completion',
        status: 'SUCCESS',
        duration_ms: 35,
        payload: { status: 'COMPLETED', response_delivered: true },
        current_hash: 'bb18293749182739182739182739182739182739182739182739182739182739',
        prev_hash: '882c91823ab49817e17281923749812739182739182739182739182739182739',
        timestamp: new Date(Date.now() - 1000 * 60 * 5 + 1800).toISOString()
      }
    ]
  }
};

export const MOCK_TRACE_GRAPH: Record<string, TraceGraphData> = {
  'run-prod-8841a': {
    run_id: 'run-prod-8841a',
    root_nodes: ['evt-8841a-01'],
    nodes: {
      'evt-8841a-01': {
        id: 'evt-8841a-01',
        event_type: 'AGENT_START',
        name: 'Supervisor Task Initiation',
        status: 'SUCCESS',
        duration_ms: 45,
        start_time: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        offset_ms: 0,
        children: ['evt-8841a-02', 'evt-8841a-04', 'evt-8841a-05'],
        has_error: false,
        is_partial_orphan: false
      },
      'evt-8841a-02': {
        id: 'evt-8841a-02',
        parent_id: 'evt-8841a-01',
        event_type: 'MODEL_CALL',
        name: 'Intent Classification (GPT-4o)',
        status: 'SUCCESS',
        duration_ms: 620,
        start_time: new Date(Date.now() - 1000 * 60 * 5 + 50).toISOString(),
        offset_ms: 50,
        children: ['evt-8841a-03'],
        has_error: false,
        is_partial_orphan: false
      },
      'evt-8841a-03': {
        id: 'evt-8841a-03',
        parent_id: 'evt-8841a-02',
        event_type: 'TOOL_CALL',
        name: 'tools/call: query_invoice_status',
        status: 'SUCCESS',
        duration_ms: 280,
        start_time: new Date(Date.now() - 1000 * 60 * 5 + 680).toISOString(),
        offset_ms: 680,
        children: [],
        has_error: false,
        is_partial_orphan: false
      },
      'evt-8841a-04': {
        id: 'evt-8841a-04',
        parent_id: 'evt-8841a-01',
        event_type: 'MODEL_CALL',
        name: 'Customer Response Synthesis',
        status: 'SUCCESS',
        duration_ms: 810,
        start_time: new Date(Date.now() - 1000 * 60 * 5 + 980).toISOString(),
        offset_ms: 980,
        children: [],
        has_error: false,
        is_partial_orphan: false
      },
      'evt-8841a-05': {
        id: 'evt-8841a-05',
        parent_id: 'evt-8841a-01',
        event_type: 'AGENT_END',
        name: 'Supervisor Task Completion',
        status: 'SUCCESS',
        duration_ms: 35,
        start_time: new Date(Date.now() - 1000 * 60 * 5 + 1800).toISOString(),
        offset_ms: 1800,
        children: [],
        has_error: false,
        is_partial_orphan: false
      }
    },
    edges: [
      { source: 'evt-8841a-01', target: 'evt-8841a-02', relation: 'spawns' },
      { source: 'evt-8841a-02', target: 'evt-8841a-03', relation: 'invokes' },
      { source: 'evt-8841a-01', target: 'evt-8841a-04', relation: 'spawns' },
      { source: 'evt-8841a-01', target: 'evt-8841a-05', relation: 'completes' }
    ],
    timeline: [
      {
        event_id: 'evt-8841a-01',
        name: 'Supervisor Task Initiation',
        type: 'AGENT_START',
        status: 'SUCCESS',
        offset_ms: 0,
        duration_ms: 45,
        has_error: false,
        is_orphan: false
      },
      {
        event_id: 'evt-8841a-02',
        name: 'Intent Classification (GPT-4o)',
        type: 'MODEL_CALL',
        status: 'SUCCESS',
        offset_ms: 50,
        duration_ms: 620,
        has_error: false,
        is_orphan: false,
        parent_id: 'evt-8841a-01'
      },
      {
        event_id: 'evt-8841a-03',
        name: 'tools/call: query_invoice_status',
        type: 'TOOL_CALL',
        status: 'SUCCESS',
        offset_ms: 680,
        duration_ms: 280,
        has_error: false,
        is_orphan: false,
        parent_id: 'evt-8841a-02'
      },
      {
        event_id: 'evt-8841a-04',
        name: 'Customer Response Synthesis',
        type: 'MODEL_CALL',
        status: 'SUCCESS',
        offset_ms: 980,
        duration_ms: 810,
        has_error: false,
        is_orphan: false,
        parent_id: 'evt-8841a-01'
      },
      {
        event_id: 'evt-8841a-05',
        name: 'Supervisor Task Completion',
        type: 'AGENT_END',
        status: 'SUCCESS',
        offset_ms: 1800,
        duration_ms: 35,
        has_error: false,
        is_orphan: false,
        parent_id: 'evt-8841a-01'
      }
    ],
    total_duration_ms: 1840,
    is_partial: false,
    missing_telemetry_warnings: [],
    failed_node_ids: []
  }
};

export const MOCK_POLICY_VIOLATIONS: PolicyViolation[] = [
  {
    violation_id: 'viol-9921',
    run_id: 'run-sec-9920b',
    event_id: 'evt-9920b-04',
    rule_id: 'SEC-004-DESTRUCTIVE-CMD',
    rule_name: 'Destructive Shell Command Execution',
    severity: 'CRITICAL',
    evidence: 'Attempted command: `rm -rf /var/lib/kubelet/*` on host container',
    remediation: 'Command blocked deterministically by observatory sandbox policy engine.',
    confidence: 1.0,
    timestamp: new Date(Date.now() - 1000 * 60 * 17).toISOString()
  },
  {
    violation_id: 'viol-9922',
    run_id: 'run-sec-9920b',
    event_id: 'evt-9920b-07',
    rule_id: 'SEC-001-UNAUTHORIZED-TOOL',
    rule_name: 'Unauthorized Tool Invocation',
    severity: 'HIGH',
    evidence: 'Agent invoked tool `export_root_secrets` not present in verified RBAC manifest.',
    remediation: 'Tool invocation quarantined and reported to security audit log.',
    confidence: 1.0,
    timestamp: new Date(Date.now() - 1000 * 60 * 16).toISOString()
  },
  {
    violation_id: 'viol-4403',
    run_id: 'run-mcp-4402d',
    event_id: 'evt-4402d-02',
    rule_id: 'SEC-008-UNKNOWN-MCP-SERVER',
    rule_name: 'Unverified MCP Server Registration',
    severity: 'MEDIUM',
    evidence: 'MCP tool requested from unregistered socket `unix:///tmp/unverified-mcp.sock`',
    remediation: 'Verify server public key and register in mcp_servers.json configuration.',
    confidence: 0.95,
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString()
  }
];

export const MOCK_INCIDENTS: IncidentItem[] = [
  {
    incident_id: 'inc-3011',
    run_id: 'run-sec-9920b',
    title: 'Repeated Command Injection Attempt in Container',
    summary: 'Agent triggered 2 critical policy violations attempting root deletion and unauthorized tool invocations.',
    severity: 'CRITICAL',
    resolved: false,
    timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString()
  },
  {
    incident_id: 'inc-3012',
    run_id: 'run-mcp-4402d',
    title: 'Unverified Model Context Protocol Server Call',
    summary: 'Agent requested filesystem write through unverified third-party MCP daemon.',
    severity: 'MEDIUM',
    resolved: false,
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString()
  }
];

export const MOCK_REDACTIONS: RedactionAuditItem[] = [
  {
    audit_id: 'red-01',
    run_id: 'run-sec-9920b',
    event_id: 'evt-9920b-02',
    redaction_type: 'AWS_ACCESS_KEY',
    masked_placeholder: '[REDACTED:AWS_ACCESS_KEY]',
    location: 'payload.env.AWS_SECRET_ACCESS_KEY',
    policy_version: 'v2.1',
    character_count: 40,
    timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString()
  },
  {
    audit_id: 'red-02',
    run_id: 'run-prod-8841a',
    event_id: 'evt-8841a-03',
    redaction_type: 'EMAIL_ADDRESS',
    masked_placeholder: '[REDACTED:EMAIL]',
    location: 'payload.masked_args.customer_email',
    policy_version: 'v2.1',
    character_count: 24,
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString()
  },
  {
    audit_id: 'red-03',
    run_id: 'run-rag-3310c',
    event_id: 'evt-3310c-01',
    redaction_type: 'OPENAI_API_KEY',
    masked_placeholder: '[REDACTED:OPENAI_API_KEY]',
    location: 'headers.authorization',
    policy_version: 'v2.1',
    character_count: 51,
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString()
  },
  {
    audit_id: 'red-04',
    run_id: 'run-sec-9920b',
    event_id: 'evt-9920b-05',
    redaction_type: 'CREDIT_CARD',
    masked_placeholder: '[REDACTED:CREDIT_CARD]',
    location: 'payload.transaction.card_number',
    policy_version: 'v2.1',
    character_count: 16,
    timestamp: new Date(Date.now() - 1000 * 60 * 16).toISOString()
  }
];

export const MOCK_TOOLS: ToolInventoryItem[] = [
  {
    name: 'mcp::postgres::query_invoice_status',
    source: 'MCP Server (PostgreSQL)',
    call_count: 342,
    avg_duration_ms: 215
  },
  {
    name: 'mcp::filesystem::read_source_file',
    source: 'MCP Server (Filesystem)',
    call_count: 184,
    avg_duration_ms: 42
  },
  {
    name: 'n8n::webhook::lead_enrichment',
    source: 'n8n Automation',
    call_count: 128,
    avg_duration_ms: 680
  },
  {
    name: 'agentops::vector_search::hybrid_query',
    source: 'RAG Retriever',
    call_count: 512,
    avg_duration_ms: 145
  },
  {
    name: 'agentops::bash::sandboxed_exec',
    source: 'Sandbox Subprocess',
    call_count: 96,
    avg_duration_ms: 310
  }
];
