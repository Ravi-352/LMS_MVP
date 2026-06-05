"""
FastAPI app factory. Register routers here.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.core.config import settings
from app.db.sessions import engine, Base


# Routers:
from app.routes import auth
from app.routes.students import router as students_router
from app.routes.instructor import router as instructor_router
from app.routes.public import router as public_router
from app.routes.logs import router as logs_router
from app.routes.enrollment import router as enrollment_router
from app.routes.feedback import router as feedback_router
#feedback

limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = FastAPI(title="LMS MVP Backend", version="1.0.0", description="Backend API for LMS MVP with RBAC and APEX features")
    
    # CORS config
    app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3000", "https://yourdomain.com"], # do NOT use '*' in prod
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    #allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-CSRF-Token", "X-Requested-With", "Cookie"],
    expose_headers=["Set-Cookie"],
    )

    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, limiter._rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Try again later."},
        )

    # Create DB tables automatically in dev (for MVP simplicity) - we prefer to use alembic upgrades in production
    #Base.metadata.create_all(bind=engine)

    # include module routers
    prefix = "/api/v1"

     # Public pages like listing courses
    app.include_router(public_router, prefix=prefix + "/public", tags=["public"])

    # Authentication routes
    app.include_router(auth.router, prefix=prefix + "/auth", tags=["auth"])

    # Student role protected routes
    app.include_router(students_router, prefix=prefix + "/students", tags=["students"])

    # Instructor role protected routes
    app.include_router(instructor_router, prefix=prefix + "/instructor", tags=["instructor"])

    # Logging routes (client to backend logs)
    app.include_router(logs_router, prefix=prefix + "/logs", tags=["logs"])


    #app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
    app.include_router(enrollment_router, prefix="/api/v1/enrollment", tags=["enrollment"])
    #app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])
    app.include_router(feedback_router, prefix="/api/v1/feedback", tags=["feedback"])

    # For Future extension
    # app.include_router(admin_router, prefix="/admin", tags=["admin"])
    # app.include_router(payments_router, prefix="/payments", tags=["payments"])


    @app.get("/healthz")
    def health():
        return {"status": "ok"}

    return app

app = create_app()
