import sys
from io import StringIO
from typing import Callable, Optional, Final, Dict
import json
import pkgutil

import requests
from bs4 import BeautifulSoup as bs

__all__ = ["test", "set_open", "set_input"]


class Problem:
    DEFAULT_HEADER: Dict[str, str] = json.loads(
        pkgutil.get_data(__name__, "static/default_header.json")
    )

    def __init__(self, num: int):
        self.num: Final[int] = num
        self.url: Final[str] = f"https://www.acmicpc.net/problem/{num}"

        match self.__get_response().status_code:
            case 200:
                self.set_soup()
                self.set_title()
                self.set_examples()
            case 404:
                raise ValueError(f"{num}번 문제는 존재하지 않습니다.")
            case 403:
                raise PermissionError(f"잘못된 접근입니다. 헤더를 수정해주세요.")
            case status_code:
                raise ConnectionError(f"연결에 문제가 있습니다. 상태코드: {status_code}")

    def __get_response(
        self, headers: Dict[str, str] = DEFAULT_HEADER
    ) -> requests.Response:
        __response: requests.Response = requests.get(
            self.url,
            headers=headers,
        )
        return __response

    def set_soup(self):
        self.soup = bs(self.__get_response().text, "html.parser")

    def set_title(self):
        self.title = self.soup.select_one("#problem_title").text

    class Example:
        counter = 0

        @classmethod
        def count(cls) -> None:
            cls.counter += 1

        def __init__(self, problem: "Problem", elem: bs):
            self.elem = elem
            self.input, self.output = map(self.text_extracrt, elem.select("pre"))
            if self.output.endswith("\n"):
                self.output = self.output.rstrip()
            problem.Example.count()
            self.num = problem.Example.counter
            self.problem = problem

        @staticmethod
        def text_extracrt(io_elem: bs) -> str:
            return io_elem.text.replace("\r\n", "\n")

        def __str__(self):
            return f"{self.input} # {self.output}"

        def __repr__(self):
            return f"< [{self.problem.num}번 {self.problem.title}]({self.problem.url}) {self.num} 번 예제 at {hex(id(self))}>"

    def set_examples(self):
        content_selector = "#problem-body > div.col-md-12"
        contents = self.soup.select(content_selector)
        copy_button_selector = "button.copy-button"
        self.examples = [
            Problem.Example(self, elem)
            for elem in contents
            if elem.select(copy_button_selector)
        ]

    def h1(self):
        return f"# [백준/{self.title}]({self.url})"

    def __str__(self):
        return f"{self.num}번 {self.title}"

    def __repr__(self):
        return f"< [{self.num}번 {self.title}]({self.url}) at {hex(id(self))}>"


def test(solution: Callable[[], None]) -> Callable[[Optional[str]], None]:
    def test_example(example: Optional[str] = None) -> None:
        sys.stdin = StringIO(example)
        solution()

    return test_example


def set_open(example: str) -> StringIO:
    return StringIO(example)


def set_input(example: str):
    return StringIO(example).readline
