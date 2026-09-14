import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, ArrowRight } from 'lucide-react';
import { IncidentItem } from '../types';

interface IncidentsPageProps {
  incidents: IncidentItem[];
  onSelectRun: (runId: string) => void;
}

export const IncidentsPage: React.FC<IncidentsPageProps> = ({ incidents, onSelectRun }) => {
  const [resolvedIds, setResolvedIds] = useState<Set<string>>(new Set());

  const handleToggleResolve = (id: string) => {
    setResolvedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem' }}>Security & Operational Incidents</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          High-severity policy breaches and critical agent exceptions aggregated into actionable triage tickets.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {incidents.map((inc) => {
          const isResolved = inc.resolved || resolvedIds.has(inc.incident_id);
          return (
            <div
              key={inc.incident_id}
              className="glass-card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
                borderLeft: `4px solid ${
                  isResolved ? 'var(--accent-emerald)' : inc.severity === 'CRITICAL' ? 'var(--accent-rose)' : 'var(--accent-amber)'
                }`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                    {inc.incident_id}
                  </span>
                  <h3 style={{ fontSize: '1rem' }}>{inc.title}</h3>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className={`badge ${inc.severity === 'CRITICAL' ? 'badge-critical' : 'badge-error'}`}>
                    {inc.severity}
                  </span>
                  <span className={`badge ${isResolved ? 'badge-success' : 'badge-partial'}`}>
                    {isResolved ? 'RESOLVED' : 'OPEN'}
                  </span>
                </div>
              </div>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {inc.summary}
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span>Run Correlation: <strong className="font-mono" style={{ color: 'var(--text-primary)' }}>{inc.run_id}</strong></span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                    onClick={() => onSelectRun(inc.run_id)}
                  >
                    Investigate Trace <ArrowRight size={12} />
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                    onClick={() => handleToggleResolve(inc.incident_id)}
                  >
                    {isResolved ? 'Re-open' : 'Mark Resolved'}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
