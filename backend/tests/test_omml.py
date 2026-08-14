from lxml import etree

from backend.infrastructure.converter.omml import (
    A14_NS,
    M_NS,
    latex_to_omml,
)


def test_latex_is_converted_to_editable_omml_structures():
    slash = chr(92)
    formula = (
        slash
        + "mathcal{L}_{CE} = -"
        + slash
        + "sum_{i=1}^{C} y_i "
        + slash
        + "log("
        + slash
        + "hat{y}_i)"
    )

    wrapper = latex_to_omml(formula, color="#2C3E50", size_pt=20)

    assert wrapper is not None
    assert wrapper.tag == f"{{{A14_NS}}}m"
    assert wrapper.find(f".//{{{M_NS}}}oMathPara") is not None
    assert wrapper.find(f".//{{{M_NS}}}f") is None
    assert wrapper.find(f".//{{{M_NS}}}nary") is not None
    assert wrapper.find(f".//{{{M_NS}}}sSub") is not None
    assert "\\mathcal" not in etree.tostring(wrapper, encoding="unicode")


def test_fraction_and_radical_are_native_math_nodes():
    slash = chr(92)
    formula = "x = " + slash + "frac{-b " + slash + "pm " + slash + "sqrt{b^2-4ac}}{2a}"

    wrapper = latex_to_omml(formula)

    assert wrapper is not None
    assert wrapper.find(f".//{{{M_NS}}}f") is not None
    assert wrapper.find(f".//{{{M_NS}}}rad") is not None
    assert wrapper.find(f".//{{{M_NS}}}sSup") is not None
