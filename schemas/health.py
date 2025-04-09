import enum

import pydantic


class Status(str, enum.Enum):
    SUCCESS = "success"
    FAIL = "fail"
    WARN = "warn"


class Health(pydantic.BaseModel):
    status: Status
    version: str
    releaseId: str