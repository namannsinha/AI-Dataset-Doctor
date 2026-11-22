import json
from pathlib import Path

import pandas as pd
import streamlit as st

from run_dataset_doctor import main

st.markdown(
    """
    <style>
    :root {
        --app-bg: #11100f;
        --panel-bg: #191715;
        --panel-raised: #201d1a;
        --card-bg: #211e1b;
        --border: #39332d;
        --border-soft: #2b2723;
        --accent: #c47a52;
        --accent-hover: #d28b62;
        --accent-soft: rgba(196, 122, 82, 0.13);
        --text: #eee9e2;
        --muted: #a69b90;
        --subtle: #766d64;
    }

    * { box-sizing: border-box; }
    .stApp, [data-testid="stMain"] {
        background: var(--app-bg);
        color: var(--text);
    }
    [data-testid="stHeader"] {
        background: rgba(17, 16, 15, 0.94);
        border-bottom: 1px solid rgba(255,255,255,0.035);
    }
    [data-testid="stSidebar"] { display: none; }
    .block-container, [data-testid="stMainBlockContainer"] {
        max-width: 1320px;
        width: 100%;
        margin: 0 auto;
        padding: 3rem 2.5rem 5rem;
        box-sizing: border-box;
    }
    h1, h2, h3, h4 {
        color: var(--text) !important;
        letter-spacing: -0.035em;
    }
    h1 { font-weight: 760 !important; letter-spacing: -0.055em; }
    h2 { font-weight: 700 !important; }
    h3 { font-weight: 650 !important; }
    p { color: var(--muted); line-height: 1.65; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }

    /* Gentle page entrance; restrained motion rather than flashy effects. */
    [data-testid="stMainBlockContainer"] > div {
        animation: pageReveal 520ms ease both;
    }
    @keyframes pageReveal {
        from { opacity: 0; transform: translateY(9px); }
        to { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        width: 100%;
        background: linear-gradient(145deg, #1d1a17, #181614);
        border: 1px solid var(--border-soft) !important;
        border-radius: 13px !important;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.16);
        transition: border-color 220ms ease, transform 220ms ease, box-shadow 220ms ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #665044 !important;
        transform: translateY(-2px);
        box-shadow: 0 14px 34px rgba(0,0,0,0.22);
    }
    hr { border-color: var(--border-soft); }

    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stCheckbox"] label {
        color: #d0c7bd;
        font-size: 0.88rem;
        font-weight: 580;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background: #12110f;
        color: var(--text);
        border: 1px solid #403931;
        border-radius: 8px;
        transition: border-color 180ms ease, box-shadow 180ms ease;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 2px var(--accent-soft);
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] { min-width: 0; border-radius: 8px; }
    [data-baseweb="select"] > div {
        background: #211e1b;
        border-color: #403931;
        color: var(--text);
    }
    [data-testid="stCheckbox"] svg { color: var(--accent); }

    .stButton > button, .stDownloadButton > button {
        min-height: 44px;
        border-radius: 8px;
        font-weight: 650;
        transition: background 180ms ease, border-color 180ms ease,
                    color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
    }
    .stButton > button[kind="primary"] {
        min-height: 54px;
        width: 100%;
        background: var(--accent);
        border: 1px solid var(--accent);
        border-radius: 9px;
        color: #17110d;
        font-size: 0.98rem;
        font-weight: 750;
        letter-spacing: 0.01em;
        box-shadow: 0 7px 20px rgba(196,122,82,0.14);
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover);
        border-color: var(--accent-hover);
        color: #17110d;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(196,122,82,0.2);
    }
    .stButton > button:active, .stDownloadButton > button:active { transform: translateY(0); }
    .stDownloadButton > button {
        background: var(--panel-raised);
        border: 1px solid var(--border);
        color: var(--text);
    }
    .stDownloadButton > button:hover {
        border-color: var(--accent);
        color: var(--accent-hover);
        transform: translateY(-1px);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #24201c, #1b1916);
        border: 1px solid var(--border-soft);
        border-radius: 12px;
        padding: 19px 20px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.13);
        transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
        animation: metricReveal 450ms ease both;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: #665044;
        box-shadow: 0 12px 26px rgba(0,0,0,0.2);
    }
    @keyframes metricReveal {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: 0.88rem; }
    [data-testid="stMetricValue"] { color: #e0a17c; font-weight: 760; letter-spacing: -0.035em; }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }
    [data-testid="stAlert"] {
        border-radius: 9px;
        border: 1px solid var(--border);
        background: #211e1a;
        color: var(--text);
    }
    [data-testid="stAlert"] p { color: var(--text); }
    [data-testid="stExpander"] {
        background: var(--panel-bg);
        border: 1px solid var(--border);
        border-radius: 9px;
    }
    [data-testid="stProgressBar"] > div > div { background: var(--accent); }
    ::selection { background: rgba(196,122,82,0.3); color: #fff; }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
    @media (max-width: 768px) {
        .block-container, [data-testid="stMainBlockContainer"] {
            padding: 1.4rem 1rem 2.5rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] { padding: 15px; }
        h1 { font-size: 2rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        """
        <div style="padding-bottom: 18px;">
            <div style="
                color: #c47a52;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-bottom: 10px;
            ">
                DATA QUALITY WORKSPACE
            </div>
            <h1 style="
                margin: 0;
                font-size: 2.5rem;
                color: #eee9e2;
            ">
                AI Dataset Doctor
            </h1>
            <p style="
                color: #a69b90;
                font-size: 1rem;
                margin-top: 10px;
            ">
                Find dataset issues. Improve data quality.
                Build more reliable ML models.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        """
        <div style="
            margin-top: 26px;
            padding: 10px 12px;
            border: 1px solid #39332d;
            border-radius: 10px;
            text-align: center;
            background: #211e1b;
            color: #d0c7bd;
            font-size: 12px;
            font-weight: 600;
        ">
            VERSION 1.0
        </div>
        """,
        unsafe_allow_html=True,
    )



