
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI Phdam")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Phdam</title>
        <style>
            body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f0f2f5; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }
            h1 { color: #2563eb; margin: 0 0 10px; }
            p { color: #555; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 AI Phdam</h1>
            <p>Xin chúc mừng! Ứng dụng đã chạy thành công 100% trên Render!</p>
        </div>
    </body>
    </html>
    """
