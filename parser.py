import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import schemas
from database import crud

URL = "https://codeforces.com/problemset"


async def get_bs_by_url(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.read()
    return BeautifulSoup(text.decode('utf-8'), "html.parser")


def problem_processing(row) -> schemas.Problem | None:
    """Get info from table row. Return None if problem don't have enough information."""
    problem = schemas.Problem()
    for col_index, col in enumerate(row.find_all('td')):
        if col_index == 0:
            problem.id = col.find("a").text.strip()
        elif col_index == 1:
            problem.name = col.find("a").text.strip()
            problem.tags = []
            for tag in col.find_all("a", {"class": "notice"}):
                if tag.text not in problem.tags:
                    problem.tags.append(tag.text)
            if not problem.tags:
                return None
        elif col_index == 3:
            span = col.find("span")
            if span is None:
                return None
            problem.complexity = int(span.text.strip())
        elif col_index == 4:
            a = col.find("a")
            if a is None:
                return None
            problem.solve_count = int(a.text.strip()[1:])
    return problem


def page_processing(soup: BeautifulSoup, db_session: Session) -> None:
    for row in soup.find_all("tr")[1:-1]:
        problem = problem_processing(row)
        if problem is not None:
            db_problem = crud.get_problem_by_id(db_session, problem.id)
            if db_problem is None:
                # add problem to database if not exist
                crud.create_problem(db_session, problem)
            else:
                # update problem if exist
                crud.update_problem(db_session, db_problem, problem)
            print(problem.id)


async def main():
    from database.database_connector import get_session
    db_session = next(get_session())  # init session to work with database
    page_number = 1
    last_page = 1
    while page_number <= last_page:
        url_for_problems = URL + f"/page/{page_number}?&locale=ru"
        tag_soup = await get_bs_by_url(url_for_problems)
        if page_number == 1:  # Update last_page number if on page more than one page
            pages = tag_soup.find_all("span", {"class": "page-index"})
            if pages:
                last_page = int(pages[-1].text)
        page_processing(tag_soup, db_session)  # add and update tasks from page to database
        page_number += 1


if __name__ == '__main__':
    # from database.database_connector import init_models
    #
    # init_models()
    asyncio.run(main())
