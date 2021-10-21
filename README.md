
# ment

## What is this?

`ment` is a tool to

- write daily logs in markdown quickly
- synthesize daily logs based on category

    Synthesizing daily logs is like sorting loose-leaf notebook.

![image](https://user-images.githubusercontent.com/45124565/126846109-ab4e804e-45e8-4053-a72c-12cfcffdf8d6.png)




## Installation

```sh
pip install ment
```

## Usage

### start editting

```sh
m
```

Type `m<Enter>`.

Default,it means `vim ~/ment_dir/<todays_date>/diary.md`
If you want to switch editor, look [configuration](#configuration)


### synthesize by tag

```sh
m synthe <tag_name>
```

Then, it extracts contents followed by "# <tag_name>" from daily logs,
and outputs `~/ment_dir/synthe/<tag_name>/synthe_<tag_name>.md`.

If you want to list tags,`m list`.

To synthesize recent 7days document,`m week`.
It outputs `~/ment_dir/synthe/week/synthe_week.md`.

To read synthesized documents,`m read <tag_name>`.

To update already synthesized documents, `m update`.

### configuration

If you want to change editor and directory, please set environment variable.

```sh
export MENT_DIR="/path/to/documents" 
export MENT_EDITOR="your editor"
```

Default,MENT_DIR is `~/ment_dir/`

### directory structure

```text
~/ment_dir/
├── 2021-03-27
│   └── 2021-03-27.md
├── 2021-03-28
│   └── 2021-03-28.md
├── 2021-03-29
│   └── 2021-03-29.md
├── 2021-03-30
│   └── 2021-03-30.md
└── synthe
    ├── tag1
    │   └── synthe_tag1.md
    ├── tag2
    │   └── synthe_tag2.md
    ├── tag3
    │   └── synthe_tag3.md
    └── weeks.md

```


### completion

bash-completion file for `ment` is `bash_completion_for_ment`.


```sh
cat bash_completion_for_ment >>  ~/.bash_completion
source ~/.bashrc
```

