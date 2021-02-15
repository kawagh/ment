import datetime
import os
import subprocess


def main():
    print("This is ment")
    BASE_DIR = os.path.join(os.path.expanduser('~/ment_dir'))
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
        print(f'{BASE_DIR=}')
    YYYY_MM_DD = str(datetime.date.today())

    # title = input("Title:")
    title = 'diary'
    file_name = title + '.md'
    os.makedirs(os.path.join(BASE_DIR, YYYY_MM_DD), exist_ok=True)
    file_path = os.path.join(BASE_DIR, YYYY_MM_DD, file_name)
    # edit
    start_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    with open(file_path, 'a') as f:
        f.write(f'<!--started:{start_time}--!>\n')

    subprocess.run(['vim', file_path])

    finish_time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    with open(file_path, 'a') as f:
        f.write(f'<!--stopped:{finish_time}--!>\n')


if __name__ == '__main__':
    main()
