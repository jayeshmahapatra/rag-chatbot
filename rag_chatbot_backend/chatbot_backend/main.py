"""Main entrypoint for the app."""
import os
from typing import Optional, Union
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from typing_extensions import Annotated
from pydantic import BaseModel

from chain.chain import answer_chain
from schema import ChatRequest

# Monitoring
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "not_provided"),
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "not_provided"),
    host = "https://cloud.langfuse.com"
    )

# # Check environment has the secret token set, else raise an error
# if "SECRET_TOKEN" not in os.environ:
#     raise ValueError("SECRET_TOKEN environment variable not set")

# async def verify_token(x_token: Annotated[str, Header()]) -> None:
#     """Verify the token is valid."""
#     # Replace this with your actual authentication logic
#     if x_token != os.environ.get("SECRET_TOKEN"):
#         raise HTTPException(status_code=400, detail="X-Token header invalid")

app = FastAPI(
    title="Jayesh Chatbot",
    description="A RAG chatbot by Jayesh",
    version="0.1.0",
    # dependencies=[Depends(verify_token)],
)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
