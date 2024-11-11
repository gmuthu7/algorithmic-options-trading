import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from login.login_controller import router as login_router
from context.context_controller import router as context_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(login_router)
app.include_router(context_router)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s.%(msecs)03d %(name)s:%(funcName)s - %(processName)s:%(thread)s -%(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    uvicorn.run("main:app", reload=True)
