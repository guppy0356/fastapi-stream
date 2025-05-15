import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="sk-PASTE_YOUR_API_KEY_HERE",
)

app = FastAPI()

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
# URL: https://medium.com/@shudongai/building-a-real-time-streaming-api-with-fastapi-and-openai-a-comprehensive-guide-cb65b3e686a5
# URL: https://platform.openai.com/docs/guides/streaming-responses?api-mode=responses
# URL: https://nikkie-ftnext.hatenablog.com/entry/how-to-test-fastapi-streamingresponse-202411
async def root():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say Hello!"}],
        stream=True,
    )

    print(f"Completion: {completion}")

    async def async_generator():
        for chunk in completion:
            print(f"Received chunk: {chunk}")
            
            response_data = {
                "id": chunk.id,
                "object": chunk.object,
                "created": chunk.created,
                "model": chunk.model,
                "system_fingerprint": chunk.system_fingerprint,
                "choices": [
                    {
                        "index": chunk.choices[0].index,
                        "delta": {
                            "content": getattr(chunk.choices[0].delta, 'content', None)
                        },
                        "finish_reason": chunk.choices[0].finish_reason
                    }
                ]
            }
            
            await asyncio.sleep(0.5)
            yield f"data: {json.dumps(response_data)}\n\n"

    return StreamingResponse(async_generator(), media_type="text/event-stream")
