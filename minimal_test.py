from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return HTMLResponse("""
    <html>
    <head>
        <title>Test</title>
    </head>
    <body>
        <h1>YouTube Analyzer - Minimal Test</h1>
        <p>If you see this, FastAPI is working!</p>
        <a href="/test">Test endpoint</a>
    </body>
    </html>
    """)

@app.get("/test")
def test():
    return {"message": "Test successful!", "status": "ok"}

if __name__ == "__main__":
    print("Starting minimal server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)