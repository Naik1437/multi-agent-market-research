import os

import pytest


@pytest.mark.skipif(
    os.getenv("RUN_LLM_INTEGRATION") != "1",
    reason="Set RUN_LLM_INTEGRATION=1 to run the live Gemini integration check."
)
def test_gemini_connection():
    from config.llm_config import llm

    response = llm.call(
        messages=[
            {
                "role": "user",
                "content": "Reply with: Gemini connection successful!"
            }
        ]
    )

    assert response
