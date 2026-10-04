import pandas as pd


# ============================================================
# Configuration
# ============================================================

INPUT_PATH = (
    "data/clean/ml_dataset.csv"
)

TRAIN_PATH = (
    "data/clean/train.csv"
)

VALIDATION_PATH = (
    "data/clean/validation.csv"
)

TEST_PATH = (
    "data/clean/test.csv"
)


TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


# ============================================================
# Load dataset
# ============================================================

def load_dataset() -> pd.DataFrame:
    """
    Đọc ML dataset từ CSV.
    """

    df = pd.read_csv(
        INPUT_PATH
    )

    if df.empty:
        raise ValueError(
            "ML dataset không có dữ liệu."
        )

    # Đảm bảo date là datetime
    df["date"] = pd.to_datetime(
        df["date"]
    )

    # Sắp xếp theo symbol và date
    df = (
        df
        .sort_values(
            ["symbol", "date"]
        )
        .reset_index(drop=True)
    )

    return df


# ============================================================
# Split dataset
# ============================================================

def split_dataset(
    df: pd.DataFrame
):
    """
    Chia dataset theo thứ tự thời gian.

    Train      = 70%
    Validation = 15%
    Test       = 15%

    Không random dữ liệu.
    """

    if (
        TRAIN_RATIO
        + VALIDATION_RATIO
        + TEST_RATIO
        != 1.0
    ):
        raise ValueError(
            "Tổng tỷ lệ Train/Validation/Test "
            "phải bằng 1."
        )

    train_parts = []
    validation_parts = []
    test_parts = []

    # --------------------------------------------------------
    # Chia riêng từng symbol
    # --------------------------------------------------------

    for symbol, symbol_df in df.groupby(
        "symbol"
    ):

        symbol_df = (
            symbol_df
            .sort_values("date")
            .reset_index(drop=True)
        )

        n = len(symbol_df)

        train_end = int(
            n * TRAIN_RATIO
        )

        validation_end = int(
            n * (
                TRAIN_RATIO
                + VALIDATION_RATIO
            )
        )

        train = symbol_df[
            :train_end
        ]

        validation = symbol_df[
            train_end:validation_end
        ]

        test = symbol_df[
            validation_end:
        ]

        train_parts.append(train)
        validation_parts.append(validation)
        test_parts.append(test)

    # --------------------------------------------------------
    # Ghép lại
    # --------------------------------------------------------

    train_df = pd.concat(
        train_parts,
        ignore_index=True
    )

    validation_df = pd.concat(
        validation_parts,
        ignore_index=True
    )

    test_df = pd.concat(
        test_parts,
        ignore_index=True
    )

    return (
        train_df,
        validation_df,
        test_df
    )


# ============================================================
# Validate split
# ============================================================

def validate_split(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> None:
    """
    Kiểm tra kết quả chia dataset.
    """

    print(
        "\n===== KIỂM TRA DATASET SPLIT ====="
    )

    # --------------------------------------------------------
    # Tổng số dòng
    # --------------------------------------------------------

    total = (
        len(train_df)
        + len(validation_df)
        + len(test_df)
    )

    print(
        f"Train:      {len(train_df):,} dòng"
    )

    print(
        f"Validation: {len(validation_df):,} dòng"
    )

    print(
        f"Test:       {len(test_df):,} dòng"
    )

    print(
        f"Tổng:       {total:,} dòng"
    )

    # --------------------------------------------------------
    # Thời gian
    # --------------------------------------------------------

    print("\nKhoảng thời gian:")

    print(
        f"Train:"
        f" {train_df['date'].min().date()}"
        f" → "
        f"{train_df['date'].max().date()}"
    )

    print(
        f"Validation:"
        f" {validation_df['date'].min().date()}"
        f" → "
        f"{validation_df['date'].max().date()}"
    )

    print(
        f"Test:"
        f" {test_df['date'].min().date()}"
        f" → "
        f"{test_df['date'].max().date()}"
    )

    # --------------------------------------------------------
    # Kiểm tra thứ tự thời gian
    # --------------------------------------------------------

    if (
        train_df["date"].max()
        >= validation_df["date"].min()
    ):
        raise ValueError(
            "Train và Validation bị chồng lấn thời gian."
        )

    if (
        validation_df["date"].max()
        >= test_df["date"].min()
    ):
        raise ValueError(
            "Validation và Test bị chồng lấn thời gian."
        )

    # --------------------------------------------------------
    # Target distribution
    # --------------------------------------------------------

    print("\nTarget distribution:")

    print("\nTrain:")
    print(
        train_df["target"]
        .value_counts(
            normalize=True
        )
        .sort_index()
        .mul(100)
        .round(2)
    )

    print("\nValidation:")
    print(
        validation_df["target"]
        .value_counts(
            normalize=True
        )
        .sort_index()
        .mul(100)
        .round(2)
    )

    print("\nTest:")
    print(
        test_df["target"]
        .value_counts(
            normalize=True
        )
        .sort_index()
        .mul(100)
        .round(2)
    )

    print(
        "\nKiểm tra split hoàn tất."
    )


# ============================================================
# Save datasets
# ============================================================

def save_datasets(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> None:
    """
    Lưu Train / Validation / Test.
    """

    train_df.to_csv(
        TRAIN_PATH,
        index=False
    )

    validation_df.to_csv(
        VALIDATION_PATH,
        index=False
    )

    test_df.to_csv(
        TEST_PATH,
        index=False
    )

    print(
        f"\nĐã lưu:"
    )

    print(
        f"- {TRAIN_PATH}"
    )

    print(
        f"- {VALIDATION_PATH}"
    )

    print(
        f"- {TEST_PATH}"
    )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        "          SPLIT ML DATASET"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    print(
        "\n[1/4] Đọc ML dataset..."
    )

    df = load_dataset()

    print(
        f"Đã đọc {len(df):,} dòng."
    )

    # --------------------------------------------------------
    # 2. Split
    # --------------------------------------------------------

    print(
        "\n[2/4] Chia Train / Validation / Test..."
    )

    (
        train_df,
        validation_df,
        test_df
    ) = split_dataset(df)

    # --------------------------------------------------------
    # 3. Validate
    # --------------------------------------------------------

    print(
        "\n[3/4] Kiểm tra..."
    )

    validate_split(
        train_df,
        validation_df,
        test_df
    )

    # --------------------------------------------------------
    # 4. Save
    # --------------------------------------------------------

    print(
        "\n[4/4] Lưu dataset..."
    )

    save_datasets(
        train_df,
        validation_df,
        test_df
    )

    print(
        "\n========================================"
    )

    print(
        "              HOÀN TẤT"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()