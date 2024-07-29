import time

from fastapi import FastAPI, Response, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.responses import HTMLResponse

from app.api.v1.endpoints import *
from app.db.base import Base
from app.db.session import engine
from aiocache import caches
from fastapi.applications import State
from app.core import limiter  # Import the limiter

app = FastAPI()
app.state = State()  # Explicitly create the state
app.state.limiter = limiter

# Configure aiocache
caches.set_config({
    'default': {
        'cache': "aiocache.SimpleMemoryCache",
        'serializer': {
            'class': "aiocache.serializers.JsonSerializer"
        },
    }
})


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    detail = {
        "error": "Rate limit exceeded",
        "message": str(exc)
    }
    return JSONResponse(status_code=429, content=detail)


@app.middleware("http")
async def global_limiter(request: Request, call_next):
    try:
        response = await limiter.limit("100/minute")(call_next)(request)
        return response
    except RateLimitExceeded as exc:
        return await rate_limit_exceeded_handler(request, exc)


app.add_middleware(BaseHTTPMiddleware, dispatch=global_limiter)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["category"])
app.include_router(shipping_router, prefix="/api/v1/shipping-orders", tags=["shipping"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/rapidoc")
async def get_rapidoc():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RapiDoc</title>
        <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
    </head>
    <body>
        <rapi-doc
            spec-url = "/openapi.json"
        ></rapi-doc>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
