from pydantic import BaseModel


class Problem(BaseModel):
    id: str | None
    name: str | None
    tags: list | None
    complexity: int | None
    solve_count: int | None
