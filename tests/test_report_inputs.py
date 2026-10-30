"""The report parameter table must match the actual canonical case."""

from src.config import load_config
from tools.export_report_inputs import TABLE_PATH, render_parameters


def test_report_table_matches_canonical_baseline():
    assert TABLE_PATH.read_text(encoding="utf8") == render_parameters(load_config())
