from pathlib import Path

import pytest
import yaml

from app.evals.runners.run_dataset import run_dataset


@pytest.mark.asyncio
async def test_run_dataset_returns_case_results(tmp_path: Path):
    dataset = tmp_path / "dataset.yaml"
    dataset.write_text(
        yaml.safe_dump(
            {
                "cases": [
                    {
                        "name": "case",
                        "input": "hello",
                        "checks": [{"type": "contains", "value": "Template"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    results = await run_dataset(dataset)

    assert results[0].name == "case"
