import logging

import uvicorn
from fastapi import FastAPI

from kite.kite_controller import router as kite_router

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(kite_router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s.%(msecs)03d %(name)s:%(funcName)s - %(processName)s:%(thread)s -%(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    uvicorn.run("main:app")
