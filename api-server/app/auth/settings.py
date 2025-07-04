import os
import pathlib
from dotenv import load_dotenv
from pydantic import BaseSettings, Field


load_dotenv()

with open(
    os.environ.get(
        "PRIVATE_KEY_PATH",
        os.path.join(
            pathlib.Path(__file__).parent.parent.parent, "dev_private_key.pem"
        ),
    ),
    "r",
) as f:
    PRIVATE_KEY = f.read()
with open(
    os.environ.get(
        "PUBLIC_KEY_PATH",
        os.path.join(pathlib.Path(__file__).parent.parent.parent, "dev_public_key.pem"),
    ),
    "r",
) as f:
    PUBLIC_KEY = f.read()


class AuthJWTSettings(BaseSettings):
    authjwt_algorithm: str = "RS256"
    authjwt_public_key: str = PUBLIC_KEY
    authjwt_private_key: str = PRIVATE_KEY
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set[str] = {"access", "refresh"}
