# 🧠 Multi-Model Intelligent Routing & Self-Learning System (`multi_model_intelligent_routing_system`)

> **Cost-Aware Prompt Gateway with Automated Quality Assurance & Continuous Self-Learning**

---

## 💡 What is this project? (In Simple Terms)

Not all AI prompts require the most expensive and powerful model. Asking *"What is the capital of France?"* doesn't need a high-cost frontier model like GPT-4o—a smaller, faster, and cheaper model (like GPT-4o Mini or Qwen 4B) can handle it in milliseconds for a fraction of a cent. However, complex coding, multi-step analysis, or structured data extraction tasks do require high-tier models.

**`multi_model_intelligent_routing_system`** acts as an **Intelligent Traffic Router for LLM Requests**:

1. **Analyzes incoming prompts** in real-time to assess complexity (simple, moderate, complex).
2. **Routes the prompt to the cheapest LLM** capable of answering it correctly.
3. **Evaluates response quality asynchronously** in the background using a powerful "LLM Judge".
4. **Feeds evaluation results back into a machine learning pipeline** to retrain the classifier continuously—making the routing decisions smarter over time!

---

## 🎯 Primary Benefits

- 💰 **Huge Cost Savings**: Minimizes LLM API spend by serving simpler prompts on low-cost models.
- ⚡ **Reduced Latency**: Faster response times for simple queries using small/lightweight models.
- 🤖 **Automated Quality Control**: Background judge evaluations verify that cheaper models don't produce low-quality outputs.
- 🔄 **Self-Learning Architecture**: Retrains its prompt complexity classifier automatically using historical performance feedback.

---

## 🏗️ Architecture & How It Works

```
                        ┌────────────────────────┐
                        │   User HTTP Request    │
                        │    POST /completions   │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │    Feature Extractor   │
                        │ (len, code, keywords)  │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   Prompt Classifier    │
                        │ (Scikit-Learn ML Model)│
                        └───────────┬────────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               ▼                    ▼                    ▼
        ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
        │ Simple Tier  │     │ Moderate Tier│     │ Complex Tier │
        │ (GPT-4o Mini)│     │  (Llama 3)   │     │   (GPT-4o)   │
        └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
               │                    │                    │
               └────────────────────┼────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │ Save Request Log to DB │
                        └───────────┬────────────┘
                                    │
                     (If Routed to Non-High Tier)
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │ Celery Background Task │
                        │  (Asynchronous Eval)   │
                        └───────────┬────────────┘
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
   ┌───────────────────────┐                 ┌───────────────────────┐
   │ Reference High Model  │                 │    LLM Judge Model    │
   │  (Generates Benchmark)│                 │ (Scores Candidate Output)│
   └───────────┬───────────┘                 └───────────┬───────────┘
               │                                         │
               └────────────────────┬────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │ Save Evaluation to DB  │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │ Scheduled Retraining   │
                        │  Feedback Dataset & ML │
                        └────────────────────────┘
```

---

## ⚙️ Core Components Explained

### 1. 🔍 Prompt Feature Extractor (`classifier/feature_extractor.py`)
Analyzes raw prompt text and calculates numeric & boolean metrics:
- **Structural**: Word count, character count, line count, question mark count.
- **Content Format**: Detects code blocks (```), JSON schemas, markdown tables.
- **Intent Keywords**: Checks for task keywords like `extract`, `summarize`, `compare`, `translate`, `design`, `analyze`.
- **Constraint Density**: Counts imperative constraint words like `must`, `should`, `only`, `exactly`.

### 2. 🤖 ML Classifier (`classifier/predict.py` & `trainer.py`)
Uses the extracted features to classify prompt complexity into tiers:
- **`simple`** $\rightarrow$ Fast/cheap tier (e.g., GPT-4o Mini / Qwen 4B).
- **`moderate`** $\rightarrow$ Mid-tier model (e.g., Llama 3).
- **`complex`** $\rightarrow$ High-capability model (e.g., GPT-4o / Qwen 8B).

### 3. 🌐 API Router & Services (`api.py`, `service.py`, `request_handler.py`)
- **FastAPI endpoint (`POST /v1/completions`)**: Accepts completion prompts.
- **`Router` & `LLMRegistry`**: Selects model based on tier and calculates token usage costs & latencies.
- **`RequestRepository`**: Stores prompt inputs, outputs, latencies, and costs in PostgreSQL via SQLAlchemy async sessions.

### 4. ⚖️ Asynchronous Judge & Evaluation Pipeline (`task.py`, `service.py`)
For requests handled by low or medium-tier models:
1. Celery dispatches a background task (`evaluate_request`).
2. The system generates a reference answer using the highest-quality model available (`GPT-4o`).
3. An **LLM Judge** (`GPT-4.1 Judge`) compares candidate output vs. reference output, scoring accuracy and determining the winner.
4. Stores evaluation scores, winning candidate, and reasoning in the database.

### 5. 🔄 Feedback & Continuous Learning (`classifier/feedback_dataset_builder.py` & `train.py`)
- `FeedbackDatasetBuilder` queries database logs where candidate low-tier responses either succeeded with high confidence ($\ge 0.8$) or failed against reference answers ($\le 0.7$).
- Retrains the machine learning model periodically via a scheduled Celery task (`retrain_classifier`), updating the model weights in `classifier/models/`.

---

## 📁 Directory Structure

| Path | Description |
| :--- | :--- |
| [`api.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/api.py) | FastAPI router providing the `/v1/completions` endpoint. |
| [`service.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/service.py) | Business logic for prompt completion routing and background LLM evaluation. |
| [`llm_registry.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/llm_registry.py) | Model registry defining tiers, costs, latencies, and prompt routing lookup. |
| [`request_handler.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/request_handler.py) | Executes model calls via LangChain and measures runtime performance. |
| [`task.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/task.py) | Celery background tasks for async LLM judge evaluation, retries, and retraining. |
| [`repo.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/repo.py) | Database repositories for request logs and evaluation results using SQLAlchemy. |
| [`evaluation_prompt.py`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/evaluation_prompt.py) | Formats judge prompts for comparing candidate vs. reference model responses. |
| [`classifier/`](file:///home/saandeep/Desktop/GenAI/multi_model_intelligent_routing_system/classifier/) | Machine learning classifier package (feature extraction, dataset building, training & inference). |

---

## 📡 API Usage Example

### Endpoint
`POST /v1/completions`

### Request Payload
```json
{
  "prompt": "Write a python function to find the quicksort partition index with inline documentation."
}
```

### Response Payload
```json
{
  "text": "def partition(arr, low, high): ...",
  "model": "Llama 3",
  "latency_ms": 1150.42,
  "cost": 0.000125
}
```
