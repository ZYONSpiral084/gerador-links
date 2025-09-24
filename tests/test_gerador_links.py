import pytest
from src.gerador_links_advanced_auth import safe_format, build_url_from_template, gerar_links_iter, UnsafeTemplateError

def test_safe_format_padding_and_spec():
    assert safe_format("{n:03d}", 5, pad=0) == "005"
    assert safe_format("{n}", 5, pad=3) == "005"
    assert safe_format("Cap {n}", 12, pad=0) == "Cap 12"

def test_build_url_auto_scheme():
    u = build_url_from_template("example.com/page/{n}", 2, pad=2)
    assert u.startswith("http://")
    assert "02" in u

def test_generator_step_and_range():
    g = list(gerar_links_iter("http://x/{n}", 1, 5, pad=0, step=2))
    assert [i["n"] for i in g] == [1, 3, 5]

def test_unsafe_template_rejected():
    with pytest.raises(UnsafeTemplateError):
        list(gerar_links_iter("http://x/{n.__class__}", 1, 2))