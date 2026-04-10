# Off-Chain Architecture

## Component Breakdown
1. **Python Orchestrator (`manager.py`)** handles the CLI/menu, routes requests, validates HTLC state, and bridges to the local inference stack while orchestrating HTLC flows for payment-aware inference.
2. **LLM Client (`llm_client/llm_client.py`)** acts as the HTTP client that packages prompts, sends them to the custom node, and normalizes responses before returning them to the orchestrator.
3. **Custom LLM Node (`llm_server/engine_server.py`)** exposes a FastAPI `POST /generate` endpoint backed by `AsyncLLMEngine` configured to run OPT-125M. It isolates sampling parameters and provides a deterministic inference target for the orchestrator.

## Request Lifecycle
```
+-------------------------------+     +----------------------------+     +----------------------------------------+
| Orchestrator (manager.py)     | --> | LLM Client (llm_client.py) | --> | Custom LLM Node (engine_server.py)      |
| - Menu/HTLC control flows    |     | - JSON payload builder     |     | - FastAPI OPT-125M backend              |
| - Payment verification hooks |     | - HTTP POST to /generate    |     | - AsyncLLMEngine + SamplingParams       |
+-------------------------------+     +----------------------------+     +----------------------------------------+
```

## Environment Isolation Strategy
The `vllm_env` virtual environment isolates GPU-bound dependencies from other Python tooling to prevent ABI conflicts during CUDA/rocm launches. Within that environment we pin `transformers==4.45.2` and `vllm==0.6.2`, with `xformers==0.0.27.post2` for compatible tensor operations. Those exact versions bypass the RoPE/tokenizer assertions that newer transformers releases introduce, so the OPT-125M engine runs reliably on the available GPU architecture. Keeping this stack isolated ensures Fabric tooling and other Python workflows remain unaffected by the heavy inference dependencies.
