from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, Boolean
from database.database_connector import Base
from sqlalchemy_serializer import SerializerMixin


class Problem(Base, SerializerMixin):
    __tablename__ = "problems"

    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    complexity = Column(Integer, nullable=False)
    solve_count = Column(Integer, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return str(self.to_dict())


class Tag(Base, SerializerMixin):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

    def __repr__(self) -> str:
        return str(self.to_dict())


class ProblemToTag(Base, SerializerMixin):
    __tablename__ = "problems_to_tags"

    problem_id = Column(String(10), ForeignKey("problems.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    def __repr__(self) -> str:
        return str(self.to_dict())

    __table_args__ = (PrimaryKeyConstraint(problem_id, tag_id),)
