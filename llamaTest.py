import transformers
import torch
import time

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

startTime = time.perf_counter()

outputs = pipeline(
    messages,
    max_new_tokens=256,
)

elapsedTime = time.perf_counter() - startTime

print(outputs[0]["generated_text"][-1])

print(f"/nElapsed time: {(elapsedTime / 60)} min")
