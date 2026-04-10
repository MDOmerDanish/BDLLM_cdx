#!/bin/bash
echo "Purging corrupted virtual environment..."
rm -rf vllm_env

echo "Building isolated Python virtual environment..."
python3 -m venv vllm_env
source vllm_env/bin/activate

echo "Enforcing strict dependency pinning..."
# 4.45.2 satisfies vLLM 0.6.2 requirements while retaining the deprecated tokenizer attributes
pip install transformers==4.45.2 vllm==0.6.2 xformers==0.0.27.post2 fastapi uvicorn

echo "Starting PlanetServe-style LLM engine with OPT-125M..."
python3 engine_server.py &
echo $! > vllm.pid
echo "Custom API node started in background. PID saved."
deactivate
