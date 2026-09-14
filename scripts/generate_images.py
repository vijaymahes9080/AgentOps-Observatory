"""
AgentOps Observatory - High-Resolution Image Generator
Creates production-quality light-theme dashboard mockups, trace graphs,
security audit visualizers, and the official LinkedIn announcement banner (image.png).
"""

from PIL import Image, ImageDraw, ImageFont
import os


def get_font(size: int, bold: bool = False):
    font_names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_dashboard_light(output_path: str):
    width, height = 1600, 900
    img = Image.new("RGBA", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = get_font(28, bold=True)
    font_sub = get_font(15, bold=False)
    font_heading = get_font(20, bold=True)
    font_card_val = get_font(32, bold=True)
    font_card_lbl = get_font(13, bold=True)
    font_table_hdr = get_font(13, bold=True)
    font_text = get_font(14, bold=False)
    font_mono = get_font(13, bold=True)
    font_badge = get_font(11, bold=True)

    # Top Navbar
    draw.rectangle([(0, 0), (width, 70)], fill="#ffffff", outline="#e2e8f0", width=1)
    
    # Logo Box
    draw.rounded_rectangle([(30, 15), (70, 55)], radius=10, fill="#0284c7")
    draw.text((43, 20), "AO", fill="#ffffff", font=get_font(20, bold=True))
    
    # Header text
    draw.text((85, 17), "AGENTOPS OBSERVATORY", fill="#0f172a", font=get_font(18, bold=True))
    draw.text((85, 40), "Enterprise AI Governance & Observability Engine", fill="#64748b", font=font_sub)

    # Live Badge
    draw.rounded_rectangle([(width - 240, 22), (width - 150, 48)], radius=12, fill="#ecfdf5", outline="#10b981", width=1)
    draw.text((width - 220, 28), "LIVE SYNC", fill="#059669", font=font_badge)

    # Admin profile pill
    draw.rounded_rectangle([(width - 135, 20), (width - 30, 50)], radius=15, fill="#f1f5f9", outline="#cbd5e1", width=1)
    draw.text((width - 120, 26), "Vijay Mahes", fill="#1e293b", font=font_text)

    # 4 KPI Cards
    cards = [
        {"title": "COMPLIANCE RATE", "val": "100.0%", "sub": "10/10 Guardrails Active", "col": "#059669", "bg": "#ecfdf5"},
        {"title": "TOTAL AGENT RUNS", "val": "200", "sub": "Zero-Trust Lineage", "col": "#0284c7", "bg": "#f0f9ff"},
        {"title": "SECRETS MASKED", "val": "100%", "sub": "Zero Leaks Committed", "col": "#7c3aed", "bg": "#f5f3ff"},
        {"title": "EST. COST & CARBON", "val": "$0.842", "sub": "32.1 gCO2eq • A+ Green", "col": "#d97706", "bg": "#fffbeb"},
    ]

    card_w = (width - 60 - 3 * 20) // 4
    for i, c in enumerate(cards):
        cx = 30 + i * (card_w + 20)
        cy = 95
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + 120)], radius=12, fill="#ffffff", outline="#e2e8f0", width=1)
        # Accent top bar
        draw.rounded_rectangle([(cx + 1, cy + 1), (cx + card_w - 1, cy + 5)], radius=2, fill=c["col"])
        draw.text((cx + 18, cy + 18), c["title"], fill="#64748b", font=font_card_lbl)
        draw.text((cx + 18, cy + 42), c["val"], fill=c["col"], font=font_card_val)
        draw.text((cx + 18, cy + 90), c["sub"], fill="#94a3b8", font=get_font(12))

    # Main Grid: Left Runs Table (width 60%), Right Guardrail Violations & Redaction (width 40%)
    # Runs Table Container
    tw = 950
    draw.rounded_rectangle([(30, 235), (30 + tw, height - 30)], radius=14, fill="#ffffff", outline="#e2e8f0", width=1)
    draw.text((50, 255), "Live Agent Telemetry Stream", fill="#0f172a", font=font_heading)
    draw.text((50, 285), "Correlated model spans, MCP tool calls, and n8n executions", fill="#64748b", font=font_sub)

    # Table Header Row
    draw.rectangle([(50, 315), (30 + tw - 20, 345)], fill="#f8fafc")
    draw.text((60, 323), "RUN ID", fill="#64748b", font=font_table_hdr)
    draw.text((220, 323), "AGENT IDENTITY", fill="#64748b", font=font_table_hdr)
    draw.text((430, 323), "STATUS", fill="#64748b", font=font_table_hdr)
    draw.text((550, 323), "DURATION", fill="#64748b", font=font_table_hdr)
    draw.text((670, 323), "TOKENS", fill="#64748b", font=font_table_hdr)
    draw.text((790, 323), "INTEGRITY", fill="#64748b", font=font_table_hdr)

    # Sample Run Rows
    sample_runs = [
        ("eval-normal-001", "ResearchTaskAgent", "SUCCESS", "#059669", "#ecfdf5", "1,450 ms", "505", "COMPLETE", "#059669"),
        ("eval-normal-002", "CodingSwarmAgent", "SUCCESS", "#059669", "#ecfdf5", "2,120 ms", "1,240", "COMPLETE", "#059669"),
        ("eval-unauth-004", "UntrustedShellAgent", "VIOLATED", "#e11d48", "#ffe4e6", "250 ms", "0", "BLOCKED", "#e11d48"),
        ("eval-secret-007", "BillingExtractorBot", "SUCCESS", "#059669", "#ecfdf5", "500 ms", "150", "MASKED", "#7c3aed"),
        ("eval-partial-012", "DistributedRAGAgent", "PARTIAL", "#d97706", "#fffbeb", "85 ms", "0", "ORPHAN", "#d97706"),
        ("eval-normal-018", "MCPWeatherService", "SUCCESS", "#059669", "#ecfdf5", "320 ms", "85", "COMPLETE", "#059669"),
        ("eval-inject-003", "ExternalChatUser", "VIOLATED", "#e11d48", "#ffe4e6", "600 ms", "162", "BLOCKED", "#e11d48"),
    ]

    for idx, r in enumerate(sample_runs):
        ry = 360 + idx * 58
        draw.line([(50, ry - 5), (30 + tw - 20, ry - 5)], fill="#f1f5f9", width=1)
        draw.text((60, ry + 12), r[0], fill="#0284c7", font=font_mono)
        draw.text((220, ry + 12), r[1], fill="#1e293b", font=font_text)
        
        # Status pill
        draw.rounded_rectangle([(430, ry + 8), (510, ry + 32)], radius=12, fill=r[4], outline=r[3], width=1)
        draw.text((442, ry + 13), r[2], fill=r[3], font=font_badge)

        draw.text((550, ry + 12), r[5], fill="#475569", font=font_text)
        draw.text((670, ry + 12), r[6], fill="#475569", font=font_text)
        draw.text((790, ry + 12), r[7], fill=r[8], font=font_badge)

    # Right Column: Security Guardrails & Redaction Feed
    rx = 30 + tw + 20
    rw = width - rx - 30
    draw.rounded_rectangle([(rx, 235), (rx + rw, height - 30)], radius=14, fill="#ffffff", outline="#e2e8f0", width=1)
    draw.text((rx + 20, 255), "Security & Privacy Audits", fill="#0f172a", font=font_heading)
    draw.text((rx + 20, 285), "Deterministic masking & policy guardrails", fill="#64748b", font=font_sub)

    right_items = [
        ("PROMPT INJECTION PREVENTED", "Jailbreak signature 'ignore previous instructions' halted.", "#e11d48", "#ffe4e6"),
        ("SEEDED API KEY MASKED", "Surrogate [REDACTED_OPENAI_KEY_3c4d] recorded without leak.", "#7c3aed", "#f5f3ff"),
        ("DESTRUCTIVE ACTION BLOCKED", "Prevented 'rm -rf /var/log' before execution.", "#e11d48", "#ffe4e6"),
        ("HMAC SIGNATURE VERIFIED", "n8n webhook execution payload authenticated cryptographically.", "#059669", "#ecfdf5"),
        ("APPEND-ONLY CHAIN VERIFIED", "SHA-256 block hash integrity validated across 520 events.", "#0284c7", "#f0f9ff")
    ]

    for idx, item in enumerate(right_items):
        iy = 320 + idx * 95
        draw.rounded_rectangle([(rx + 20, iy), (rx + rw - 20, iy + 80)], radius=10, fill=item[3], outline=item[2], width=1)
        draw.text((rx + 35, iy + 14), item[0], fill=item[2], font=font_badge)
        draw.text((rx + 35, iy + 35), item[1], fill="#334155", font=get_font(13))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Created: {output_path}")


