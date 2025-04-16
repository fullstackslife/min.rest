from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess
from typing import List, Dict, Any
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    command: str

class Repository(BaseModel):
    name: str
    path: str
    type: str

def get_workspace_root() -> Path:
    return Path(__file__).parent.parent.parent

@app.get("/api/repositories", response_model=List[Repository])
async def list_repositories():
    workspace_root = get_workspace_root()
    repositories = []
    
    for item in workspace_root.iterdir():
        if item.name.startswith('.'):
            continue
            
        repositories.append(Repository(
            name=item.name,
            path=str(item.relative_to(workspace_root)),
            type="directory" if item.is_dir() else "file"
        ))
    
    return repositories

@app.post("/api/execute")
async def execute_command(request: CommandRequest):
    try:
        # Execute the command in the workspace root
        result = subprocess.run(
            request.command,
            shell=True,
            cwd=str(get_workspace_root()),
            capture_output=True,
            text=True
        )
        
        return {
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 