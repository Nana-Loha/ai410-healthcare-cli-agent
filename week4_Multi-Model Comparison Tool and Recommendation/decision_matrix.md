# Lab 4.3 Decision Matrix

| Criteria | Weight | Claude Sonnet 4.6 | GPT-5.4 | Gemini 3.1 Pro |
|---|---:|---:|---:|---:|
| Coding capability | 30% | 10 | 9 | 8 |
| Reasoning quality | 25% | 10 | 10 | 8 |
| Tool/MCP workflow behavior | 15% | 10 | 9 | 7 |
| Latency / responsiveness | 15% | 8 | 5 | 10 |
| Responsible AI awareness | 10% | 10 | 9 | 8 |
| Cost efficiency | 5% | 8 | 6 | 9 |
| **Total** | **100%** | **9.5** | **8.5** | **8.2** |

---

# Recommendation

Claude Sonnet 4.6 is recommended as the primary model for the Sprint 2 medical AI assistant workflow. During benchmarking, it demonstrated the strongest autonomous software engineering behavior, including proactive test generation, iterative debugging, multi-file implementation, pytest validation, and strong specification-awareness tied to FR-003 through FR-006 requirements.

GPT-5.4 demonstrated excellent reasoning and specification-review capability, especially for privacy and compliance analysis. However, it showed significantly higher latency during complex summarization tasks, making it less efficient for rapid iterative workflows.

Gemini 3.1 Pro demonstrated the fastest response times and consistently structured outputs. However, it showed less autonomous tool-use and verification behavior compared to Claude Sonnet 4.6.

Overall, Claude Sonnet 4.6 provided the best balance of:
- coding capability
- reasoning quality
- workflow automation
- latency
- responsible AI awareness
- MCP/tool integration

for the Sprint 2 project requirements.

---

# Benchmark Limitation

This benchmark used a sequential shared-workspace evaluation. Earlier models created and modified implementation files and tests, which may have influenced later model performance by providing additional project context and structure.

As a result, these findings should be interpreted as workflow-oriented comparative observations rather than fully isolated production-grade benchmark measurements.