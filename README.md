# ment

## what is this?

`ment` is a tool to

- write daily logs in markdown quickly
- synthesize daily logs based on category

    Synthesizing daily logs is like sorting loose-leaf notebook.


## installation

```
pip install ment
```

## usage

### start editting

```
m  # just type `m<Enter>`
```

It means `vim ~/ment_dir/<todays_date>/diary.md`

### synthesize by tag

```
m synthe <tag_name>
```

Then, it extracts contents followed by "# <tag_name>" from daily logs,
and outputs `~/ment_dir/synthe/<tag_name>/synthe_<tag_name>.md`.

If you want to list tags,`m list`

### directory structure

```
~/ment_dir/
├── 2021-03-27
│   └── diary.md
├── 2021-03-28
│   └── diary.md
├── 2021-03-29
│   └── diary.md
├── 2021-03-30
│   └── diary.md
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


```
cat bash_completion_for_ment >>  ~/.bash_completion
source ~/.bashrc
```

