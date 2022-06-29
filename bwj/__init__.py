import sys
from io import StringIO
from typing import Any, Callable, Container, Iterator, Optional, Final

import requests
from bs4 import BeautifulSoup as bs

__all__ = ["test"]


class Problem:
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

    def __get_response(self) -> requests.Response:
        __response: requests.Response = requests.get(self.url, headers={
            "Host": "www.acmicpc.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
        })
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
            print(self.output)
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
        self.examples = [Problem.Example(self, elem) for elem in contents if elem.select(copy_button_selector)]

    def h1(self):
        return f"# [백준/{self.title}]({self.url})"

    def __str__(self):
        return f"{self.num}번 {self.title}"
    
    def __repr__(self):
        return f"< [{self.num}번 {self.title}]({self.url}) at {hex(id(self))}>"


def test(solution: Callable[[Callable], None]) -> Callable[[Optional[str]], None]:
    def test_example(example: Optional[str] = None) -> None:
        sys.stdin = StringIO(example)
        solution()
    return test_example
