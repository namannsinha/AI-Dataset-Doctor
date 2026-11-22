
import json
from pathlib import Path

from app.models import AnalysisResult


class ReportWriter:

    def write_json(
        self,
        results: list[AnalysisResult],
        output_path: str,
        summary: dict[str, int],
    ) -> None:

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = {
            "summary": summary,
            "analyzers": [
                result.model_dump(mode="json")
                for result in results
            ],
        }

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
            )
