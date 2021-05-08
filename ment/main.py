import argparse
import datetime
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import List

BASE_DIR = os.path.join(os.path.expanduser("~/ment_dir"))


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


def command_synthe(args):
    print(args.tag)
    tag = args.tag
    os.makedirs(os.path.join(BASE_DIR, "synthe", tag), exist_ok=True)
    dst_dir = os.path.join(BASE_DIR, "synthe", tag)
    # tag search
    synthesize_by_tag(tag, BASE_DIR, dst_dir)
    print("synthe END")
    exit()


def command_read(args):
    tag = args.tag
    read_file_path = Path(BASE_DIR) / "synthe" / tag / f"synthe_{tag}.md"
    if not read_file_path.exists():
        raise FileNotFoundError(
            f"Please run `m synthe {tag}` or `m week` before read command"
        )
    else:
        subprocess.run(["vim", read_file_path])


def command_week(args):
    combine_recent_docs_to_one(BASE_DIR)


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


def extract_content_for_tag_from_mkd(mkd_path, query_tag: str) -> List[str]:
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


def combine_recent_docs_to_one(base_dir, day_num=7):
    """
    週報作成
    """
    with open(Path(base_dir) / "synthe/week/synthe_week.md", "w") as f:
        for delta_day in range(day_num - 1, -1, -1):
            diary_path = (
                Path(base_dir)
                / str(datetime.date.today() - datetime.timedelta(delta_day))
                / "diary.md"
            )
            if diary_path.exists():
                with open(diary_path, "r") as f2:
                    mkd_content = f2.read()
                    f.write(mkd_content)
                print(diary_path)


def synthesize_by_tag(tag, src_dir, dst_dir):
    """synthesize_by_tag.
    タグに応じた文書を吸い上げて生成する

    Args:
        tag:統合するタグ
        src_dir:統合されるマークダウンを格納したディレクトリ群の親ディレクトリ
        dst_dir:生成するマークダウンの場所
    """
    src_mkd_dir = Path(src_dir)
    mkd_dir_paths = [
        mkd_dirs for mkd_dirs in src_mkd_dir.iterdir() if mkd_dirs.stem != "synthe"
    ]
    # 時系列順に眺めていきたい
    mkd_dir_paths.sort()
    p = Path(dst_dir)
    with open(p / f"synthe_{tag}.md", "w") as f:
        for src_mkd_dir in mkd_dir_paths:
            diary_path = Path(src_mkd_dir) / "diary.md"
            if diary_path.exists():
                clines = extract_content_for_tag_from_mkd(diary_path, tag)
                f.writelines(clines)
                if clines != []:
                    f.write("\n")
    return "a"


def main():
    """main."""
    args = get_args()
    if hasattr(args, "handler"):
        args.handler(args)
        return
    print("This is ment")
    os.makedirs(Path(BASE_DIR) / "synthe/week", exist_ok=True)
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
        print(f"{BASE_DIR=}")

    YYYY_MM_DD = str(datetime.date.today())

    title = "diary"
    file_name = title + ".md"
    os.makedirs(os.path.join(BASE_DIR, YYYY_MM_DD), exist_ok=True)
    file_path = os.path.join(BASE_DIR, YYYY_MM_DD, file_name)
    # edit
    # if not args.debug:
    #     start_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    #     with open(file_path, 'a') as f:
    #         f.write(f'> <!--started:{start_time}--!>\n')

    subprocess.run(["vim", file_path])

    # if not args.debug:
    #     finish_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    #     with open(file_path, 'a') as f:
    #         f.write(f'> <!--stopped:{finish_time}--!>\n')


if __name__ == "__main__":
    main()
