import argparse
import datetime
import os
import re
import subprocess
from pathlib import Path
from typing import List


def get_args():
    """get_args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='stop logging time ')
    parser.add_argument('-l', '--list', action='store_true', help='list names of tag')
    parser.add_argument('--synthe', help='synthesize from daily.md files by tag')
    args = parser.parse_args()
    return args


def _extract_tags(mkd_path) -> List[str]:
    pattern = r'^# .*\n$'
    compiled_ptn = re.compile(pattern)
    tags = []
    with mkd_path.open('r') as f:
        line = f.readline()
        while line:
            # 正規表現で見出し抽出
            if compiled_ptn.match(line):
                tag = ''.join(line.split(' ')[1:]).rstrip()
                tags.append(tag)
            line = f.readline()
    return tags


def list_tags(src_dir):
    '''
    日付ごとにタグを列挙
    '''
    src_mkd_dir = Path(src_dir)
    mkd_dir_paths = [mkd_dirs for mkd_dirs in src_mkd_dir.iterdir() if mkd_dirs.stem != 'synthe']
    # 時系列順に眺めていきたい
    mkd_dir_paths.sort()
    for src_mkd_dir in mkd_dir_paths:
        diary_path = src_mkd_dir / 'diary.md'
        if diary_path.exists():
            tags = _extract_tags(diary_path)
            print(src_mkd_dir, tags)


def extract_content_for_tag_from_mkd(mkd_path, query_tag: str) -> List[str]:
    pattern = r'^# .*\n$'
    compiled_ptn = re.compile(pattern)
    tags = []
    contents_lines = []
    is_in_content_of_the_tag = False
    with mkd_path.open('r') as f:
        line = f.readline()
        while line:
            # 正規表現で見出し抽出
            if compiled_ptn.match(line):
                tag = line.split(' ')[1].rstrip()
                tags.append(tag)
                if tag == query_tag and not is_in_content_of_the_tag:
                    is_in_content_of_the_tag = True
                elif tag != query_tag and is_in_content_of_the_tag:
                    is_in_content_of_the_tag = False
            if is_in_content_of_the_tag:
                # write
                contents_lines.append(line)
            else:
                # dont write
                pass

            line = f.readline()
    return contents_lines


def synthesize_by_tag(tag, src_dir, dst_dir):
    """synthesize_by_tag.
    タグに応じた文書を吸い上げて生成する

    Args:
        tag:統合するタグ
        src_dir:統合されるマークダウンを格納したディレクトリ群の親ディレクトリ
        dst_dir:生成するマークダウンの場所
    """
    src_mkd_dir = Path(src_dir)
    mkd_dir_paths = [mkd_dirs for mkd_dirs in src_mkd_dir.iterdir() if mkd_dirs.stem != 'synthe']
    # 時系列順に眺めていきたい
    mkd_dir_paths.sort()
    p = Path(dst_dir)
    with open(p / f'synthe_{tag}.md', 'w') as f:
        for src_mkd_dir in mkd_dir_paths:
            diary_path = Path(src_mkd_dir) / 'diary.md'
            if diary_path.exists():
                clines = extract_content_for_tag_from_mkd(diary_path, tag)
                f.writelines(clines)
                if clines != []:
                    f.write('\n')
    return 'a'


def main():
    """main.
    """
    args = get_args()
    print("This is ment")
    BASE_DIR = os.path.join(os.path.expanduser('~/ment_dir'))
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
        print(f'{BASE_DIR=}')

    if args.synthe is not None:
        tag = args.synthe
        os.makedirs(os.path.join(BASE_DIR, 'synthe', tag), exist_ok=True)
        dst_dir = os.path.join(BASE_DIR, 'synthe', tag)
        # tag search
        synthesize_by_tag(tag, BASE_DIR, dst_dir)
        print(args.synthe)
        print("synthe END")
        exit()
    elif args.list:
        list_tags(BASE_DIR)
        exit()
        # show_tags()

    YYYY_MM_DD = str(datetime.date.today())

    # title = input("Title:")
    title = 'diary'
    file_name = title + '.md'
    os.makedirs(os.path.join(BASE_DIR, YYYY_MM_DD), exist_ok=True)
    file_path = os.path.join(BASE_DIR, YYYY_MM_DD, file_name)
    # edit
    if not args.debug:
        start_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
        with open(file_path, 'a') as f:
            f.write(f'> <!--started:{start_time}--!>\n')

    subprocess.run(['vim', file_path])

    if not args.debug:
        finish_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
        with open(file_path, 'a') as f:
            f.write(f'> <!--stopped:{finish_time}--!>\n')


if __name__ == '__main__':
    main()
