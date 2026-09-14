import React from 'react';
import { Wrench, Server, Zap, CheckCircle2 } from 'lucide-react';
import { ToolInventoryItem } from '../types';

interface ToolInventoryPageProps {
  tools: ToolInventoryItem[];
}

export const ToolInventoryPage: React.FC<ToolInventoryPageProps> = ({ tools }) => {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem' }}>Tool & MCP Capability Inventory</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Comprehensive catalog of tools, MCP server resources, invocation frequencies, and latencies.
        </p>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Tool Name</th>
              <th>Origin Source</th>
              <th>Total Invocations</th>
              <th>Avg Latency</th>
              <th>Governance Status</th>
            </tr>
          </thead>
          <tbody>
            {tools.map((t) => (
              <tr key={t.name}>
                <td style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Wrench size={14} color="var(--accent-cyan)" />
                  <span className="font-mono">{t.name}</span>
                </td>
                <td>
                  <span className="badge badge-info">
                    {t.source.toUpperCase()}
                  </span>
                </td>
                <td style={{ fontWeight: 500 }}>{t.call_count.toLocaleString()} calls</td>
                <td className="font-mono">{t.avg_duration_ms > 0 ? `${t.avg_duration_ms} ms` : '—'}</td>
                <td>
                  <span className="badge badge-success" style={{ gap: '0.25rem' }}>
                    <CheckCircle2 size={12} /> Approved
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
