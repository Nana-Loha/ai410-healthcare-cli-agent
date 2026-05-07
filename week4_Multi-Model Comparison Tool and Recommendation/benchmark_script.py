import time
import csv

test_prompts = [
    {
        "task": "Medical Record Summarization",
        "prompt": "Build the medical record summarization feature as defined in SPEC.md. Use LlamaIndex for processing and ensure no data is stored as per FR-004."
    },
    {
        "task": "Drug Interaction Reasoning",
        "prompt": "Identify potential risks in a drug interaction analysis workflow and explain why human review is required."
    },
    {
        "task": "Coding Validation",
        "prompt": "Write a Python function that validates whether a medication dosage value is numeric, positive, and within an expected safe range."
    },
    {
        "task": "Responsible AI Risk",
        "prompt": "List three responsible AI risks for a medical AI assistant and provide concrete mitigations."
    }
]

models = [
    "Claude Sonnet 4.6",
    "GPT-5.4",
    "Gemini 3.1 Pro"
]

results = []

for model in models:
    print("\n" + "=" * 60)
    print(f"MODEL: {model}")
    print("=" * 60)

    for test in test_prompts:
        print(f"\nTASK: {test['task']}")
        print("\nCopy this prompt into the model chat:")
        print("-" * 60)
        print(test["prompt"])
        print("-" * 60)

        input("\nPress ENTER right before you send the prompt to the model...")
        start_time = time.perf_counter()

        input("Press ENTER when the model finishes the full response...")
        end_time = time.perf_counter()

        latency = round(end_time - start_time, 2)

        quality_score = input("Enter quality score from 1-10: ")
        notes = input("Enter short observation notes: ")

        results.append({
            "model": model,
            "task": test["task"],
            "latency_seconds": latency,
            "quality_score": quality_score,
            "notes": notes
        })

with open("benchmark_results.csv", "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "model",
        "task",
        "latency_seconds",
        "quality_score",
        "notes"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("\nBenchmark results saved to benchmark_results.csv")