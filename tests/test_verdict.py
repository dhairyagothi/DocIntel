from reasoning.verdict_engine import create_verdict


def test_verdict_includes_human_readable_finding():
    verdict = create_verdict(4, [], failures_count=1, evidence_coverage=1.0)

    assert len(verdict.detailed_finding) == 3
    assert "4 evidence-grounded facts" in verdict.detailed_finding[0]
    assert "100%" in verdict.detailed_finding[0]