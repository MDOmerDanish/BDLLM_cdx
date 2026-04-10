# Off-Chain Architecture

## Python Orchestration Stack
1. `manager.py` is the CLI control plane: it bootstraps the Fabric network (`setup_and_run_fabric`), deploys HTLC chaincode (`deploy_chaincode`), runs the HTLC demonstration suite (`execute_htlc_payment`), and manages the custom LLM node (`manage_llm_server`). Each menu entry maps directly to the Fabric scripts and HTLC gateway interactions in `blockchain/gateway.py`.
2. `llm_client/llm_client.py` is a minimal HTTP client that serializes prompts into JSON, issues POST requests to `http://localhost:8000/generate`, and returns the response text or error message.
3. `llm_server/engine_server.py` spins up a FastAPI endpoint backed by `vLLM`'s `AsyncLLMEngine` configured for `facebook/opt-125m`, enforcing eager execution and sampling parameters before returning the generated text.

## Request Lifecycle
```
+-------------------------------+     +----------------------------+     +----------------------------------------+
| Orchestrator (manager.py)     | --> | LLM Client (llm_client.py) | --> | Custom LLM Node (engine_server.py)      |
| - Fabric/HTLC orchestration   |     | - JSON payload builder     |     | - FastAPI /generate endpoint           |
| - HTLC demo vectors           |     | - HTTP POST -> /generate    |     | - AsyncLLMEngine + SamplingParams      |
| - Subprocess to start/stop    |     |                            |     | - OPT-125M, enforce_eager, temp=0.7     |
+-------------------------------+     +----------------------------+     +----------------------------------------+
```

The orchestrator's `manage_llm_server` menu calls `start_vllm.sh`/`stop_vllm.sh` inside `llm_server/`, while option 2 imports `query_llm()` from `llm_client` to relay prompts to the running FastAPI node.

## Environment Isolation Strategy
`llm_server/start_vllm.sh` rebuilds an isolated `vllm_env` virtual environment, removes any stale environment, and installs the pinned dependencies `transformers==4.45.2`, `vllm==0.6.2`, `xformers==0.0.27.post2`, `fastapi`, and `uvicorn`. These exact versions prevent the RoPE/tokenizer assertion errors that appear with newer transformers releases and supply the heavy GPU/tensor operations required by `AsyncLLMEngine`. We keep this stack siloed so Docker/Fabric tooling elsewhere in the repo does not inherit large inference dependencies. `stop_vllm.sh` simply kills the PID stored in `vllm.pid`, ensuring a clean shutdown before redeploying the node.
