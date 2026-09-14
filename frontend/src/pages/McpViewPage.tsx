import React from 'react';
import { Server, Terminal, CheckCircle2, ShieldCheck, Database, CloudRain, Folder } from 'lucide-react';

export const McpViewPage: React.FC = () => {
  const mcpServers = [
    {
      name: 'mcp-local-filesystem',
      transport: 'stdio',
      endpoint: 'local-process',
      status: 'Connected',
      toolsCount: 4,
      tools: ['read_file', 'view_file', 'list_dir', 'grep_search'],
      governance: 'Strict Path Whitelist'
    },
    {
      name: 'mcp-github',
      transport: 'SSE',
      endpoint: 'https://api.github.com/mcp',
      status: 'Connected',
      toolsCount: 3,
      tools: ['create_issue', 'read_pull_request', 'list_repos'],
      governance: 'OAuth Scoped Token'
    },
    {
      name: 'mcp-database-readonly',
      transport: 'stdio',
      endpoint: 'postgres-proxy:5432',
      status: 'Connected',
      toolsCount: 2,
      tools: ['database_query_readonly', 'explain_query'],
      governance: 'Read-Only Enforced'
    },
    {
      name: 'mcp-weather',
      transport: 'HTTP',
      endpoint: 'https://weather.mcp.internal',
      status: 'Connected',
      toolsCount: 1,
      tools: ['mcp_fetch_weather'],
      governance: 'Public Data'
    },
    {
      name: 'mcp-observatory',
      transport: 'stdio',
      endpoint: 'localhost:8000',
      status: 'Active',
      toolsCount: 3,
      tools: ['ingest_event', 'query_run', 'check_guardrail'],
      governance: 'Self-Telemetry'
    }
  ];

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem' }}>Model Context Protocol (MCP) Registry</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Observed MCP stdio and SSE servers with protocol metadata, capability exposure, and security sandbox policies.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
        {mcpServers.map((s) => (
          <div key={s.name} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Server size={18} color="var(--accent-cyan)" />
                <h3 style={{ fontSize: '1rem', fontFamily: 'var(--font-display)' }}>{s.name}</h3>
              </div>
              <span className="badge badge-success">{s.status}</span>
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div>Transport: <strong className="font-mono" style={{ color: 'var(--text-secondary)' }}>{s.transport}</strong></div>
              <div>Endpoint: <span className="font-mono">{s.endpoint}</span></div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                Exposed Tools ({s.toolsCount}):
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                {s.tools.map((t) => (
                  <span key={t} className="font-mono" style={{
                    fontSize: '0.75rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--accent-emerald)' }}>
              <ShieldCheck size={14} />
              <span>Policy: <strong>{s.governance}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
