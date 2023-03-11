from sqlalchemy.orm import Session
from database.models import Problem, Tag, ProblemToTag
from database import schemas


def create_problem(session: Session, problem: schemas.Problem) -> Problem:
    db_user = Problem(id=problem.id, name=problem.name, complexity=problem.complexity,
                      solve_count=problem.solve_count)
    session.add(db_user)
    for tag in problem.tags:
        db_tag = get_tag_by_name(session, tag)
        if db_tag is None:
            db_tag = create_tag(session, tag)
        add_tag_to_problem(session, problem.id, db_tag.id)
    session.commit()
    return db_user


def update_problem(session: Session, db_problem: Problem, problem: schemas.Problem) -> None:
    db_problem.solve_count = problem.solve_count
    session.commit()


def get_problem_by_id(session: Session, problem_id: str) -> Problem | None:
    return session.query(Problem).where(Problem.id == problem_id).first()


def get_tag_by_name(session: Session, name: str) -> Tag | None:
    return session.query(Tag).where(Tag.name == name).first()


def create_tag(session: Session, name: str) -> Tag:
    db_tag = Tag(name=name)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


def add_tag_to_problem(session: Session, problem_id: str, tag_id: int) -> ProblemToTag:
    db_tag = ProblemToTag(problem_id=problem_id, tag_id=tag_id)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag
