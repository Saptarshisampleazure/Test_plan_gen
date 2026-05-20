from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileRecord:
    file_id: str
    file_name: str
    content_type: str
    size: int
    path: Path
