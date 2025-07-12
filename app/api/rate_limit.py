from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict
from jose import jwt, JWTError
import os

RATE_LIMIT = 10  # requests
RATE_PERIOD = 120  # seconds
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)

    def is_allowed(self, user: str):
        print(f"Checking rate limit for user: {user}")
        now = time.time()
        window = now - RATE_PERIOD
        requests = self.user_requests[user]
        self.user_requests[user] = [t for t in requests if t > window]
        if len(self.user_requests[user]) >= RATE_LIMIT:
            return False
        self.user_requests[user].append(now)
        return True

rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = "anonymous"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user = payload.get("sub", "anonymous")
                print(f"✅ RateLimitMiddleware: Authenticated user: {user}")
            except JWTError as e:
                print(f"❌ RateLimitMiddleware: Invalid token: {e}")

        if not rate_limiter.is_allowed(user):
            return Response("Rate limit exceeded", status_code=429)

        return await call_next(request)
