/**
 * AgentOps Observatory — TypeScript / Node.js Client SDK
 * Enables Node.js AI agents, LangChain.js, and Vercel AI SDK applications
 * to stream telemetry events directly into AgentOps Observatory.
 */

export interface AgentOpsConfig {
  endpoint?: string;
  apiKey?: string;
  tenantId?: string;
}

export interface IngestPayload {
  run_id: string;
  parent_id?: string;
  source?: 'agent' | 'mcp' | 'n8n' | 'model' | 'rag' | 'system';
  actor?: string;
  tool_or_model_name?: string;
  status?: 'success' | 'error' | 'in_progress' | 'violated' | 'redacted' | 'partial';
  duration_ms?: number;
  sensitivity?: 'public' | 'internal' | 'confidential' | 'restricted';
  attributes?: Record<string, any>;
  [key: string]: any;
}

export class AgentOpsObservatory {
  private endpoint: string;
  private apiKey: string;
  private tenantId: string;

  constructor(config?: AgentOpsConfig) {
    this.endpoint = (config?.endpoint || 'http://localhost:8000/api/v1').replace(/\/$/, '');
    this.apiKey = config?.apiKey || 'agy-ts-sdk-key-live';
    this.tenantId = config?.tenantId || 'default';
  }

  public async recordEvent(event: IngestPayload, idempotencyKey?: string): Promise<any> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-AgentOps-API-Key': this.apiKey,
    };
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const payload = {
      ...event,
      timestamp: new Date().toISOString(),
      provenance: { sdk: 'agentops-node-ts', version: '1.0.0' }
    };

    const response = await fetch(`${this.endpoint}/events`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`AgentOps Ingestion Error: ${response.status} ${await response.text()}`);
    }

    return await response.json();
  }

  public async recordModelCall(params: {
    runId: string;
    modelName: string;
    prompt: string;
    response: string;
    tokens: { prompt: number; completion: number };
    durationMs: number;
    parentId?: string;
  }): Promise<any> {
    return this.recordEvent({
      run_id: params.runId,
      parent_id: params.parentId,
      source: 'model',
      tool_or_model_name: params.modelName,
      model_name: params.modelName,
      prompt_redacted: params.prompt,
      response_redacted: params.response,
      prompt_tokens: params.tokens.prompt,
      completion_tokens: params.tokens.completion,
      total_tokens: params.tokens.prompt + params.tokens.completion,
      duration_ms: params.durationMs,
      status: 'success'
    });
  }
}
