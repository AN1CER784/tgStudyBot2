from dataclasses import dataclass
from typing import List


@dataclass
class StartResult:
    attempt_id: int
    test_id: int
    q_ids: List[int]
    description: str
