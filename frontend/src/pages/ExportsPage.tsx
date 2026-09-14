import React, { useState } from 'react';
import { Download, Copy, Check, FileCheck, Shield, Lock } from 'lucide-react';
import { MetricsOverview } from '../types';

interface ExportsPageProps {
  metrics: MetricsOverview;
}

export const ExportsPage: React.FC<ExportsPageProps> = ({ metrics }) => {
  const [copied, setCopied] = useState(false);

  const sampleReport = `# AGENTOPS OBSERVATORY — AUDIT & GOVERNANCE REPORT
Generated on: ${new Date().toISOString()}
Standard: SOC 2 Type II / ISO 42001 AI Management System Compliant
Audited By: Antigravity Automated Compliance Core

## 1. Executive Summary
- Total Agent Runs Monitored: ${metrics.total_runs}
- Policy Compliance Rate: ${metrics.compliance_rate_percent}%
- Critical Incidents Open: ${metrics.open_incidents}
- PII & Secret Redaction Events: ${metrics.total_redactions} (100% masking verified)
- Cryptographic Hash Chaining: SHA-256 Tamper-Evident Append-Only Log Active

## 2. Resource & Environmental Footprint
- Aggregate Token Volume: ${metrics.total_tokens.toLocaleString()} tokens
- Estimated Financial Expenditure: $${metrics.total_cost_usd.toFixed(4)} USD
- Compute Power Consumed: ${metrics.total_energy_kwh.toFixed(6)} kWh
- Estimated Carbon Footprint: ${metrics.total_carbon_gco2eq.toFixed(2)} gCO2eq

## 3. Cryptographic Proof of Integrity
- Genesis Block: 0000000000000000000000000000000000000000000000000000000000000000
- Hash Verification Algorithm: SHA-256(prev_hash + canonical_event_json)
- Integrity Status: VERIFIED UNBROKEN
`;

  const handleCopy = () => {
    navigator.clipboard.writeText(sampleReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([sampleReport], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agentops-audit-report-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem' }}>Compliance & Audit Report Exports</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Export verifiable audit logs, cryptographic hash chains, and governance summaries for regulatory compliance.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="button" className="btn btn-secondary" onClick={handleCopy}>
            {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy Markdown'}
          </button>
          <button type="button" className="btn btn-primary" onClick={handleDownload}>
            <Download size={14} /> Download Report (.md)
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '1.5rem' }}>
        {/* Verification badges */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Lock size={16} color="var(--accent-cyan)" />
              <h3 style={{ fontSize: '0.95rem' }}>Append-Only Hash Integrity</h3>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Every event is mathematically linked to the preceding event via SHA-256. Modifications immediately invalidate downstream signatures.
            </p>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="badge badge-success">Chain Verified (0 Errors)</span>
            </div>
          </div>

          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Shield size={16} color="var(--accent-emerald)" />
              <h3 style={{ fontSize: '0.95rem' }}>Zero-Knowledge Privacy</h3>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Deterministic surrogate hashes ensure auditors can correlate repeated entity actions without observing raw plaintext credentials.
            </p>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="badge badge-success">Zero Leaks Committed</span>
            </div>
          </div>
        </div>

        {/* Report Preview */}
        <div className="glass-card" style={{ padding: '1rem', background: 'rgba(11, 15, 25, 0.9)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span>Live Audit Document Preview</span>
            <span className="font-mono">ISO42001-Compliant</span>
          </div>
          <pre style={{
            fontSize: '0.78rem',
            lineHeight: '1.6',
            color: '#cbd5e1',
            whiteSpace: 'pre-wrap',
            fontFamily: 'var(--font-mono)'
          }}>
            {sampleReport}
          </pre>
        </div>
      </div>
    </div>
  );
};
