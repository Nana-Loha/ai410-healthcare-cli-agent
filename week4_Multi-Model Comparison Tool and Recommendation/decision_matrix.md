# Lab 4.3 Decision Matrix

| Criteria | Weight | Claude Sonnet 4.6 | GPT-5.4 | Gemini 3.1 Pro |
| :--- | ---: | ---: | ---: | ---: |
| Coding capability | 30% | 10 | 9 | 8 |
| Reasoning quality | 25% | 10 | 10 | 8 |
| Tool/MCP workflow behavior | 15% | 10 | 9 | 7 |
| Latency / responsiveness | 15% | 8 | 5 | 10 |
| Responsible AI awareness | 10% | 10 | 9 | 8 |
| Cost efficiency | 5% | 8 | 6 | 9 |
| **Total** | **100%** | **9.5** | **8.5** | **8.2** |

---

## Recommendation

Claude Sonnet 4.6 is recommended as the primary model for the Sprint 2 Medical AI Assistant workflow.

## Key Findings

### Engineering Autonomy
During benchmarking, Claude Sonnet 4.6 demonstrated the strongest autonomous software engineering behavior, including proactive test generation, iterative debugging, multi-file implementation, and automated verification workflows.

### Requirements Alignment
It showed the strongest specification-awareness related to FR-003 through FR-006, helping ensure that privacy, safety, and clinical summarization requirements remained consistent throughout the implementation process.

### Industry Alignment
These observations are consistent with current industry benchmark trends. SWE-bench highlights Claude’s strong performance on real-world software engineering tasks, while LiveCodeBench demonstrates high reasoning quality in coding-oriented workflows. Its ability to manage files, execute tests, and maintain implementation consistency was particularly valuable for Sprint 2.

## Alternative Model Observations

### GPT-5.4
GPT-5.4 demonstrated strong reasoning quality and excellent privacy/compliance analysis capabilities. However, benchmark observations showed significantly higher latency during long-context summarization workflows, reducing efficiency for rapid iterative development.

### Gemini 3.1 Pro
Gemini 3.1 Pro demonstrated the fastest response times and consistently structured outputs. However, it showed less autonomous tool-use, testing behavior, and self-verification capability compared to Claude Sonnet 4.6.

## Benchmark Limitations

This evaluation used a sequential shared-workspace methodology. Earlier models created and modified implementation files and tests, meaning later models may have benefited from additional project context and existing structure.

In addition, latency measurements were collected through a manual interactive workflow and may include minor human delays during prompt switching and response recording.

Therefore, these findings should be interpreted as workflow-oriented comparative observations rather than fully isolated production-grade benchmark measurements.