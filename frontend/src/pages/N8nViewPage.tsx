import React from 'react';
import { Workflow, CheckCircle, AlertTriangle, ShieldCheck, Clock } from 'lucide-react';

export const N8nViewPage: React.FC = () => {
  const workflows = [
    {
      workflowId: 'wf-slack-notifier',
      name: 'Agent Incident Slack Dispatcher',
      executionId: 'exec-84920',
      triggerNode: 'Webhook Trigger',
      webhookVerified: true,
      nodesExecuted: 4,
      durationMs: 145,
      status: 'Success',
      lastRun: '10 minutes ago'
    },
    {
      workflowId: 'wf-lead-enrichment',
      name: 'AgentOps Lead Intelligence Sync',
      executionId: 'exec-84921',
      triggerNode: 'Webhook Trigger',
      webhookVerified: true,
      nodesExecuted: 7,
      durationMs: 820,
      status: 'Success',
      lastRun: '22 minutes ago'
    },
    {
      workflowId: 'wf-auto-remediation',
      name: 'Untrusted Command Quarantine Hook',
      executionId: 'exec-84922',
      triggerNode: 'Agent Policy Event',
      webhookVerified: true,
      nodesExecuted: 3,
      durationMs: 65,
      status: 'Success',
      lastRun: '1 hour ago'
    }
  ];

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem' }}>n8n Workflow Automation Telemetry</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Trace orchestration pipelines, webhook HMAC signature verifications, and downstream automation node latencies.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
        {workflows.map((w) => (
          <div key={w.workflowId} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Workflow size={18} color="var(--accent-purple)" />
                <h3 style={{ fontSize: '1rem', fontFamily: 'var(--font-display)' }}>{w.name}</h3>
              </div>
              <span className="badge badge-success">{w.status}</span>
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div>Workflow ID: <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>{w.workflowId}</span></div>
              <div>Execution ID: <span className="font-mono">{w.executionId}</span></div>
              <div>Trigger: {w.triggerNode}</div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '0.25rem' }}>
              <span>Nodes Executed: <strong>{w.nodesExecuted}</strong></span>
              <span>Latency: <strong>{w.durationMs} ms</strong></span>
            </div>

            <div style={{
              marginTop: 'auto',
              paddingTop: '0.5rem',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.75rem'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--accent-emerald)' }}>
                <ShieldCheck size={14} /> HMAC Webhook Signature: <strong>Verified</strong>
              </span>
              <span style={{ color: 'var(--text-muted)' }}>{w.lastRun}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
