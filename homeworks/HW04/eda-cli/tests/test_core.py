from __future__ import annotations

import pandas as pd
import pytest

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    assert not corr.empty
    assert "age" in corr.columns and "height" in corr.index

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2


def test_compute_quality_flags_new_heuristics():
    """
    Проверяет новые эвристики качества:
    - has_constant_columns
    - has_suspicious_id_duplicates (user_id не уникален)
    - has_high_cardinality_categoricals (колонка с долей уникальных > 0.9)
    """
    df = pd.DataFrame({
        "user_id": ["u1", "u2", "u3", "u2"],      # ← дубликат u2 → должен выполнять has_suspicious_id_duplicates
        "constant_col": [42, 42, 42, 42],          # ← все одинаковые → has_constant_columns = True
        "high_card_cat": ["a", "b", "c", "d"],     # ← 4 уникальных из 4 → доля 1.0 > 0.9 → high cardinality
        "normal_cat": ["X", "X", "Y", "Y"],        # ← нормальная категория
        "numeric": [1.0, 2.0, 3.0, 4.0],           # ← числовая, без пропусков
    })

    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)

    assert flags["has_constant_columns"] is True
    assert flags["has_suspicious_id_duplicates"] is True
    assert flags["has_high_cardinality_categoricals"] is True 

    user_id_summary = next(col for col in summary.columns if col.name == "user_id")
    assert user_id_summary.unique == 3
    assert user_id_summary.unique < summary.n_rows


def test_quality_score_penalized_by_issues():
    """
    Проверяет, что quality_score снижается при наличии проблем:
    - константная колонка
    - дубликаты user_id
    - колонка с высокой кардинальностью
    """
    df_good = pd.DataFrame({
        "user_id": ["u1", "u2", "u3", "u4"],
        "cat": ["A", "B", "A", "C"],
        "num": [1, 2, 3, 4],
    })
    summary_good = summarize_dataset(df_good)
    missing_df_good = missing_table(df_good)
    flags_good = compute_quality_flags(summary_good, missing_df_good)

    df_bad = pd.DataFrame({
        "user_id": ["u1", "u2", "u3", "u2"],
        "const": [99, 99, 99, 99],
        "high_card": ["x1", "x2", "x3", "x4"],
        "num": [1, 2, 3, 4],
    })
    summary_bad = summarize_dataset(df_bad)
    missing_df_bad = missing_table(df_bad)
    flags_bad = compute_quality_flags(summary_bad, missing_df_bad)



def test_has_constant_columns_without_user_id():
    df = pd.DataFrame({
        "A": [1, 1, 1],
        "B": [2, 3, 4],
        "C": ["x", "x", "x"],  
    })
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)

    assert flags["has_constant_columns"] is True
    assert flags.get("has_suspicious_id_duplicates", False) is False