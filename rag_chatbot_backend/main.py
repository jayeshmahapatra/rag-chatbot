"""Main entrypoint for the app."""
import os
from typing import Optional, Union
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from langsmith import Client
from pydantic import BaseModel
from dotenv import load_dotenv

from chain import ChatRequest, answer_chain

# Monitoring
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "not_provided"),
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "not_provided"),
    host = "https://cloud.langfuse.com"
    )

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def add_langfuse_callback(config, request):
    config.update({"callbacks": [langfuse_handler]})
    return config

add_routes(
    app,
    answer_chain,
    path="/chat",
    input_type=ChatRequest,
    config_keys=["metadata", "configurable", "tags"],
    per_req_config_modifier = add_langfuse_callback
)


class SendFeedbackBody(BaseModel):
    run_id: UUID
    key: str = "user_score"

    score: Union[float, int, bool, None] = None
    feedback_id: Optional[UUID] = None
    comment: Optional[str] = None


# @app.post("/feedback")
# async def send_feedback(body: SendFeedbackBody):
#     client.create_feedback(
#         body.run_id,
#         body.key,
#         score=body.score,
#         comment=body.comment,
#         feedback_id=body.feedback_id,
#     )
#     return {"result": "posted feedback successfully", "code": 200}


# class UpdateFeedbackBody(BaseModel):
#     feedback_id: UUID
#     score: Union[float, int, bool, None] = None
#     comment: Optional[str] = None


# @app.patch("/feedback")
# async def update_feedback(body: UpdateFeedbackBody):
#     feedback_id = body.feedback_id
#     if feedback_id is None:
#         return {
#             "result": "No feedback ID provided",
#             "code": 400,
#         }
#     client.update_feedback(
#         feedback_id,
#         score=body.score,
#         comment=body.comment,
#     )
#     return {"result": "patched feedback successfully", "code": 200}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
