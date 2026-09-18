from backend.application.services.document_rag_service import DocumentRagService


def test_source_excerpt_ends_at_last_complete_sentence_before_limit():
    source = "First complete sentence. " + ("A long unfinished sentence " * 20)

    excerpt = DocumentRagService._sentence_bounded_excerpt(source, limit=80)

    assert excerpt == "First complete sentence. …"


def test_source_excerpt_looks_ahead_when_sentence_crosses_limit():
    source = ("word " * 18) + "the first sentence ends here. Next sentence."

    excerpt = DocumentRagService._sentence_bounded_excerpt(source, limit=80)

    assert excerpt.endswith(". …")
    assert "Next sentence." not in excerpt


def test_source_excerpt_falls_back_to_a_word_boundary_without_punctuation():
    source = "word " * 100

    excerpt = DocumentRagService._sentence_bounded_excerpt(source, limit=80)

    assert excerpt.endswith(" …")
    assert not excerpt[:-2].endswith(" ")
