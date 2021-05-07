# ment
## what is this?
ment is a python library to write daily log in markdown quickly and to synthesize daily logs based on category.

## prerequisities
- vim
## installation
```
pip install ment
```
## usage
#### start editting
```
m
```
Then, starts to edit `~/ment_dir/<todays_date>/diary.md`

#### synthesize by tag
```
m synthe <tag_name>
```
Then, it extracts contents followed by "# <tag_name>" from daily logs,
and outputs `~/ment_dir/synthe/<tag_name>/synthe_<tag_name>.md`.

If you want to list tags,`m list`


## directory structure
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
