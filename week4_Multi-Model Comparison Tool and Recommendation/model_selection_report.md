# Week 4 Model Selection Report

## Benchmark Analysis

This report evaluates candidate AI models for Sprint 2 using benchmark evidence, operational constraints, latency observations, and responsible AI considerations collected during Week 4 benchmarking.

### Benchmark Interpretation

| Benchmark | Purpose | Use in Decision |
| :--- | :--- | :--- |
| SWE-bench Verified | Measures software engineering issue resolution | Strong signal for coding agents |
| HumanEval / LiveCodeBench | Measures coding and reasoning performance | Supplemental coding benchmark |
| GPQA Diamond | Evaluates scientific reasoning | Important for medical and science-heavy systems |

### Benchmark Pitfalls

Benchmark scores should not be treated as absolute indicators of real-world performance. Risks include benchmark contamination, narrow task distributions, and cherry-picked reporting. High benchmark scores do not automatically guarantee production reliability, strong domain fit, or effective tool-use behavior.

Additionally, this benchmark used a sequential shared-workspace workflow. Earlier models modified implementation files and tests, which may have influenced later model performance by providing additional project context and structure.

## Model Evaluation Results

The Sprint 2 project includes coding-heavy, reasoning-heavy, and safety-critical healthcare workflows. Operational constraints such as latency, cost efficiency, MCP/tool workflow behavior, and responsible AI requirements were included in the selection process. The weighted decision criteria and scores are documented in the accompanying Decision Matrix (Lab 4.3).

### Claude Sonnet 4.6

Claude Sonnet 4.6 demonstrated the strongest autonomous software engineering workflow during benchmarking. It proactively created tests, modified multiple project files, executed pytest validation, identified FR-004 privacy conflicts, and demonstrated strong specification-awareness tied to FR-003 through FR-006 requirements.

Claude Sonnet 4.6 also provided a strong balance between:
- coding capability
- reasoning quality
- tool-use behavior
- automated verification
- latency
- cost efficiency

making it the strongest overall model for the Sprint 2 workflow.

### GPT-5.4

GPT-5.4 demonstrated strong reasoning quality and specification-review capability, especially for privacy and compliance analysis. It provided detailed architectural explanations and implementation validation. However, latency during complex summarization tasks was significantly higher than the other models, making it less efficient for rapid iterative workflows.

### Gemini 3.1 Pro

Gemini 3.1 Pro demonstrated the fastest response times and consistently structured outputs. It performed well in concise summarization and risk analysis tasks. However, it demonstrated less autonomous tool-use and verification behavior compared to Claude Sonnet 4.6.

### Claude Opus 4.6 — Note

Claude Opus 4.6 was provisionally selected for drug interaction analysis in the Week 3 model strategy based on its highest reasoning capability among Anthropic models (SWE-bench Verified 80.8%, Rank 2 — AI410 Spring 2026 Syllabus Appendix). However, direct empirical benchmarking was not conducted during Week 4 due to VS Code Copilot plan limitations that do not include access to Claude Opus 4.6 during the benchmarking session. Based on provider documentation, Opus 4.6 is expected to provide higher reasoning quality at the cost of increased latency and cost compared to Sonnet 4.6. This comparison remains an open item for future sprint validation.

## Conclusion

The final model selection combines benchmark evidence with operational constraints and responsible AI considerations rather than relying on benchmark leadership alone.

Based on the Week 4 benchmark results, Claude Sonnet 4.6 is recommended as the primary model for Sprint 2 because it provided the best overall balance between:
- coding capability
- reasoning quality
- tool/MCP workflow behavior
- automated verification
- latency
- responsible AI awareness
- cost efficiency

This supports a balanced and production-oriented multi-model strategy for the medical AI assistant workflow.