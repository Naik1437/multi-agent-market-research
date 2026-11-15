import json

import main


def test_benchmark_record_matches_generated_artifact_paths(tmp_path, monkeypatch):
    benchmark_file = tmp_path / "benchmarks.json"
    benchmark_file.write_text(json.dumps({"existing": "preserved"}), encoding="utf-8")
    monkeypatch.setattr(main, "BENCHMARK_FILE", benchmark_file)
    markdown_path, pdf_path = main.report_paths("Tech Sector Q3 Analysis")

    main.update_benchmarks(
        query="Tech Sector Q3 Analysis",
        status="SUCCESS",
        execution_time=12.5,
        report_path=markdown_path,
        pdf_path=pdf_path,
        report_generated=True,
        pdf_generated=True,
        run_id="test-run-id",
        started_at="2026-11-15T00:00:00+00:00"
    )

    result = json.loads(benchmark_file.read_text(encoding="utf-8"))
    execution = result["execution"]
    assert result["existing"] == "preserved"
    assert execution["query"] == "Tech Sector Q3 Analysis"
    assert execution["run_id"] == "test-run-id"
    assert execution["markdown_report"] == markdown_path.relative_to(main.BASE_DIR).as_posix()
    assert execution["pdf_report"] == pdf_path.relative_to(main.BASE_DIR).as_posix()
    assert execution["report_generated"] is True
    assert execution["pdf_generated"] is True
