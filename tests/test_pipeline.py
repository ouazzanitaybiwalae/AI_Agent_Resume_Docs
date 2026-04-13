# tests/test_pipeline.py
# Tests du pipeline NLP complet

import pytest
import os
import sys

# Ajouter le dossier racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.chunk_text import chunk_text, chunk_text_by_paragraphs, count_tokens
from src.summarize import summarize_single_chunk, summarize_chunks
from src.merge import merge_summaries, run_full_pipeline


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def short_text():
    return "L'intelligence artificielle transforme le monde moderne grâce aux algorithmes."

@pytest.fixture
def medium_text():
    return """
    L'intelligence artificielle (IA) est un domaine de l'informatique qui cherche à reproduire
    des capacités cognitives humaines dans des machines. Elle repose sur des techniques comme
    le machine learning et le deep learning.

    Le machine learning permet aux algorithmes d'apprendre à partir de données sans être
    explicitement programmés pour chaque tâche. Les réseaux de neurones artificiels imitent
    le fonctionnement du cerveau humain.

    Les applications de l'IA sont nombreuses : reconnaissance vocale, traduction automatique,
    conduite autonome, diagnostic médical, et bien d'autres domaines en pleine expansion.
    """ * 3

@pytest.fixture
def long_text():
    """Texte long pour tester le chunking (>3000 tokens simulé par répétition)."""
    paragraph = """
    L'intelligence artificielle révolutionne de nombreux secteurs industriels et académiques.
    Les modèles de langage comme GPT et Claude transforment la façon dont les humains
    interagissent avec les machines. Ces systèmes apprennent à partir de milliards de
    paramètres entraînés sur des corpus massifs de textes en plusieurs langues.
    Les défis éthiques sont nombreux : biais algorithmiques, vie privée, emploi, souveraineté.
    """
    return paragraph * 50  # Assez long pour forcer le découpage


@pytest.fixture
def sample_summaries():
    return [
        "L'IA est un domaine informatique visant à reproduire l'intelligence humaine.",
        "Le machine learning permet aux machines d'apprendre sans programmation explicite.",
        "Les applications incluent la santé, l'automobile, la finance et le traitement du langage.",
    ]


# ─────────────────────────────────────────────
# TESTS — chunk_text.py
# ─────────────────────────────────────────────

class TestCountTokens:
    def test_count_tokens_basic(self, short_text):
        count = count_tokens(short_text)
        assert isinstance(count, int)
        assert count > 0

    def test_count_tokens_empty(self):
        assert count_tokens("") == 0

    def test_count_tokens_long_gt_short(self, short_text, medium_text):
        assert count_tokens(medium_text) > count_tokens(short_text)


class TestChunkText:
    def test_short_text_no_split(self, short_text):
        """Un texte court ne doit pas être découpé."""
        chunks = chunk_text(short_text, max_tokens=3000)
        assert len(chunks) == 1
        assert chunks[0] == short_text

    def test_long_text_splits(self, long_text):
        """Un texte long doit être découpé en plusieurs chunks."""
        chunks = chunk_text(long_text, max_tokens=500)
        assert len(chunks) > 1

    def test_chunk_size_respected(self, long_text):
        """Chaque chunk doit respecter la limite de tokens."""
        max_tokens = 500
        chunks = chunk_text(long_text, max_tokens=max_tokens)
        for chunk in chunks:
            assert count_tokens(chunk) <= max_tokens + 10  # +10 tolérance décodage

    def test_chunks_not_empty(self, long_text):
        """Aucun chunk ne doit être vide."""
        chunks = chunk_text(long_text, max_tokens=500)
        for chunk in chunks:
            assert chunk.strip() != ""

    def test_returns_list(self, short_text):
        result = chunk_text(short_text)
        assert isinstance(result, list)


