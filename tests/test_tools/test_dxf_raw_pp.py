import pytest

from ezdxf.templates import TemplateLoader
from ezdxf.options import options
from ezdxf.lldxf.tagger import low_level_tagger

from ezdxf.pp.rawpp import rawpp

finder = TemplateLoader(options.template_dir)


@pytest.fixture(scope='module', params=['AC1009', 'AC1015'])
def tags(request):
    stream = finder.getstream(request.param)
    return low_level_tagger(stream)


def test_raw_dxf_tags_to_html(tags):
    # checks only if pretty printer is still working
    result = rawpp(tags, filename='test.dxf')
    assert len(result) > 0


if __name__ == '__main__':
    pytest.main([__file__])

