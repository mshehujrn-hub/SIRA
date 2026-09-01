from src.data_loader import DataLoader
from src.eda import DataExplorer
from src.preprocessing import IncidentDataCleaner
from src.services import PredictionService
from src.utils import print_header


def main():
    # ---------------------------------------------------------
    # Stage 1: Data Loading & Preprocessing Pipeline
    # ---------------------------------------------------------
    print_header("1. DATA LOADING & PREPROCESSING")
    loader = DataLoader()
    explorer = DataExplorer()

    df_raw = loader.load_data()

    print("[INFO] Raw Dataset Summary:")
    explorer.show_shape(df_raw)
    explorer.show_missing_values(df_raw)

    print("\n[INFO] Executing Incident Data Cleaner Pipeline...")
    categorical_cols = [
        "location",
        "reported_by",
        "department",
        "severity",
        "incident_type",
        "shift",
        "status",
    ]

    cleaner = IncidentDataCleaner(df_raw)
    df_clean = (
        cleaner.clean_text_sentinels()
        .remove_duplicates()
        .clean_free_text(text_cols=["report_text"])
        .standardize_text_fields(categorical_cols=categorical_cols)
        .fix_date_formats(date_columns=["report_date"])
        .handle_missing_values(
            categorical_cols=categorical_cols, numeric_cols=[]
        )
        .get_cleaned_data()
    )

    print(f"Data shape after cleaning: {df_clean.shape}\n")

    # ---------------------------------------------------------
    # Stage 2: Real-Time Model Inference Pipeline
    # ---------------------------------------------------------
    print_header("2. SIRA REAL-TIME INFERENCE SERVICE")

    try:
        service = PredictionService()

        sample_reports = [
            "Gas leak detected near pressure control valve in Block B manifold.",
            "High temperature alarm triggered on crude oil pump bearing.",
            "Minor oil spill noticed during pipe flange maintenance at storage tank 4.",
            "Operator slipped on wet metal stairs while ascending to platform level 2.",
        ]

        print("[INFO] Evaluating sample incident logs:\n")
        for report in sample_reports:
            predicted_type = service.predict_single(report)
            print(f'Report: "{report}"')
            print(f"  └─> Predicted Category: [{predicted_type}]\n")

    except FileNotFoundError:
        print(
            "[ERROR] Model artifacts missing. Run 'uv run --active python train_and_save.py' first!"
        )


if __name__ == "__main__":
    main()