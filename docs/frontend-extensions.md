# Frontend Extensions

## API Integration

### REST API

```typescript
// Create response
const response = await fetch('http://localhost:8000/v1/responses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token',
    'x-request-id': 'req_' + Date.now()
  },
  body: JSON.stringify({
    input: 'What is in the knowledge base?',
    conversation_id: 'conv_123',
    metadata: { user_id: 'user_456' }
  })
});

const data = await response.json();
console.log(data.output[0].content[0].text);
```

### Streaming API

```typescript
// OpenAI-style streaming uses POST /v1/responses with stream=true.
const response = await fetch('http://localhost:8000/v1/responses', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: 'Hello', stream: true })
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (reader) {
  const { value, done } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value, { stream: true }));
}
```

### React Hook Example

```typescript
import { useState, useEffect } from 'react';

function useStreamingResponse(input: string) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!input) return undefined;

    setLoading(true);
    setText('');

    const controller = new AbortController();

    const run = async () => {
      const response = await fetch('/v1/responses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input, stream: true }),
        signal: controller.signal,
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        for (const eventBlock of chunk.split('\n\n')) {
          if (!eventBlock.includes('event: response.output_text.delta')) continue;
          const dataLine = eventBlock.split('\n').find((line) => line.startsWith('data: '));
          if (!dataLine) continue;
          const data = JSON.parse(dataLine.slice(6));
          setText((prev) => prev + data.delta);
        }
      }

      setLoading(false);
    };

    void run();

    return () => controller.abort();
  }, [input]);

  return { text, loading };
}
```

## Response Format

```typescript
interface Response {
  id: string;
  object: 'response';
  model: string;
  output: Array<{
    type: 'message';
    role: 'assistant';
    content: Array<{
      type: 'output_text';
      text: string;
    }>;
  }>;
  metadata: {
    route: 'rag' | 'tool' | 'direct' | 'clarify' | 'guardrail';
    [key: string]: any;
  };
  extensions: Record<string, any>;
}
```

## Error Handling

```typescript
try {
  const response = await fetch('/v1/responses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input: 'Hello' })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(error.error.code, error.error.message);
    return;
  }

  const data = await response.json();
  // Handle success
} catch (err) {
  console.error('Network error:', err);
}
```

## Document Upload

```typescript
async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', 'user_456');

  const response = await fetch('/v1/documents/upload', {
    method: 'POST',
    body: formData
  });

  return await response.json();
}
```

## CORS Configuration

For production, configure CORS in `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Authentication

Replace auth stub with real authentication:

```python
# app/middleware/auth.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        
        if not token:
            raise HTTPException(status_code=401, detail="Missing token")
        
        # Verify token
        user = await verify_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        request.state.user = user
        return await call_next(request)
```

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/responses")
@limiter.limit("10/minute")
async def create_response(request: Request, ...):
    # ...
```

## WebSocket Support

For real-time bidirectional communication:

```python
from fastapi import WebSocket

@app.websocket("/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        data = await websocket.receive_text()
        response = await process_message(data)
        await websocket.send_json(response)
```

Frontend:

```typescript
const ws = new WebSocket('ws://localhost:8000/v1/ws');

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response);
};

ws.send(JSON.stringify({ input: 'Hello' }));
```

## Best Practices

1. **Use request IDs** - Track requests across frontend/backend
2. **Handle errors gracefully** - Show user-friendly messages
3. **Keep model params backend-owned** - Configure `DEFAULT_CHAT_MODEL` and `DEFAULT_TEMPERATURE` on the server
4. **Show loading states** - Indicate processing
5. **Stream when possible** - Better UX for long responses
6. **Validate input** - Client-side validation before API call
7. **Cache responses** - Reduce redundant API calls
8. **Monitor performance** - Track API latency
