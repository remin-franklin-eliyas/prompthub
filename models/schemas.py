from dataclasses import dataclass
from datetime import datetime

@dataclass
class Prompt:
    id: int
    name: str
    filepath: str
    created_at: datetime

@dataclass
class Version:
    id: int
    prompt_id: int
    version_tag: str
    content: str
    message: str
    committed_at: datetime
    embedding: bytes | None = None

@dataclass
class TestCase:
    id: int
    prompt_id: int
    name: str
    input: str
    created_at: datetime

@dataclass
class TestResult:
    id: int
    version_id: int
    test_case_id: int
    output: str
    model: str
    ran_at: datetime