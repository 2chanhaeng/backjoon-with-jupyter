import json
import os
import pkgutil
import sys

from bwj import Problem

match sys.argv:
    case [_]:
        num = int(input("문제 번호를 입력하세요.: "))
    case [_, num]:
        num = int(num)
    case _:
        raise ValueError("Usage: python3 -m bwj <problem_number>")
problem = Problem(num)

raw_template = pkgutil.get_data(__name__, "static/template.json")
template = json.loads(raw_template)
template["cells"][0]["source"] = problem.h1()


for example in problem.examples:
    input_line = f'test_solution("""{example.input}""")'

    if example.output.find("\n") == -1:
        output_line = f" # {example.output}"
        source = [input_line + output_line]
    else:
        output_line = "\n# ".join(["# answer:", *example.output.split("\n")])
        source = [input_line, output_line]

    template["cells"].append(
        {"cell_type": "code", "execution_count": None, "metadata": {}, "source": source}
    )

# 만약 solving 폴더가 없다면 생성할 지를 묻고 "yes" 라면 생성
if not os.path.exists("./solving"):
    print("solving 폴더가 없습니다. 생성하시겠습니까? (y/n)")
    if input() == "y":
        os.mkdir("./solving")
    else:
        sys.exit()

fn = f"{num}.ipynb"
# 만약 solving 폴더에 이미 파일이 있다면 덮어쓸 지를 묻고 "y" 라면 덮어쓰기
if os.path.exists(f"./solving/{fn}"):
    print(
        f"solving 폴더에 {num}번 문제의 풀이가 이미 있습니다. 덮어쓰시겠습니까?\n"
        "(y: 덮어쓰기, n: 저장 취소 및 종료, 그 외: 해당 이름으로 저장)"
    )
    match input():
        case "y":
            fn = f"{num}.ipynb"
        case "n":
            sys.exit()
        case filename:
            while set(filename) & set('/\\:*?."<>|') or os.path.exists(
                f"./solving/{filename}.ipynb"
            ):
                if set(filename) & set('/\\:*?."<>|'):
                    print(
                        "파일 이름에 사용할 수 없는 특수문자가 포함되어 있습니다.",
                        '/\\:*?."<>|를 제외하여 다시 입력해주세요. (n: 저장 취소 및 종료)',
                    )
                elif os.path.exists(f"./solving/{filename}.ipynb"):
                    print(
                        "이미 같은 이름의 파일이 존재합니다.",
                        "다시 입력해주세요.",
                        "(n: 저장 취소 및 종료)",
                    )
                filename = input()
                if filename == "n":
                    sys.exit()

            fn = f"{filename}.ipynb"

with open(f"solving/{fn}", "w", encoding="utf-8") as f:
    json.dump(template, f, indent=2, ensure_ascii=False)
