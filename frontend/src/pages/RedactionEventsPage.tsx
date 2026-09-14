import React, { useState } from 'react';
import { EyeOff, ShieldCheck, Lock, FileKey } from 'lucide-react';
import { RedactionAuditItem } from '../types';

interface RedactionEventsPageProps {
  redactions: RedactionAuditItem[];
}

export const RedactionEventsPage: React.FC<RedactionEventsPageProps> = ({ redactions }) => {
  const [filterType, setFilterType] = useState<string>('all');

  const uniqueTypes = Array.from(new Set(redactions.map((r) => r.redaction_type)));

  const filtered = redactions.filter((r) => 
    filterType === 'all' || r.redaction_type === filterType
  );

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem' }}>Deterministic Redaction Audit Trail</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Zero-trust secret masking audit logs. Raw credentials are never stored in disk or logs.
          </p>
        </div>

        {/* Filter Buttons */}
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className={`btn ${filterType === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem' }}
            onClick={() => setFilterType('all')}
          >
            ALL
          </button>
          {uniqueTypes.map((t) => (
            <button
              key={t}
              type="button"
              className={`btn ${filterType === t ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem' }}
              onClick={() => setFilterType(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Audit ID</th>
              <th>Secret / PII Type</th>
              <th>Deterministic Surrogate Placeholder</th>
              <th>Payload Location (JSONPath)</th>
              <th>Length</th>
              <th>Policy Version</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.audit_id}>
                <td className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {r.audit_id.slice(0, 8)}...
                </td>
                <td>
                  <span className="badge badge-info" style={{ gap: '0.25rem' }}>
                    <FileKey size={12} /> {r.redaction_type}
                  </span>
                </td>
                <td className="font-mono" style={{ color: 'var(--accent-purple)', fontSize: '0.8rem', fontWeight: 600 }}>
                  {r.masked_placeholder}
                </td>
                <td className="font-mono" style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  {r.location}
                </td>
                <td style={{ fontSize: '0.8rem' }}>{r.character_count} chars</td>
                <td className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  v{r.policy_version}
                </td>
                <td>
                  <span className="badge badge-success" style={{ gap: '0.25rem' }}>
                    <ShieldCheck size={12} /> Masked
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
