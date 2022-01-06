from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import List


class CFG:
    def __init__(self):
        if os.environ.get("MENT_DIR"):
            self.BASE_DIR = Path(os.environ.get("MENT_DIR"))  # type:ignore
        else:
            self.BASE_DIR: Path = Path.home() / "ment_dir"
        if os.environ.get("MENT_EDITOR"):
            self.MENT_EDITOR = os.environ.get("MENT_EDITOR")  # type:ignore
        else:
            self.MENT_EDITOR: str = "vim"


def get_args():
    """get_args."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser("list", help="list names of tags")
    parser_list.set_defaults(handler=command_list)

    parser_synthe = subparsers.add_parser("synthe", help="synthesize from daily.md files by tag")
    parser_synthe.add_argument(
        "tag",
        type=str,
        help="synthesize from daily.md files by tag",
    )
    parser_synthe.set_defaults(handler=command_synthe)

    parser_week = subparsers.add_parser("week", help="output notes of recent 7 days")
    parser_week.set_defaults(handler=command_week)

    parser_read = subparsers.add_parser("read", help="open tag-synthesized file for reading")
    parser_read.add_argument(
        "tag",
        type=str,
        help="open tag-synthesized file for reading",
    )
    parser_read.set_defaults(handler=command_read)

    parser_list = subparsers.add_parser("update", help="update all synthesized documents")
    parser_list.set_defaults(handler=command_update)

    args = parser.parse_args()

    return args


def command_list(_):
    cfg = CFG()
    list_tags(cfg.BASE_DIR)
    exit()


def command_update(_):
    """
    合成ファイルの一括更新
    ```
    m week
    m synthe {any tag}
    ```
    """
    cfg = CFG()
    combine_recent_docs_to_one(cfg.BASE_DIR)
    for dst_dir in (cfg.BASE_DIR / "synthe").iterdir():
        tag = dst_dir.stem
        # week,externalはtagとして扱えない
        if tag == "week" or tag == "external":
            continue
        synthesize_by_tag(dst_dir.stem, cfg.BASE_DIR, dst_dir)
    exit()


def command_synthe(args):
    cfg = CFG()
    tag = args.tag
    dst_dir: Path = cfg.BASE_DIR / "synthe" / tag
    dst_dir.mkdir(parents=True, exist_ok=True)
    # tag search
    synthesize_by_tag(tag, cfg.BASE_DIR, dst_dir)
    exit()


def command_read(args):
    cfg = CFG()
    tag = args.tag
    read_file_path = Path(cfg.BASE_DIR) / "synthe" / tag / f"synthe_{tag}.md"
    if not read_file_path.exists():
        raise FileNotFoundError(f"Please run `m synthe {tag}` or `m week` before read command")
    else:
        subprocess.run([cfg.MENT_EDITOR, read_file_path])
        exit()


def command_week(_):
    cfg = CFG()
    combine_recent_docs_to_one(cfg.BASE_DIR)
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
    mkd_dir_paths = [mkd_dirs for mkd_dirs in src_mkd_dir.iterdir() if mkd_dirs.stem != "synthe"]
    # 時系列順に眺めていきたい
    tag_cnt = Counter()
    mkd_dir_paths.sort()
    for src_mkd_dir in mkd_dir_paths:
        file_name = src_mkd_dir.name + ".md"
        diary_path = src_mkd_dir / file_name
        if not diary_path.exists():
            diary_path = src_mkd_dir / "diary.md"

        if diary_path.exists():
            tags = _extract_tags(diary_path)
            print(f"\033[32m{src_mkd_dir.stem}\33[0m")
            print(*tags, sep="\n")
            tag_cnt += Counter(tags)
    # print(tag_cnt)


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


def make_header(diary_path: Path) -> list[str]:
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
            date = str(datetime.date.today() - datetime.timedelta(delta_day))
            diary_path = base_dir / date / f"{date}.md"
            if not diary_path.exists():
                diary_path = base_dir / date / "diary.md"
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

    mkd_dir_paths: list[Path] = [mkd_dir for mkd_dir in src_dir.iterdir() if mkd_dir.stem != "synthe"]
    # 時系列順に眺めていきたい
    mkd_dir_paths.sort()
    dst_dir.mkdir(parents=True, exist_ok=True)
    output_file = dst_dir / f"synthe_{tag}.md"

    print(f"Started Extracting tag `{tag}` from ...")
    has_content = False
    with open(output_file, "w") as f:
        for src_mkd_dir in mkd_dir_paths:
            diary_path = Path(src_mkd_dir) / f"{src_mkd_dir.name}.md"

            if not diary_path.exists():
                diary_path = Path(src_mkd_dir) / "diary.md"
            if diary_path.exists():
                header = make_header(diary_path)
                clines = extract_content_for_tag_from_mkd(diary_path, tag)
                if len(clines) != 0:
                    has_content = True
                    print(diary_path)
                    f.writelines(header)
                    f.writelines(clines)
                    f.write("\n")
    if not has_content:
        output_file.unlink()
        dst_dir.rmdir()
        print("contents tagged `{tag}` not found")
    else:
        print("Extracted.")
        print()
        print(f"output to  {output_file}")
        print(
            f"To access to the file, \
    `m read {tag}`"
        )


def main():
    """main."""
    args = get_args()
    cfg = CFG()
    if hasattr(args, "handler"):
        args.handler(args)
    print("This is ment")
    Path(cfg.BASE_DIR / "synthe/week").mkdir(exist_ok=True, parents=True)

    YYYY_MM_DD = str(datetime.date.today())

    file_name = YYYY_MM_DD + ".md"
    Path(cfg.BASE_DIR / YYYY_MM_DD).mkdir(exist_ok=True)
    file_path = cfg.BASE_DIR / YYYY_MM_DD / file_name

    subprocess.run([cfg.MENT_EDITOR, file_path])


if __name__ == "__main__":
    main()
