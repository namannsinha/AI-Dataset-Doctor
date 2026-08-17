import os
import uuid
import math

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Query,
)

from app.tabular.services.profiler import (
    load_dataset,
    get_basic_profile,
)

from app.tabular.services.quality import (
    analyze_quality,
    calculate_health_score,
    get_health_score_breakdown,
)

from app.tabular.services.statistics import (
    calculate_statistics,
)

from app.tabular.services.outliers import (
    detect_outliers,
)

from app.tabular.services.recommendations import (
    generate_recommendations,
)

from app.tabular.services.clustering import (
    perform_clustering,
)

from app.tabular.services.correlation import (
    calculate_correlations,
)

from app.tabular.services.overview import (
    generate_overview,
)

from app.tabular.services.treatment import (
    treat_dataset,
)

from app.tabular.services.readiness import (
    calculate_ml_readiness,
)


router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


def make_json_safe(obj):

    if isinstance(obj, dict):

        return {
            key: make_json_safe(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):

        return [
            make_json_safe(value)
            for value in obj
        ]

    if isinstance(obj, float):

        if math.isnan(obj) or math.isinf(obj):
            return None

    return obj

@router.post("/analyze")
async def analyze_dataset(
    file: UploadFile = File(...),
):

    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    if file_extension not in [
        ".csv",
        ".xlsx",
        ".xls",
    ]:

        return {
            "error": (
                "Only CSV and Excel files "
                "are supported."
            )
        }

    file_id = str(uuid.uuid4())

    file_path = os.path.join(
        UPLOAD_DIR,
        file_id + file_extension,
    )

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    try:

        df = load_dataset(
            file_path
        )

        profile = get_basic_profile(
            df
        )

        quality = analyze_quality(
            df
        )

        statistics = calculate_statistics(
            df
        )

        outliers = detect_outliers(
            df
        )

        recommendations = (
            generate_recommendations(
                df,
                quality,
                outliers,
            )
        )

        health_score = (
            calculate_health_score(
                quality,
                outliers,
            )
        )

        health_breakdown = (
            get_health_score_breakdown(
                quality,
                outliers,
            )
        )

        result = {
            "dataset": profile,
            "quality": quality,
            "statistics": statistics,
            "outliers": outliers,
            "health_score": health_score,
            "health_breakdown": health_breakdown,
            "recommendations": recommendations,
        }

        return make_json_safe(
            result
        )

    except Exception as exc:

        return {
            "error": str(exc)
        }