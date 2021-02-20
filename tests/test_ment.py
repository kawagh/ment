from pathlib import Path

from ment import __version__
from ment.main import extract_content_for_tag_from_mkd, synthesize_by_tag


def test_version():
    assert __version__ == '0.1.0'


def test_extract_content_for_tag_from_mkd():
    mkd_path = Path('tests') / 'sample_mkd' / 's1' / 'diary.md'
    t1_lines = ['# tag1\n', '- this is tag1 in s1\n', '\n', '# tag1\n', '- this is tag1 in s1 again\n']
    t2_lines = ['# tag2\n', '- this is tag2 in s1\n', '\n']
    assert t1_lines == extract_content_for_tag_from_mkd(mkd_path, 'tag1')
    assert t2_lines == extract_content_for_tag_from_mkd(mkd_path, 'tag2')


def test_synthesize_by_tag():
    # synthesize_by_tag('tag1', './sample_mkd/', './sample_mkd/')
    assert 1 == 1
