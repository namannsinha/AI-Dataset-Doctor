import json
from pathlib import Path

import pandas as pd
import streamlit as st

from run_dataset_doctor import main

st.markdown(
    """
    <style>
    :root {
        --app-bg: #0b0d0f;
        --panel-bg: #131714;
        --card-bg: #151a17;
        --border: #29352d;
        --accent: #42d392;
        --accent-hover: #2bb87c;
        --accent-soft: rgba(66, 211, 146, 0.12);
        --amber: #f2b866;
        --text: #f1f5f2;
        --muted: #9ba89f;
    }

    .stApp, [data-testid="stMain"] {
        background: var(--app-bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(11, 13, 15, 0.92);
    }

    /* Keep the workspace centered; controls are in the main page. */
    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 1240px;
        width: 100%;
        margin-left: auto;
        margin-right: auto;
        padding: 2.5rem 2rem 4rem;
        box-sizing: border-box;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        letter-spacing: -0.45px;
    }

    h1 {
        font-weight: 800 !important;
        letter-spacing: -1.4px;
    }

    h2 { font-weight: 750 !important; }
    h3 { font-weight: 650 !important; }

    p { color: var(--muted); }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    /* Configuration and results panels */
    [data-testid="stVerticalBlockBorderWrapper"] {
        width: 100%;
        box-sizing: border-box;
        background: var(--panel-bg);
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #3b5745 !important;
    }

    hr { border-color: var(--border); }

    /* Form controls */
    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label {
        color: #c6d0c9;
        font-size: 0.9rem;
        font-weight: 600;
        white-space: normal;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background: #0f1310;
        color: var(--text);
        border: 1px solid #303a32;
        border-radius: 10px;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] {
        min-width: 0;
        border-radius: 10px;
    }

    [data-testid="stCheckbox"] label {
        color: var(--text);
    }

    /* Primary and secondary actions */
    .stButton > button,
    .stDownloadButton > button {
        min-height: 44px;
        border-radius: 10px;
        font-weight: 650;
        transition: all 0.18s ease;
    }

    .stButton > button[kind="primary"] {
        min-height: 56px;
        width: 100%;
        background: var(--accent);
        border: 1px solid var(--accent);
        border-radius: 12px;
        color: #07130c;
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 0.15px;
        box-shadow: 0 6px 22px rgba(66, 211, 146, 0.12);
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover);
        border-color: var(--accent-hover);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(66, 211, 146, 0.2);
    }

    .stDownloadButton > button {
        background: var(--card-bg);
        border: 1px solid var(--border);
        color: var(--text);
    }

    .stDownloadButton > button:hover {
        border-color: var(--accent);
        color: var(--accent);
    }

    /* Result metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #171e19, #111512);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        color: var(--accent);
        font-weight: 800;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stProgressBar"] > div > div {
        background: var(--accent);
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    [data-testid="stExpander"] {
        background: var(--panel-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    ::selection {
        background: rgba(66, 211, 146, 0.3);
        color: #ffffff;
    }

    @media (max-width: 768px) {
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding: 1.25rem 1rem 2.5rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 14px;
        }

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
                color: #42d392;
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
                color: #f1f5f2;
            ">
                AI Dataset Doctor
            </h1>
            <p style="
                color: #9ba89f;
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
            border: 1px solid #29352d;
            border-radius: 10px;
            text-align: center;
            background: #151a17;
            color: #c6d0c9;
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
        background:linear-gradient(100deg,#121914,#101310);
        border:1px solid #29352d;
        border-radius:12px;
    ">
        <span style="
            display:inline-block;
            width:9px;
            height:9px;
            flex-shrink:0;
            border-radius:50%;
            background:#42d392;
            box-shadow:0 0 12px rgba(66,211,146,.45);
        "></span>
        <span style="color:#dce8df;font-weight:650;">
            Dataset Quality Workspace
        </span>
        <span style="color:#738078;">·</span>
        <span style="color:#9ba89f;font-size:13px;">
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
        <div style="color:#42d392;font-size:12px;
                    font-weight:700;letter-spacing:1.8px;">
            WORKSPACE CONFIGURATION
        </div>
        <h2 style="margin:6px 0;color:#f1f5f2;">
            Configure your analysis
        </h2>
        <p style="margin:0;color:#9ba89f;">
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
        "Choose whether each analyzer should flag findings, "
        "quarantine affected images, or be skipped."
    )

    action_options = ["Flag", "Quarantine", "Skip"]

    action_defaults = {
        "corruption": "Quarantine",
        "resolution": "Flag",
        "blur": "Quarantine",
        "duplicate": "Quarantine",
        "clustering": "Flag",
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
            "Skip": "ignore",
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
        total_checked = max(
            (item.get("images_checked", 0) for item in analyzers),
            default=0,
        )
        total_findings = sum(
            len(item.get("findings", []))
            for item in analyzers
        )

        st.subheader("Analysis overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("Images analyzed", total_checked)
        col2.metric("Total findings", total_findings)
        col3.metric("Analyzers completed", len(analyzers))

        st.subheader("Results by analyzer")

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
                    "Severity": finding.get("severity", ""),
                    "Reason": finding.get("reason", ""),
                })

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
