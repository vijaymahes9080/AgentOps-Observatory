import React, { useState } from 'react';
import { ShieldAlert, AlertCircle, ArrowRight, Lightbulb } from 'lucide-react';
import { PolicyViolation } from '../types';

interface PolicyViolationsPageProps {
  violations: PolicyViolation[];
  onSelectRun: (runId: string) => void;
}

export const PolicyViolationsPage: React.FC<PolicyViolationsPageProps> = ({ violations, onSelectRun }) => {
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const filtered = violations.filter((v) => 
    severityFilter === 'all' || v.severity.toLowerCase() === severityFilter.toLowerCase()
  );

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem' }}>Guardrails & Policy Violation Triage</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Real-time enforcement against prompt injection, destructive actions, sensitive paths, and unknown tools.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Severity:</span>
          {['all', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
            <button
              key={sev}
              type="button"
              className={`btn ${severityFilter === sev ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
              onClick={() => setSeverityFilter(sev)}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filtered.map((v) => (
          <div key={v.violation_id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldAlert size={16} color={v.severity === 'CRITICAL' ? 'var(--accent-rose)' : 'var(--accent-amber)'} />
                <h3 style={{ fontSize: '0.95rem' }}>{v.rule_name}</h3>
                <span className="font-mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  ({v.rule_id})
                </span>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className={`badge ${v.severity === 'CRITICAL' ? 'badge-critical' : 'badge-error'}`}>
                  {v.severity}
                </span>
                <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                  Confidence: {(v.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Evidence Block */}
            <div style={{
              background: 'rgba(244, 63, 94, 0.06)',
              border: '1px solid rgba(244, 63, 94, 0.2)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.65rem 0.85rem',
              fontSize: '0.82rem',
              color: '#fecdd3'
            }}>
              <strong>Evidence:</strong> {v.evidence}
            </div>

            {/* Remediation Block */}
            <div style={{
              background: 'rgba(56, 189, 248, 0.05)',
              border: '1px solid rgba(56, 189, 248, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.65rem 0.85rem',
              fontSize: '0.82rem',
              color: '#bae6fd',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Lightbulb size={16} color="var(--accent-cyan)" />
              <div>
                <strong>Recommended Remediation:</strong> {v.remediation}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>Correlated Run: <strong className="font-mono" style={{ color: 'var(--accent-cyan)' }}>{v.run_id}</strong></span>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: '0.75rem', padding: '0.2rem 0.55rem' }}
                onClick={() => onSelectRun(v.run_id)}
              >
                Inspect Run Timeline <ArrowRight size={12} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
