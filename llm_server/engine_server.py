import uuid
import uvicorn
from fastapi import FastAPI, Request
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams

app = FastAPI(title="BDLLM PlanetServe Node")

# OPT-125m completely bypasses Llama RoPE scaling configurations
engine_args = AsyncEngineArgs(
    model="facebook/opt-125m",
    enforce_eager=True,
    gpu_memory_utilization=0.9
)
engine = AsyncLLMEngine.from_engine_args(engine_args)

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "Hello")
    
    sampling_params = SamplingParams(max_tokens=100, temperature=0.7)
    request_id = str(uuid.uuid4())
    
    results_generator = engine.generate(prompt, sampling_params, request_id)
    final_output = None
    async for request_output in results_generator:
        final_output = request_output
        
    return {"response": final_output.outputs[0].text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
