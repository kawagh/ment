import argparse
import datetime
import os
import re
import subprocess
from typing import List


def get_args():
    """get_args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--synthe')
    args = parser.parse_args()
    return args


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
    dst_mkd_file = os.path.join(dst_dir, tag + '.md')
    with open(dst_mkd_file, 'a') as f:
        f.write(f'# {tag}\n')
        # TODO
        # タグに関わる文書を生成していく
        days = os.listdir(src_dir)
        print(days)
        days.sort()
        print(days)
        for day in days:
            print(day)
            if day == 'synthe':
                continue
            src_mkd_file = os.path.join(src_dir, day, 'diary.md')
            # TODO 見出しを段落でスプリットして行番号ごとにcat
            subprocess.run(['cat', src_mkd_file])


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
