import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { LiveRunsPage } from './pages/LiveRunsPage';
import { RunDetailPage } from './pages/RunDetailPage';
import { ToolInventoryPage } from './pages/ToolInventoryPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { PolicyViolationsPage } from './pages/PolicyViolationsPage';
import { RedactionEventsPage } from './pages/RedactionEventsPage';
import { CostEnergyPage } from './pages/CostEnergyPage';
import { N8nViewPage } from './pages/N8nViewPage';
import { McpViewPage } from './pages/McpViewPage';
import { ExportsPage } from './pages/ExportsPage';

import {
  AgentRunSummary,
  IncidentItem,
  MetricsOverview,
  PageView,
  PolicyViolation,
  RedactionAuditItem,
  ToolInventoryItem
} from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<PageView>('overview');
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [metrics, setMetrics] = useState<MetricsOverview>({
    total_runs: 0,
    open_incidents: 0,
    total_policy_violations: 0,
    total_redactions: 0,
    total_tokens: 0,
    total_cost_usd: 0,
    total_energy_kwh: 0,
    total_carbon_gco2eq: 0,
    compliance_rate_percent: 100
  });

  const [runs, setRuns] = useState<AgentRunSummary[]>([]);
  const [violations, setViolations] = useState<PolicyViolation[]>([]);
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [redactions, setRedactions] = useState<RedactionAuditItem[]>([]);
  const [tools, setTools] = useState<ToolInventoryItem[]>([]);

  const loadData = useCallback(async () => {
    const [m, r, v, inc, red, t] = await Promise.all([
      api.getOverview(),
      api.getRuns(),
      api.getPolicyViolations(),
      api.getIncidents(),
      api.getRedactions(),
      api.getToolInventory()
    ]);
    setMetrics(m);
    setRuns(r);
    setViolations(v);
    setIncidents(inc);
    setRedactions(red);
    setTools(t);
  }, []);

  useEffect(() => {
    loadData();
    // Poll every 10 seconds for real-time live telemetry
    const timer = setInterval(loadData, 10000);
    return () => clearInterval(timer);
  }, [loadData]);

  // Keyboard navigation shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === 'Escape') {
        setCurrentView('overview');
        setSelectedRunId(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectRun = (runId: string) => {
    setSelectedRunId(runId);
    setCurrentView('run_detail');
  };

  const handleBackToRuns = () => {
    setSelectedRunId(null);
    setCurrentView('live_runs');
  };

  return (
    <div className="app-container">
      <Sidebar
        currentView={currentView}
        onSelectView={(v) => {
          setSelectedRunId(null);
          setCurrentView(v);
        }}
      />

      <main className="main-content">
        <Header
          currentView={currentView}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onRefresh={loadData}
          selectedRunId={selectedRunId}
        />

        {currentView === 'overview' && (
          <OverviewPage
            metrics={metrics}
            recentRuns={runs}
            recentViolations={violations}
            onSelectRun={handleSelectRun}
            onNavigate={setCurrentView}
          />
        )}

        {currentView === 'live_runs' && (
          <LiveRunsPage
            runs={runs}
            onSelectRun={handleSelectRun}
          />
        )}

        {currentView === 'run_detail' && selectedRunId && (
          <RunDetailPage
            runId={selectedRunId}
            onBack={handleBackToRuns}
          />
        )}

        {currentView === 'tool_inventory' && (
          <ToolInventoryPage tools={tools} />
        )}

        {currentView === 'incidents' && (
          <IncidentsPage
            incidents={incidents}
            onSelectRun={handleSelectRun}
          />
        )}

        {currentView === 'policy_violations' && (
          <PolicyViolationsPage
            violations={violations}
            onSelectRun={handleSelectRun}
          />
        )}

        {currentView === 'redaction_events' && (
          <RedactionEventsPage redactions={redactions} />
        )}

        {currentView === 'cost_energy' && (
          <CostEnergyPage metrics={metrics} />
        )}

        {currentView === 'mcp_view' && (
          <McpViewPage />
        )}

        {currentView === 'n8n_view' && (
          <N8nViewPage />
        )}

        {currentView === 'exports' && (
          <ExportsPage metrics={metrics} />
        )}
      </main>
    </div>
  );
};

export default App;
