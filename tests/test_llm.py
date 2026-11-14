from config.llm_config import llm

print("Testing Gemini connection...")

response = llm.call(
    messages=[
        {
            "role": "user",
            "content": "Reply with: Gemini connection successful!"
        }
    ]
)

print("Response:", response)