st.markdown(
    """
    <div style="
        display:flex;
        align-items:center;
        gap:10px;
        flex-wrap:wrap;
        margin:8px 0 30px;
        padding:13px 16px;
        background:linear-gradient(100deg,#211e1b,#191715);
        border:1px solid #39332d;
        border-radius:12px;
    ">
        <span style="
            display:inline-block;
            width:9px;
            height:9px;
            flex-shrink:0;
            border-radius:50%;
            background:#c47a52;
            box-shadow:0 0 12px rgba(196,122,82,.45);
        "></span>
        <span style="color:#eee9e2;font-weight:650;">
            Dataset Quality Workspace
        </span>
        <span style="color:#766d64;">·</span>
        <span style="color:#a69b90;font-size:13px;">
            Image integrity · Resolution · Blur · Duplicates · Visual analysis
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------
# Configuration workspace
# -------------------------

st.markdown(
    """
    <div style="margin: 10px 0 18px;">
        <div style="color:#c47a52;font-size:12px;
                    font-weight:700;letter-spacing:1.8px;">
            WORKSPACE CONFIGURATION
        </div>
        <h2 style="margin:6px 0;color:#eee9e2;">
            Configure your analysis
        </h2>
        <p style="margin:0;color:#a69b90;">
            Select your dataset, set quality thresholds, and choose
            how each analyzer should handle detected issues.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dataset paths
with st.container(border=True):
    st.markdown("### 01 · Dataset")

    dataset_col, output_col = st.columns(2)

    with dataset_col:
        dataset_path = st.text_input(
            "Input dataset folder",
            value="data/input/practice_dataset",
            help="Path to the folder containing your images.",
        )

    with output_col:
        output_path = st.text_input(
            "Output folder",
            value="data/output/frontend_run",
            help="Analysis reports and generated files will be saved here.",
        )

# Analysis settings
with st.container(border=True):
    st.markdown("### 02 · Quality thresholds")

    width_col, height_col, blur_col = st.columns(3)

    with width_col:
        min_width = st.number_input(
            "Minimum image width (px)",
            min_value=1,
            value=224,
            step=16,
        )

    with height_col:
        min_height = st.number_input(
            "Minimum image height (px)",
            min_value=1,
            value=224,
            step=16,
        )

    with blur_col:
        blur_threshold = st.number_input(
            "Blur threshold",
            min_value=0.0,
            value=60.0,
            step=5.0,
            help="Images below the configured sharpness threshold may be flagged.",
        )

    st.divider()

    clustering_col, clusters_col, validation_col = st.columns(3)

    with clustering_col:
        enable_clustering = st.checkbox(
            "Enable clustering",
            value=True,
        )

    with clusters_col:
        num_clusters = st.number_input(
            "Number of clusters",
            min_value=1,
            value=2,
            step=1,
            disabled=not enable_clustering,
        )

    with validation_col:
        enable_label_validation = st.checkbox(
            "Enable label validation",
            value=True,
        )

# Analyzer actions
with st.container(border=True):
    st.markdown("### 03 · Analyzer actions")
    st.caption(
        "Choose whether each analyzer should flag findings "
        "or quarantine affected images."
    )

    action_options = ["Flag", "Quarantine"]

    action_defaults = {
        "corruption": "Quarantine",
        "resolution": "Flag",
        "blur": "Quarantine",
        "duplicate": "Quarantine",
        "label_validation": "Flag",
    }

    action_columns = st.columns(2)
    analyzer_actions = {}

    for index, (name, default) in enumerate(action_defaults.items()):
        with action_columns[index % 2]:
            selected = st.selectbox(
                name.replace("_", " ").title(),
                options=action_options,
                index=action_options.index(default),
                key=f"action_{name}",
            )

        analyzer_actions[name] = {
            "Flag": "flag",
            "Quarantine": "quarantine",
        }[selected]

# Run button at the bottom of all settings
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

run_analysis = st.button(
    "Run dataset analysis  →",
    type="primary",
    use_container_width=True,
)


if run_analysis:
    input_dir = Path(dataset_path).expanduser()
    output_dir = Path(output_path).expanduser()

    if not input_dir.is_dir():
        st.error("Input folder does not exist. Check the path.")
    elif input_dir.resolve() == output_dir.resolve():
        st.error("Input and output folders must be different.")
    elif input_dir.resolve() in output_dir.resolve().parents:
        st.error(
            "Choose an output folder outside the input dataset."
        )
    else:
        try:
            with st.spinner(
                "Analyzing your dataset. This may take a while..."
            ):
                main(
                    input_dir,
                    output_dir,
                    blur_threshold=float(blur_threshold),
                    min_width=int(min_width),
                    min_height=int(min_height),
                    batch_size=5,
                    enable_clustering=enable_clustering,
                    num_clusters=int(num_clusters),
                    enable_label_validation=enable_label_validation,
                    analyzer_actions=analyzer_actions,
                )

            st.session_state["report_path"] = str(
                output_dir / "report.json"
            )
            st.session_state["dataset_root"] = str(
                input_dir.resolve()
            )
            st.success("Analysis completed successfully.")

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

report_path_value = st.session_state.get("report_path")

if report_path_value:
    report_path = Path(report_path_value)

    if report_path.is_file():
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)

        
        analyzers = report.get("analyzers", [])
        run_summary = report.get("summary", {})

        # Use the run-level summary from the backend.
        total_images = run_summary.get("total_images", 0)
        active_images = run_summary.get("active_images", 0)
        quarantined_images = run_summary.get("quarantined_images", 0)
        total_findings = run_summary.get("total_findings", 0)
        unique_affected = run_summary.get("unique_affected_images", 0)

        st.subheader("Analysis overview")

        # First row: dataset status
        col1, col2, col3 = st.columns(3)

        col1.metric("Total images", f"{total_images:,}")
        col2.metric("Active images", f"{active_images:,}")
        col3.metric("Quarantined images", f"{quarantined_images:,}")

        # Second row: findings
        col1, col2, col3 = st.columns(3)

        col1.metric("Total findings", f"{total_findings:,}")
        col2.metric("Unique affected images", f"{unique_affected:,}")
        col3.metric("Analyzers completed", len(analyzers))

        st.subheader("Finding severity")

        summary_rows = []
        finding_rows = []

        for item in analyzers:
            analyzer_name = item.get("analyzer", "unknown")
            findings = item.get("findings", [])

            summary_rows.append({
                "Analyzer": analyzer_name.replace("_", " ").title(),
                "Images Checked": item.get("images_checked", 0),
                "Findings": len(findings),
            })

            for finding in findings:
                finding_rows.append({
                    "Analyzer": analyzer_name.replace("_", " ").title(),
                    "Image": finding.get("image_id", ""),
                    "Issue": finding.get("issue_type", ""),
                    "Severity": finding.get("severity", "unknown").title(),
                    "Reason": finding.get("reason", ""),
                })

        severity_counts = {}

        for finding in finding_rows:
            severity = finding["Severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        severity_df = pd.DataFrame(
            [
                {"Severity": severity, "Findings": count}
                for severity, count in severity_counts.items()
            ]
        )

        if not severity_df.empty:
            st.dataframe(
                severity_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("No findings to classify by severity.")

        # ---------------------------------------------------------
        # Class distribution and label imbalance
        # ---------------------------------------------------------
        st.subheader("Class Distribution & Label Imbalance")

        class_result = next(
            (
                item for item in analyzers
                if item.get("analyzer") == "class_distribution"
            ),
            None,
        )

        if class_result is None:
            st.warning(
                "Class distribution results were not found in this report. "
                "Run the analysis again with the latest backend."
            )
        else:
            class_stats = class_result.get("statistics") or {}
            class_status = str(class_stats.get("status", "")).lower()

            if class_status in {"not_applicable", "not applicable", "skipped"}:
                st.info(
                    "Label imbalance analysis is not applicable because "
                    "the dataset does not contain usable class labels."
                )
            else:
                # Some reports store counts directly; others group them by split.
                split_stats = class_stats.get("splits")
                if not isinstance(split_stats, dict) or not split_stats:
                    split_stats = {
                        "Dataset": class_stats,
                    }

                rendered_distribution = False

                for split_name, split_data in split_stats.items():
                    if not isinstance(split_data, dict):
                        continue

                    # Accept the analyzer's class-count mapping. The aliases
                    # make the dashboard tolerant of small report schema changes.
                    counts = (
                        split_data.get("class_counts")
                        or split_data.get("class_distribution")
                        or split_data.get("classes")
                    )

                    if not isinstance(counts, dict) or not counts:
                        continue

                    numeric_counts = {}
                    for label, count in counts.items():
                        try:
                            numeric_counts[str(label)] = int(count)
                        except (TypeError, ValueError):
                            continue

                    if not numeric_counts:
                        continue

                    rendered_distribution = True
                    total_labeled = sum(numeric_counts.values())
                    percentages = split_data.get("class_percentages", {})

                    st.markdown(f"#### {str(split_name).replace('_', ' ').title()}")

                    metric_cols = st.columns(3)
                    metric_cols[0].metric("Labeled images", f"{total_labeled:,}")
                    metric_cols[1].metric("Classes", f"{len(numeric_counts):,}")

                    imbalance_ratio = split_data.get("imbalance_ratio")
                    if imbalance_ratio is not None:
                        metric_cols[2].metric(
                            "Imbalance ratio",
                            f"{imbalance_ratio}:1" if isinstance(imbalance_ratio, (int, float)) else str(imbalance_ratio),
                        )
                    else:
                        metric_cols[2].metric("Imbalance ratio", "Not provided")

                    rows = []
                    for label, count in sorted(
                        numeric_counts.items(),
                        key=lambda pair: pair[1],
                        reverse=True,
                    ):
                        percentage = percentages.get(label) if isinstance(percentages, dict) else None
                        if percentage is None:
                            percentage = (count / total_labeled * 100) if total_labeled else 0
                        rows.append({
                            "Class": label,
                            "Images": count,
                            "Percentage": f"{float(percentage):.2f}%",
                        })

                    distribution_df = pd.DataFrame(rows)
                    st.dataframe(
                        distribution_df,
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.bar_chart(
                        pd.DataFrame(
                            {"Images": numeric_counts}
                        ).sort_values("Images", ascending=False)
                    )

                    underrepresented = split_data.get("underrepresented_classes", [])
                    if underrepresented:
                        st.warning(
                            "Underrepresented classes: "
                            + ", ".join(str(label) for label in underrepresented)
                        )
                    else:
                        st.caption(
                            "No underrepresented classes were reported "
                            "for this split, or the analyzer did not provide that field."
                        )

                if not rendered_distribution:
                    labeled_images = class_stats.get("labeled_images")
                    unlabeled_images = class_stats.get("unlabeled_images")

                    if labeled_images is not None or unlabeled_images is not None:
                        metric_cols = st.columns(2)
                        metric_cols[0].metric(
                            "Labeled images",
                            f"{int(labeled_images or 0):,}",
                        )
                        metric_cols[1].metric(
                            "Unlabeled images",
                            f"{int(unlabeled_images or 0):,}",
                        )

                    st.info(
                        "The report contains class-distribution statistics, "
                        "but no recognized per-class count mapping was found. "
                        "The raw statistics are available below for inspection."
                    )
                    with st.expander("View raw class distribution statistics"):
                        st.json(class_stats)

        st.subheader("Results by analyzer")
        st.dataframe(
            pd.DataFrame(summary_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Detailed findings")

        if finding_rows:
            findings_df = pd.DataFrame(finding_rows)

            selected_analyzer = st.selectbox(
                "Filter by analyzer",
                ["All"] + sorted(findings_df["Analyzer"].unique()),
            )

            if selected_analyzer != "All":
                findings_df = findings_df[
                    findings_df["Analyzer"] == selected_analyzer
                ]

            st.dataframe(
                findings_df,
                use_container_width=True,
                hide_index=True,
            )

            # Inspect one finding at a time to avoid loading
            # hundreds of image previews simultaneously.
            st.subheader("Finding inspection")

            inspection_index = st.selectbox(
                "Select a finding to inspect",
                options=range(len(findings_df)),
                format_func=lambda index: (
                    f"{findings_df.iloc[index]['Analyzer']} | "
                    f"{findings_df.iloc[index]['Image']} | "
                    f"{findings_df.iloc[index]['Issue']}"
                ),
                key="finding_inspection",
            )

            selected_finding = findings_df.iloc[inspection_index]

            detail_col, preview_col = st.columns([1, 1])

            with detail_col:
                st.markdown("**Finding details**")
                st.write("Image:", selected_finding["Image"])
                st.write("Analyzer:", selected_finding["Analyzer"])
                st.write("Issue:", selected_finding["Issue"])
                st.write("Severity:", selected_finding["Severity"])
                st.write("Reason:", selected_finding["Reason"])

            with preview_col:
                st.markdown("**Original image preview**")

                dataset_root_value = st.session_state.get("dataset_root")

                if not dataset_root_value:
                    st.warning(
                        "Dataset location is unavailable. "
                        "Run the analysis again to enable image previews."
                    )
                else:
                    dataset_root = Path(dataset_root_value).resolve()
                    relative_path = Path(str(selected_finding["Image"]))

                    if (
                        relative_path.is_absolute()
                        or ".." in relative_path.parts
                    ):
                        st.error("Invalid image path in the report.")
                    else:
                        image_path = (
                            dataset_root / relative_path
                        ).resolve()

                        if not image_path.is_relative_to(dataset_root):
                            st.error(
                                "The image path points outside the dataset."
                            )
                        elif not image_path.is_file():
                            st.warning(
                                "The original image could not be found."
                            )
                        else:
                            try:
                                st.image(
                                    str(image_path),
                                    use_container_width=True,
                                )
                            except Exception:
                                st.error(
                                    "This image cannot be displayed. "
                                    "It may be corrupted or unreadable."
                                )

        else:
            st.success("No findings were reported.")

        with report_path.open("rb") as file:
            st.download_button(
                "Download JSON report",
                data=file.read(),
                file_name="report.json",
                mime="application/json",
            )

        st.caption(f"Report location: {report_path}")
    else:
        st.warning(
            "The report file was not found. Run the analysis again."
        )
