import time
import logging
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status

logger = logging.getLogger("blog_api")


class LoggingMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request:Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} completed_in={duration_ms:.2f}ms status={response.status_code}")
    response.headers["X-Process-Time-ms"] = f"{duration_ms:.2f}"
    return response

class RateLimiterMiddleware(BaseHTTPMiddleware):
  def __init__(self, app, max_requests: int= 5, window_seconds: int= 60):
    super().__init__(app)
    self.max_requests = max_requests
    self.window_seconds = window_seconds
    self.clients = {}

  async def dispatch(self, request, call_next):

    if request.url.path in["/docs", "/redoc", "/openapi.json"]:
      return await call_next(request)

    client_ip = request.client.host
    now = time.time()
    if client_ip not in self.clients:
      self.clients[client_ip]= []


    window_start = now - self.window_seconds
    self.clients[client_ip] = [t for t in self.clients[client_ip] if t> window_start]

    if len(self.clients[client_ip]) >= self.max_requests:
      from starlette.responses import JSONResponse
      return JSONResponse(
        status_code = 429,
        content = {"detail": "Too Many Request. Please wait."}
      )
    self.clients[client_ip].append(now)

    response = await call_next(request)
    return response

  
def setup_cors(app):
  app.add_middleware(
     CORSMiddleware,
     allow_origins= ["*"],
     allow_credentials= True,
     allow_methods= ["*"],
     allow_headers= ["*"],
    )

    

