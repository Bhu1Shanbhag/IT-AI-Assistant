from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

# Import the logic and variables from main
from main import handle_query, vector_store, llm, create_and_store_article, load_excel_safely, EXCEL_PATH

app = FastAPI(title="IT Support AI Agent API")

# Add CORS middleware to allow the HTML frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"[API] Received query: {request.question}")
        response = handle_query(request.question, vector_store, llm)
        return {"response": response}
    except Exception as e:
        print(f"[API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@app.get("/")
async def root():
    return FileResponse("index.html")

def start_server():
    # Process Rows ONLY IF DB IS EMPTY (ensure setup is done)
    existing_docs = vector_store.get()
    if not existing_docs['ids']:
        print("Vector DB is empty. Processing Excel data...")
        df = load_excel_safely(EXCEL_PATH)
        for index, row in df.iterrows():
            create_and_store_article(row.to_dict(), vector_store)
    else:
        print(f"Vector DB already exists with {len(existing_docs['ids'])} documents.")

    print("\n--- Starting FastAPI Server on http://127.0.0.1:8000 ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start_server()
