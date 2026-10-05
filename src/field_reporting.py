import pandas as pd
from datetime import datetime

print("==============================================")
print("PathSetu - Field / Community Reporting")
print("==============================================")

# ==================================================
# 1. SAMPLE FIELD REPORTS
# ==================================================
#
# These are DEMONSTRATION reports only.
# They are not real-time observations.
#
# Later, the Streamlit dashboard can replace
# these sample records with user-submitted reports.

reports = [

    {
        "report_id": "R001",
        "reporter_type": "Community",
        "location": "Samdong",
        "latitude": 27.3910,
        "longitude": 88.6670,
        "incident_type": "Road Blockage",
        "severity": "HIGH",
        "description":
            "Road reported as partially blocked.",
        "reported_at": "2025-12-31 09:30:00"
    },

    {
        "report_id": "R002",
        "reporter_type": "Field Team",
        "location": "Dikchu",
        "latitude": 27.4060,
        "longitude": 88.6070,
        "incident_type": "Landslide",
        "severity": "VERY HIGH",
        "description":
            "Possible landslide affecting road accessibility.",
        "reported_at": "2025-12-31 10:15:00"
    },

    {
        "report_id": "R003",
        "reporter_type": "Community",
        "location": "Raley",
        "latitude": 27.3600,
        "longitude": 88.6900,
        "incident_type": "Road Damage",
        "severity": "MODERATE",
        "description":
            "Road surface reported damaged.",
        "reported_at": "2025-12-31 11:00:00"
    },

    {
        "report_id": "R004",
        "reporter_type": "Community",
        "location": "Makha",
        "latitude": 27.3100,
        "longitude": 88.6200,
        "incident_type": "Waterlogging",
        "severity": "MODERATE",
        "description":
            "Water accumulation reported on road.",
        "reported_at": "2025-12-31 11:45:00"
    },

    {
        "report_id": "R005",
        "reporter_type": "Field Team",
        "location": "Rumtek",
        "latitude": 27.2850,
        "longitude": 88.5500,
        "incident_type": "Road Blockage",
        "severity": "HIGH",
        "description":
            "Temporary road obstruction reported.",
        "reported_at": "2025-12-31 12:20:00"
    }
]

# ==================================================
# 2. CREATE DATAFRAME
# ==================================================

reports_df = pd.DataFrame(
    reports
)

print()
print(
    f"Reports received: "
    f"{len(reports_df)}"
)

# ==================================================
# 3. VALIDATE REQUIRED COLUMNS
# ==================================================

required_columns = [
    "report_id",
    "reporter_type",
    "location",
    "latitude",
    "longitude",
    "incident_type",
    "severity",
    "description",
    "reported_at"
]

missing_columns = [
    column
    for column in required_columns
    if column not in reports_df.columns
]

if missing_columns:

    print()
    print("ERROR: Missing columns:")
    print(missing_columns)

    raise ValueError(
        "Required columns are missing."
    )

print("Required columns verified.")

# ==================================================
# 4. CONVERT DATA TYPES
# ==================================================

reports_df["latitude"] = pd.to_numeric(
    reports_df["latitude"],
    errors="coerce"
)

reports_df["longitude"] = pd.to_numeric(
    reports_df["longitude"],
    errors="coerce"
)

reports_df["reported_at"] = pd.to_datetime(
    reports_df["reported_at"],
    errors="coerce"
)

# ==================================================
# 5. VALIDATE COORDINATES
# ==================================================

valid_coordinates = (
    reports_df["latitude"].between(
        -90,
        90
    )
    &
    reports_df["longitude"].between(
        -180,
        180
    )
)

reports_df["coordinate_valid"] = (
    valid_coordinates
)

# ==================================================
# 6. SEVERITY SCORE
# ==================================================

severity_scores = {
    "LOW": 25,
    "MODERATE": 50,
    "HIGH": 75,
    "VERY HIGH": 100
}

reports_df["severity_score"] = (
    reports_df["severity"]
    .map(severity_scores)
)

# ==================================================
# 7. REPORTER TRUST SCORE
# ==================================================
#
# Field teams receive a higher initial trust score.
# Community reports receive a lower score because
# they may require verification.
#
# This is a prototype rule, not a validated
# real-world trust model.

trust_scores = {
    "Community": 70,
    "Field Team": 90
}

reports_df["reporter_trust_score"] = (
    reports_df["reporter_type"]
    .map(trust_scores)
    .fillna(50)
)

# ==================================================
# 8. REPORT CONFIDENCE
# ==================================================

reports_df["report_confidence"] = (
    0.60
    * reports_df["reporter_trust_score"]
    +
    0.40
    * reports_df["severity_score"]
)

reports_df["report_confidence"] = (
    reports_df["report_confidence"]
    .clip(0, 100)
)

# ==================================================
# 9. VALID / INVALID REPORT
# ==================================================

reports_df["report_valid"] = (
    reports_df["coordinate_valid"]
    &
    reports_df["reported_at"].notna()
    &
    reports_df["severity_score"].notna()
)

# ==================================================
# 10. REPORT STATUS
# ==================================================

def get_status(row):

    if not row["report_valid"]:

        return "INVALID"

    if row["report_confidence"] >= 80:

        return "HIGH CONFIDENCE"

    elif row["report_confidence"] >= 60:

        return "MEDIUM CONFIDENCE"

    else:

        return "LOW CONFIDENCE"


reports_df["report_status"] = (
    reports_df.apply(
        get_status,
        axis=1
    )
)

# ==================================================
# 11. SORT BY CONFIDENCE
# ==================================================

reports_df = reports_df.sort_values(
    by="report_confidence",
    ascending=False
)

# ==================================================
# 12. SELECT OUTPUT COLUMNS
# ==================================================

output = reports_df[
    [
        "report_id",
        "reporter_type",
        "location",
        "latitude",
        "longitude",
        "incident_type",
        "severity",
        "severity_score",
        "reporter_trust_score",
        "report_confidence",
        "report_status",
        "description",
        "reported_at",
        "report_valid"
    ]
].copy()

# ==================================================
# 13. SAVE
# ==================================================

output_file = (
    "data/field_reports.csv"
)

output.to_csv(
    output_file,
    index=False
)

# ==================================================
# 14. DISPLAY RESULTS
# ==================================================

print()
print("==============================================")
print("FIELD REPORT RESULTS")
print("==============================================")

print()

print(
    output[
        [
            "report_id",
            "location",
            "incident_type",
            "severity",
            "report_confidence",
            "report_status"
        ]
    ].to_string(index=False)
)

# ==================================================
# 15. SUMMARY
# ==================================================

print()
print("==============================================")
print("REPORT SUMMARY")
print("==============================================")

print(
    f"Total reports: "
    f"{len(output)}"
)

print(
    f"Valid reports: "
    f"{output['report_valid'].sum()}"
)

print(
    f"Invalid reports: "
    f"{(~output['report_valid']).sum()}"
)

print()
print("Report status:")

print(
    output[
        "report_status"
    ].value_counts().to_string()
)

print()
print("Incident types:")

print(
    output[
        "incident_type"
    ].value_counts().to_string()
)

print()
print(
    f"Output saved to: "
    f"{output_file}"
)

print()
print("==============================================")
print("FIELD REPORTING MODULE COMPLETE")
print("==============================================")