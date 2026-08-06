# 🧪 LLM Evaluation & Regression Testing Framework (`llm-eval-project`)

> **CI/CD and Automated Quality Assurance for Large Language Models & Prompts**

---

## 💡 What is this project? (In Simple Terms)

When building applications powered by Large Language Models (LLMs), tweaking a system prompt, modifying expected output formats, or changing model providers (e.g., switching from Ollama to Groq, or upgrading models) can unpredictable impact performance. What worked well before might suddenly break.

**`llm-eval-project`** works like an automated **CI/CD test suite for AI prompts**. 
It runs standard test datasets against your LLMs, verifies whether the output matches expected categories/summaries, measures latency, detects accuracy regressions compared to previous runs, and automatically alerts your team on Slack if a prompt change caused a drop in quality.

---

## ✨ Key Features

- 🏷️ **Prompt & Dataset Versioning**: Organizes prompts and test evaluation datasets using simple YAML configuration files.
- ⚡ **Multi-Provider Support**: Seamlessly evaluates prompts using providers like **Ollama** (local) or **Groq** (cloud-accelerated).
- 📐 **Structured Output Validation**: Enforces JSON output schemas dynamically using Pydantic models to guarantee valid structured responses.
- 📉 **Regression & Delta Analysis**: Compares current evaluation runs against historical benchmarks to detect regressions (test cases that previously passed but now fail) and improvements.
- 🔔 **Slack Alerts**: Sends instant Slack notifications categorized by status:
  - 🟢 **PASS**: Performance is stable or improved.
  - 🟡 **WARNING**: Minor drop in accuracy.
  - 🔴 **CRITICAL**: Significant regression detected (e.g., >8% drop in accuracy).

---

## 🏗️ Architecture & How It Works

```
                     ┌──────────────────────┐
                     │   YAML Configs       │
                     │ (Prompts & Datasets) │
                     └──────────┬───────────┘
                                │
                                ▼
┌──────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│  LLM Models  │ ◄───┤   Evaluator Engine   │ ◄───┤  Pydantic Schema │
│ (Groq/Ollama)│     │     (batching)       │     │    Validation    │
└──────────────┘     └──────────┬───────────┘     └──────────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │   Report Generator   │
                     └──────────┬───────────┘
                                │
          ┌─────────────────────┴─────────────────────┐
          ▼                                           ▼
┌──────────────────┐                       ┌──────────────────┐
│ Report Storage   │                       │  Slack Notifier  │
│ (Latest & History)                       │ (Alerts & Delta) │
└──────────────────┘                       └──────────────────┘
```

1. **Configuration**: Load versioned prompts (`prompts/`) and evaluation datasets (`dataset/`).
2. **Batch Processing**: The `Evaluator` sends prompts in batches asynchronously through LangChain chains.
3. **Structured Parsing**: Predictions are parsed and validated against strict JSON schemas defined in the prompt config.
4. **Comparison & Storage**: Results are benchmarked against `reports/latest.json`. Regressions and improvements are calculated.
5. **Notification**: Results and accuracy deltas are dispatched to a Slack webhook.

---

## 📁 Directory Structure

| File / Directory | Purpose |
| :--- | :--- |
| [`main.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/main.py) | Entry point to trigger an evaluation run based on environment variables. |
| [`evaluator.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/evaluator.py) | Core evaluation engine that communicates with LLMs, batches requests, and validates outputs. |
| [`models.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/models.py) | Pydantic data models for prompt configs, dataset items, evaluation results, runs, and diffs. |
| [`report_generator.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/report_generator.py) | Orchestrates evaluations, computes summary stats (accuracy, latency), and invokes storage/notifications. |
| [`report_storage.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/report_storage.py) | Saves run history JSONs and compares new runs against historical benchmarks to detect regressions. |
| [`slack_notifier.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/slack_notifier.py) | Formats and posts color-coded evaluation summary alerts to a Slack channel webhook. |
| [`yaml_manager.py`](file:///home/saandeep/Desktop/GenAI/llm-eval-project/yaml_manager.py) | Helper utility to load YAML configuration files for datasets and prompts. |
| `dataset/` | Contains YAML dataset files with test cases, expected categories, summaries, and difficulty ratings. |
| `prompts/` | Contains YAML prompt configurations including system prompts, output schemas, and few-shot examples. |
| `reports/` | Stores `latest.json` and timestamped evaluation run history. |

---

## 🚀 Environment Variables & Quick Start

### 1. Set Up Environment Variables
Create a `.env` file or export the following environment variables:

```bash
# Model & Provider Configuration
EVAL_PROVIDER=groq                     # Provider: 'groq' or 'ollama'
EVAL_MODEL=openai/gpt-oss-120b         # LLM model identifier
EVAL_PROMPT_VERSION=v1                 # Prompt version file in prompts/
EVAL_DATASET_VERSION=v1                # Dataset version file in dataset/

# API Keys & Webhooks
GROQ_API_KEY=your_groq_api_key         # Required if provider is groq
SLACK_WEBHOOK_URL=your_slack_webhook   # Optional: Slack webhook URL for notifications
```

### 2. Run an Evaluation
```bash
python main.py
```

### Example Console Output
```text
Processing batch 1/1
accuracy 0.95
accuracy_delta +0.05
regression_count 0
```
