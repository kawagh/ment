import subprocess
from pathlib import Path

from ment import __version__
from ment.main import (_extract_tags, extract_content_for_tag_from_mkd,
                       list_tags, synthesize_by_tag)


def test_version():
    assert __version__ == '0.1.2'


def test_extract_content_for_tag_from_mkd():
    mkd_path = Path('tests/sample_mkd/20200219/diary.md')
    t1_lines = ['- this is tag1 in 20200219\n',
                '\n', '- this is tag1 in 20200219 again\n']
    # t2_lines = ['# tag2\n', '- this is tag2 in 20200219\n', '\n']
    t2_lines = ['- this is tag2 in 20200219\n', '\n']
    assert t1_lines == extract_content_for_tag_from_mkd(mkd_path, 'tag1')
    assert t2_lines == extract_content_for_tag_from_mkd(mkd_path, 'tag2')


def test_synthesize_by_tag():
    '''
    tagを指定して合成したファイルと所望のファイルの差分がないか調べる
    '''
    synthesize_by_tag('tag1', 'tests/sample_mkd/', 'tests/sample_mkd/synthe/')
    ret_code = subprocess.run(['diff', '-s', 'tests/sample_mkd/synthe/synthe_tag1.md',
                               'tests/sample_mkd/target_synthe/synthe_tag1.md']).returncode
    assert ret_code == 0


def test__extract_tags():
    tags = _extract_tags(Path('tests/sample_mkd/20200219/diary.md'))
    assert tags == ['tag1', 'tag2', 'tag1']
    list_tags(Path('tests/sample_mkd'))
