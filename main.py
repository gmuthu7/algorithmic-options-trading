import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ui.common import router as common_router
from ui.form import router as form_router
from ui.login import router as login_router
from ui.navbar import router as navbar_router
from ui.tabs import router as tabs_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(login_router)
app.include_router(common_router)
app.include_router(form_router)
app.include_router(navbar_router)
app.include_router(tabs_router)

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
    uvicorn.run("main:app", reload=False)
