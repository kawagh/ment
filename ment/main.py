import argparse
import datetime
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import List

# config
if os.environ.get("MENT_DIR") is None:
    BASE_DIR = Path.home() / "ment_dir"
else:
    BASE_DIR = Path(os.environ.get("MENT_DIR"))
if os.environ.get("MENT_EDITOR") is None:
    MENT_EDITOR = "vim"
else:
    MENT_EDITOR = os.environ.get("MENT_EDITOR")


def get_args():
    """get_args."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser("list", help="list names of tags")
    parser_list.set_defaults(handler=command_list)

    parser_synthe = subparsers.add_parser(
        "synthe", help="synthesize from daily.md files by tag"
    )
    parser_synthe.add_argument(
        "tag",
        type=str,
        help="synthesize from daily.md files by tag",
    )
    parser_synthe.set_defaults(handler=command_synthe)

    parser_week = subparsers.add_parser(
        "week", help="output notes of recent 7 days")
    parser_week.set_defaults(handler=command_week)

    parser_read = subparsers.add_parser(
        "read", help="open tag-synthesized file for reading"
    )
    parser_read.add_argument(
        "tag",
        type=str,
        help="open tag-synthesized file for reading",
    )
    parser_read.set_defaults(handler=command_read)
    args = parser.parse_args()
    return args


def command_list(args):
    list_tags(BASE_DIR)
    exit()


def command_synthe(args):
    tag = args.tag
    dst_dir: Path = BASE_DIR / "synthe" / tag
    dst_dir.mkdir(parents=True, exist_ok=True)
    # tag search
    synthesize_by_tag(tag, BASE_DIR, dst_dir)
    exit()


def command_read(args):
    tag = args.tag
    read_file_path = Path(BASE_DIR) / "synthe" / tag / f"synthe_{tag}.md"
    if not read_file_path.exists():
        raise FileNotFoundError(
            f"Please run `m synthe {tag}` or `m week` before read command"
        )
    else:
        subprocess.run([MENT_EDITOR, read_file_path])


def command_week(args):
    combine_recent_docs_to_one(BASE_DIR)
    exit()


def _extract_tags(mkd_path) -> List[str]:
    pattern = r"^# .*\n$"
    compiled_ptn = re.compile(pattern)
    tags = []
    with mkd_path.open("r") as f:
        line = f.readline()
        while line:
            # 正規表現で見出し抽出
            if compiled_ptn.match(line):
                tag = "".join(line.split(" ")[1:]).rstrip()
                tags.append(tag)
            line = f.readline()
    return tags


def list_tags(src_dir):
    """
    日付ごとにタグを列挙
    """
    src_mkd_dir = Path(src_dir)
    mkd_dir_paths = [
        mkd_dirs for mkd_dirs in src_mkd_dir.iterdir() if mkd_dirs.stem != "synthe"
    ]
    # 時系列順に眺めていきたい
    tag_cnt = Counter()
    mkd_dir_paths.sort()
    for src_mkd_dir in mkd_dir_paths:
        diary_path = src_mkd_dir / "diary.md"
        if diary_path.exists():
            tags = _extract_tags(diary_path)
            print(f"\033[32m{src_mkd_dir}\33[0m", tags)
            tag_cnt += Counter(tags)
    print(tag_cnt)


def extract_content_for_tag_from_mkd(mkd_path: Path, query_tag: str) -> List[str]:
    pattern = r"^# .*\n$"
    compiled_ptn = re.compile(pattern)
    contents_lines = []
    is_in_content_of_the_tag = False
    with mkd_path.open("r") as f:
        line = f.readline()
        while line:
            # 正規表現で見出し抽出
            if compiled_ptn.match(line):
                tag = line.split(" ")[1].rstrip()
                if tag == query_tag and not is_in_content_of_the_tag:
                    is_in_content_of_the_tag = True
                elif tag != query_tag and is_in_content_of_the_tag:
                    is_in_content_of_the_tag = False
                else:
                    pass
            elif is_in_content_of_the_tag:
                # タグの名前は含めない
                # write
                contents_lines.append(line)
            else:
                # dont write
                pass

            line = f.readline()
    return contents_lines


def make_header(diary_path: Path) -> List[str]:
    header = [
        "# " + diary_path.parent.name + "\n\n",
    ]  # 抽出元ファイル
    return header


def combine_recent_docs_to_one(base_dir: Path, day_num=7):
    """
    週報作成
    """
    output_file = base_dir / "synthe/week/synthe_week.md"
    with open(output_file, "w") as f:
        for delta_day in range(day_num - 1, -1, -1):
            diary_path = (
                base_dir
                / str(datetime.date.today() - datetime.timedelta(delta_day))
                / "diary.md"
            )
            if diary_path.exists():
                with open(diary_path, "r") as f2:
                    mkd_content = f2.read()
                header = make_header(diary_path)
                f.writelines(header)
                f.write(mkd_content)
                f.write("\n")
                print(diary_path)
    print("Extracted.")
    print()
    print(f"output to  {output_file}")
    print(
        "To access to the file, \
`m read week`"
    )


def synthesize_by_tag(tag: str, src_dir: Path, dst_dir: Path):
    """synthesize_by_tag.
    タグに応じた文書を吸い上げて生成する

    Args:
        tag:統合するタグ
        src_dir:統合されるマークダウンを格納したディレクトリ群の親ディレクトリ
        dst_dir:生成するマークダウンの場所
    """
    mkd_dir_paths = [
        mkd_dir for mkd_dir in src_dir.iterdir() if mkd_dir.stem != "synthe"
    ]
    # 時系列順に眺めていきたい
    mkd_dir_paths.sort()
    p = Path(dst_dir)
    output_file = p / f"synthe_{tag}.md"

    print(f"Extracting tag `{tag}` from")
    with open(output_file, "w") as f:
        for src_mkd_dir in mkd_dir_paths:
            diary_path = Path(src_mkd_dir) / "diary.md"
            if diary_path.exists():
                header = make_header(diary_path)
                clines = extract_content_for_tag_from_mkd(diary_path, tag)
                if len(clines) != 0:
                    print(diary_path)
                    f.writelines(header)
                    f.writelines(clines)
                    f.write("\n")
    print("Extracted.")
    print()
    print(f"output to  {output_file}")
    print(
        f"To access to the file, \
`m read {tag}`"
    )
    return "a"


def main():
    """main."""
    args = get_args()
    if hasattr(args, "handler"):
        args.handler(args)
    print("This is ment")
    Path(BASE_DIR / "synthe/week").mkdir(exist_ok=True, parents=True)

    YYYY_MM_DD = str(datetime.date.today())

    title = "diary"
    file_name = title + ".md"
    Path(BASE_DIR / YYYY_MM_DD).mkdir(exist_ok=True)
    file_path = BASE_DIR / YYYY_MM_DD / file_name

    subprocess.run([MENT_EDITOR, file_path])


if __name__ == "__main__":
    main()
