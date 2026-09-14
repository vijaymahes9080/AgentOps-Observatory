# Framework Integration Guides

Easily connect your AI agents and workflows to AgentOps Observatory.

---

## 1. LangChain Integration

```python
from langchain_openai import ChatOpenAI
from collectors.agent.frameworks import AgentOpsLangChainCallback

handler = AgentOpsLangChainCallback(run_id="run-customer-support-01")
llm = ChatOpenAI(model="gpt-4o", callbacks=[handler])

response = llm.invoke("Summarize system logs")
```

---

## 2. CrewAI Integration

```python
from crewai import Agent, Task, Crew
from collectors.agent.sdk import AgentObserver

observer = AgentObserver(run_id="crew-market-research")

@observer.observe_tool(tool_name="web_search")
def search(query: str):
    return f"Results for {query}"
```

---

## 3. AutoGen Swarm Integration

```python
from collectors.agent.frameworks import AgentOpsAutoGenHook

hook = AgentOpsAutoGenHook(run_id="autogen-code-review")

# Wire into AutoGen group chat agent
hook.on_message_sent(
    sender_name="CoderAgent",
    recipient_name="ReviewerAgent",
    message={"code": "def process(): return True"}
)
```

---

## 4. n8n Workflow Webhook Integration

1. In n8n, create an **HTTP Request** or **Webhook** node.
2. Target URL: `http://<agentops-host>:8000/api/v1/events`
3. Method: `POST`
4. Headers:
   - `Content-Type: application/json`
   - `X-AgentOps-API-Key: agy-adm-prod-live-key-9999`
5. Payload:
```json
{
  "run_id": "n8n-{{ $execution.id }}",
  "source": "n8n",
  "workflow_id": "{{ $workflow.id }}",
  "workflow_name": "{{ $workflow.name }}",
  "execution_id": "{{ $execution.id }}",
  "node_name": "{{ $node.name }}",
  "node_type": "{{ $node.type }}",
  "status": "success",
  "duration_ms": 120
}
```