def create_trace_dag_light(output_path: str):
    width, height = 1600, 900
    img = Image.new("RGBA", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(img)

    font_title = get_font(26, bold=True)
    font_sub = get_font(15, bold=False)
    font_node_title = get_font(16, bold=True)
    font_mono = get_font(13, bold=True)
    font_text = get_font(14, bold=False)
    font_badge = get_font(12, bold=True)

    # Top Navbar
    draw.rectangle([(0, 0), (width, 70)], fill="#ffffff", outline="#e2e8f0", width=1)
    draw.text((40, 20), "AgentOps Trace DAG & Timeline Inspector", fill="#0f172a", font=font_title)
    draw.text((650, 25), "Run: eval-normal-001 (ResearchTaskAgent)", fill="#0284c7", font=font_mono)

    # Left: Directed Acyclic Graph (DAG) Spans
    draw.rounded_rectangle([(30, 95), (850, height - 30)], radius=14, fill="#ffffff", outline="#e2e8f0", width=1)
    draw.text((50, 115), "Execution Directed Acyclic Graph (DAG)", fill="#0f172a", font=get_font(20, bold=True))
    draw.text((50, 142), "Parent-child hierarchy and model-to-tool invocation linkages", fill="#64748b", font=font_sub)

    nodes = [
        {"name": "ResearchTaskAgent [Root Span]", "type": "Span", "time": "1,450 ms", "stat": "SUCCESS", "col": "#059669", "bg": "#ecfdf5", "x": 60, "y": 180, "w": 420},
        {"name": "GPT-4o [Model Call]", "type": "ModelCall", "time": "780 ms", "stat": "SUCCESS", "col": "#0284c7", "bg": "#f0f9ff", "x": 120, "y": 280, "w": 420},
        {"name": "search_web [Tool Call]", "type": "ToolCall", "time": "320 ms", "stat": "SUCCESS", "col": "#059669", "bg": "#ecfdf5", "x": 180, "y": 380, "w": 420},
        {"name": "mcp_fetch_weather [MCP Tool]", "type": "ToolCall", "time": "145 ms", "stat": "SUCCESS", "col": "#7c3aed", "bg": "#f5f3ff", "x": 180, "y": 480, "w": 420},
        {"name": "calculate_hash [MCP Tool]", "type": "ToolCall", "time": "45 ms", "stat": "SUCCESS", "col": "#059669", "bg": "#ecfdf5", "x": 180, "y": 580, "w": 420},
        {"name": "Task Completion [Span]", "type": "Span", "time": "160 ms", "stat": "COMPLETE", "col": "#059669", "bg": "#ecfdf5", "x": 120, "y": 680, "w": 420},
    ]

    # Draw connecting lines
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i]["x"] + 40, nodes[i]["y"] + 65
        x2, y2 = nodes[i+1]["x"] + 40, nodes[i+1]["y"]
        draw.line([(x1, y1), (x1, y2 - 10), (x2, y2)], fill="#94a3b8", width=2)

    for n in nodes:
        draw.rounded_rectangle([(n["x"], n["y"]), (n["x"] + n["w"], n["y"] + 65)], radius=10, fill=n["bg"], outline=n["col"], width=1)
        draw.text((n["x"] + 15, n["y"] + 12), n["name"], fill="#0f172a", font=font_node_title)
        draw.text((n["x"] + 15, n["y"] + 36), f"{n['type']} • {n['time']}", fill="#64748b", font=font_sub)
        draw.text((n["x"] + n["w"] - 90, n["y"] + 24), n["stat"], fill=n["col"], font=font_badge)

    # Right: Timeline Gantt Latency Bars & Cryptographic Proof
    draw.rounded_rectangle([(875, 95), (width - 30, height - 30)], radius=14, fill="#ffffff", outline="#e2e8f0", width=1)
    draw.text((900, 115), "Relative Latency Timeline & Cryptography", fill="#0f172a", font=get_font(20, bold=True))
    draw.text((900, 142), "Deterministic Gantt offset metrics and tamper-evident SHA-256 chain", fill="#64748b", font=font_sub)

    timeline = [
        {"name": "ResearchTaskAgent", "offset": 0, "len": 650, "col": "#0284c7"},
        {"name": "GPT-4o (Inference)", "offset": 80, "len": 380, "col": "#3b82f6"},
        {"name": "search_web", "offset": 480, "len": 180, "col": "#10b981"},
        {"name": "mcp_fetch_weather", "offset": 670, "len": 90, "col": "#8b5cf6"},
        {"name": "calculate_hash", "offset": 770, "len": 40, "col": "#10b981"},
        {"name": "Output Formatting", "offset": 820, "len": 80, "col": "#06b6d4"},
    ]

    for idx, t in enumerate(timeline):
        ty = 190 + idx * 75
        draw.text((900, ty), t["name"], fill="#1e293b", font=font_node_title)
        # Background track
        draw.rounded_rectangle([(900, ty + 25), (width - 60, ty + 42)], radius=6, fill="#f1f5f9")
        # Offset bar
        bx1 = 900 + int(t["offset"] * 0.6)
        bx2 = bx1 + int(t["len"] * 0.6)
        draw.rounded_rectangle([(bx1, ty + 25), (bx2, ty + 42)], radius=6, fill=t["col"])

    # Cryptographic Chain Box at bottom right
    cy = 660
    draw.rounded_rectangle([(900, cy), (width - 60, height - 55)], radius=10, fill="#f8fafc", outline="#cbd5e1", width=1)
    draw.text((920, cy + 15), "Append-Only Hash Chain Verification", fill="#0f172a", font=font_node_title)
    draw.text((920, cy + 42), "Prev Hash:  d94c7825a70cb10caeb389dadee26b17bc593ea13c1faa27a053d605e6b1e88c", fill="#64748b", font=font_mono)
    draw.text((920, cy + 68), "Curr Hash:  64217c747bc7f2afb2d8619185839d9e1b009b871ba3775023a8f0bf1afbabcf", fill="#0284c7", font=font_mono)
    draw.text((920, cy + 98), "Integrity Status:  VERIFIED UNBROKEN (0 Errors)", fill="#059669", font=font_badge)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Created: {output_path}")


