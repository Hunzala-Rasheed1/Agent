import os
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from src.agent import GraphQLAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Get environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
graphql_api_url = os.getenv("GRAPHQL_API_URL")

# Check if required environment variables are set
if not all([openai_api_key, openai_api_version, openai_api_endpoint, graphql_api_url]):
    missing_vars = []
    if not openai_api_key:
        missing_vars.append("OPENAI_API_KEY")
    if not openai_api_version:
        missing_vars.append("OPENAI_API_VERSION")
    if not openai_api_endpoint:
        missing_vars.append("OPENAI_API_ENDPOINT")
    if not graphql_api_url:
        missing_vars.append("GRAPHQL_API_URL")
    
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize the GraphQL agent
agent = GraphQLAgent(
    graphql_url=graphql_api_url,
    openai_api_key=openai_api_key,
    openai_api_version=openai_api_version,
    openai_api_endpoint=openai_api_endpoint
)

# Create FastAPI app
app = FastAPI(
    title="LLM-Powered GraphQL Agent",
    description="An API that translates natural language queries into GraphQL requests",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    q: str

class QueryResponse(BaseModel):
    answer: str
    graphql_query: str = None
    error: str = None

@app.get("/")
async def root():
    return {"message": "Welcome to the LLM-Powered GraphQL Agent. Use POST /query to ask questions."}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> Dict[str, Any]:
    """
    Process a natural language query and return an answer.
    
    Args:
        request: QueryRequest with the question
        
    Returns:
        QueryResponse with the answer
    """
    if not request.q:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    logger.info(f"Received query: {request.q}")
    
    try:
        result = agent.query(request.q)
        
        # Check for errors
        if "error" in result:
            logger.error(f"Error processing query: {result['error']}")
            return QueryResponse(
                answer=result.get("answer", "I couldn't process your query."),
                error=result["error"]
            )
            
        return QueryResponse(
            answer=result["answer"],
            graphql_query=result["graphql_query"]
        )
        
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)