class TestChunkTextByParagraphs:
    def test_preserves_paragraphs(self, medium_text):
        chunks = chunk_text_by_paragraphs(medium_text, max_tokens=300)
        assert len(chunks) >= 1

    def test_no_empty_chunks(self, medium_text):
        chunks = chunk_text_by_paragraphs(medium_text, max_tokens=300)
        for chunk in chunks:
            assert chunk.strip() != ""

    def test_single_chunk_if_small(self, short_text):
        chunks = chunk_text_by_paragraphs(short_text, max_tokens=3000)
        assert len(chunks) == 1


# ─────────────────────────────────────────────
# TESTS — summarize.py (nécessite API key)
# ─────────────────────────────────────────────

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY non définie — test API ignoré"
)
class TestSummarizeSingleChunk:
    def test_returns_string(self, short_text):
        result = summarize_single_chunk(short_text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_not_empty(self, medium_text):
        result = summarize_single_chunk(medium_text)
        assert result.strip() != ""

    def test_shorter_than_original(self, medium_text):
        result = summarize_single_chunk(medium_text)
        assert len(result) < len(medium_text)

    def test_with_doc_type(self, medium_text):
        result = summarize_single_chunk(medium_text, doc_type="article scientifique")
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY non définie — test API ignoré"
)
class TestSummarizeChunks:
    def test_returns_list(self, medium_text):
        chunks = chunk_text_by_paragraphs(medium_text)
        summaries = summarize_chunks(chunks, verbose=False)
        assert isinstance(summaries, list)

    def test_same_length_as_chunks(self, medium_text):
        chunks = chunk_text_by_paragraphs(medium_text)
        summaries = summarize_chunks(chunks, verbose=False)
        assert len(summaries) == len(chunks)

    def test_all_summaries_non_empty(self, medium_text):
        chunks = chunk_text_by_paragraphs(medium_text)
        summaries = summarize_chunks(chunks, verbose=False)
        for s in summaries:
            assert s.strip() != ""


# ─────────────────────────────────────────────
# TESTS — merge.py
# ─────────────────────────────────────────────

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY non définie — test API ignoré"
)
class TestMergeSummaries:
    def test_returns_string(self, sample_summaries):
        result = merge_summaries(sample_summaries, verbose=False)
        assert isinstance(result, str)

    def test_not_empty(self, sample_summaries):
        result = merge_summaries(sample_summaries, verbose=False)
        assert result.strip() != ""

    def test_single_summary_no_merge(self):
        single = ["Un seul résumé partiel."]
        result = merge_summaries(single, verbose=False)
        assert result == single[0]

    def test_empty_list_returns_empty(self):
        result = merge_summaries([], verbose=False)
        assert result == ""

    def test_output_formats(self, sample_summaries):
        for fmt in ["paragraphe", "bullet", "structuré"]:
            result = merge_summaries(sample_summaries, output_format=fmt, verbose=False)
            assert isinstance(result, str)
            assert len(result) > 0


# ─────────────────────────────────────────────
# TESTS — Pipeline complet
# ─────────────────────────────────────────────

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY non définie — test API ignoré"
)
class TestFullPipeline:
    def test_pipeline_returns_string(self, medium_text):
        result = run_full_pipeline(medium_text, verbose=False)
        assert isinstance(result, str)

    def test_pipeline_not_empty(self, medium_text):
        result = run_full_pipeline(medium_text, verbose=False)
        assert result.strip() != ""

    def test_pipeline_shorter_than_original(self, medium_text):
        result = run_full_pipeline(medium_text, verbose=False)
        assert len(result) < len(medium_text)

    def test_pipeline_with_instructions(self, medium_text):
        result = run_full_pipeline(
            medium_text,
            instructions="Résume en 3 points maximum.",
            verbose=False
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pipeline_long_document(self, long_text):
        """Test le pipeline sur un long document nécessitant du chunking."""
        result = run_full_pipeline(long_text, verbose=True)
        assert isinstance(result, str)
        assert len(result) > 0
        # Le résumé doit être significativement plus court
        assert len(result) < len(long_text) * 0.5


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])