def create_linkedin_banner(output_path: str):
    width, height = 1200, 630
    img = Image.new("RGBA", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    # Elegant subtle gradient wash
    for y in range(height):
        r = int(255 - (y / height) * 8)
        g = int(255 - (y / height) * 4)
        b = int(255)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    font_badge = get_font(13, bold=True)
    font_hero = get_font(46, bold=True)
    font_sub = get_font(21, bold=False)
    font_h3 = get_font(17, bold=True)
    font_body = get_font(14, bold=False)
    font_metric_val = get_font(28, bold=True)
    font_metric_lbl = get_font(12, bold=True)

    # Top Brand Ribbon
    draw.rectangle([(0, 0), (width, 8)], fill="#0284c7")
    
    # Header Category Badge
    draw.rounded_rectangle([(60, 40), (320, 72)], radius=16, fill="#f0f9ff", outline="#0284c7", width=1)
    draw.text((78, 48), "OPEN-SOURCE AI PLATFORM", fill="#0284c7", font=font_badge)

    draw.rounded_rectangle([(335, 40), (510, 72)], radius=16, fill="#ecfdf5", outline="#10b981", width=1)
    draw.text((352, 48), "100% SLA PASS", fill="#059669", font=font_badge)

    # Main Hero Title
    draw.text((60, 95), "AGENTOPS OBSERVATORY", fill="#0f172a", font=font_hero)
    draw.text((60, 155), "Observability, Governance & Audit for Autonomous AI Agents & MCP", fill="#334155", font=font_sub)

    # 4 Feature Pills
    features = [
        ("Zero-Trust Privacy", "Deterministic regex & Luhn redaction for API keys & PII", "#7c3aed", "#f5f3ff"),
        ("10 Security Guardrails", "Halts prompt injections, destructive commands, & rogue tools", "#e11d48", "#ffe4e6"),
        ("Trace DAG & Timeline", "Full parent-child spans with failure propagation & latency", "#0284c7", "#f0f9ff"),
        ("Append-Only Cryptography", "Tamper-evident SHA-256 hash chaining for compliance", "#059669", "#ecfdf5"),
    ]

    for idx, f in enumerate(features):
        col = idx % 2
        row = idx // 2
        fx = 60 + col * 550
        fy = 215 + row * 105
        draw.rounded_rectangle([(fx, fy), (fx + 530, fy + 88)], radius=12, fill=f[3], outline=f[2], width=1)
        draw.text((fx + 20, fy + 16), f[0], fill=f[2], font=font_h3)
        draw.text((fx + 20, fy + 45), f[1], fill="#475569", font=font_body)

    # Bottom Metric Highlight Banner
    my = 445
    draw.rounded_rectangle([(60, my), (width - 60, my + 135)], radius=14, fill="#0f172a")

    metrics = [
        ("100.0%", "TRACE COMPLETENESS", "#38bdf8"),
        ("100.0%", "SECRET REDACTION", "#a855f7"),
        ("100.0%", "POLICY DETECTION", "#34d399"),
        ("0 LEAKS", "CROSS-USER ISOLATION", "#fbbf24"),
    ]

    bw = (width - 120) // 4
    for i, m in enumerate(metrics):
        mx = 60 + i * bw
        draw.text((mx + 30, my + 25), m[0], fill=m[2], font=font_metric_val)
        draw.text((mx + 30, my + 68), m[1], fill="#94a3b8", font=font_metric_lbl)

    # Author signature & Stack
    draw.text((60, my + 102), "FastAPI • React • TypeScript • Vite • OpenTelemetry • SQLite/Postgres • Docker", fill="#64748b", font=get_font(12))
    draw.text((width - 320, my + 102), "Created by Vijay Mahes", fill="#cbd5e1", font=get_font(13, bold=True))

    img.save(output_path, "PNG")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    create_dashboard_light("docs/images/dashboard_light.png")
    create_trace_dag_light("docs/images/trace_dag_light.png")
    create_linkedin_banner("image.png")
