import os
from datetime import datetime
from typing import Optional

from redis_om import HashModel, Field

from setting import KITE_CREDENTIALS_KEY


# Credentials Model
class CredentialsModel(HashModel):
    primary_key: str = Field(default=KITE_CREDENTIALS_KEY, primary_key=True)
    api_key: str = Field(default=os.getenv("KITE_API_KEY"))
    api_secret: str = Field(default=os.getenv("KITE_API_SECRET"))
    access_token: Optional[str] = None
    timestamp: Optional[datetime] = None
