import pytest
from typing import Tuple
from bs4 import BeautifulSoup, Tag

from iframe_processing import pre_process_iframes_from_html, post_process_iframes_to_markdown


@pytest.fixture
def raw_content() -> str:
    return '</div><div></div><div><iframe src="https://www.youtube.com/embed/SqdxNUMO2cg" width="420" height="315" frameborder="0" allowfullscreen="" youtube="true" anchorhref="https://www.youtube.com/watch?v=SqdxNUMO2cg">&nbsp;</iframe></div><div>'


def test_pre_process_iframes_from_html(raw_content):
    processed_content, iframes_dict = pre_process_iframes_from_html(raw_content)

    assert 'iframe-placeholder-id-' in processed_content
    for key, value in iframes_dict.items():
        assert 'iframe-placeholder-id-' in key
        assert isinstance(value, Tag)
        assert '<iframe allowfullscreen="" anchorhref="https://www.youtube.com/watch?v=SqdxNUMO2cg" frameborder="0" height="315" src="https://www.youtube.com/embed/SqdxNUMO2cg" width="420" youtube="true"> </iframe>' in str(value)


@pytest.fixture
def post_fixture() -> Tuple[str, Tag, dict, str]:
    raw_md_content = '# heading1\niframe-placeholder-id-123456\n#heading2'
    raw_html = '</div><div></div><div><iframe src="https://www.youtube.com/embed/SqdxNUMO2cg" width="420" height="315" frameborder="0" allowfullscreen="" youtube="true" anchorhref="https://www.youtube.com/watch?v=SqdxNUMO2cg">&nbsp;</iframe></div><div>'
    soup = BeautifulSoup(raw_html, 'html.parser')
    iframe_tag = soup.select('iframe')[0]
    iframes_dict = {'iframe-placeholder-id-123456': iframe_tag}
    result = '# heading1\n\n<iframe allowfullscreen="" anchorhref="https://www.youtube.com/watch?v=SqdxNUMO2cg" frameborder="0" height="315" src="https://www.youtube.com/embed/SqdxNUMO2cg" width="420" youtube="true"> </iframe>\n\n#heading2'
    return raw_md_content, iframes_dict, result


def test_post_process_iframes_to_markdown(post_fixture):
    post_content = post_process_iframes_to_markdown(post_fixture[0], post_fixture[1])
    assert post_fixture[2] == post_content
    pass
