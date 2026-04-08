from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

from ..config import PROCESSED_DIR, ARTIFACTS_DIR

DATA_PATH = PROCESSED_DIR / "company_monthly_emissions.csv"
COMPANIES_PATH = PROCESSED_DIR / "company_profiles.csv"
MODEL_PATH = ARTIFACTS_DIR / "forecast_model.joblib"

FEATURE_COLUMNS = [
    "month_num",
    "employees",
    "revenue_musd",
    "energy_consumption_mwh",
    "renewable_share_pct",
    "environmental_score",
    "social_score",
    "governance_score",
    "controversies_count",
    "lag_1",
    "lag_3_mean",
]


def load_data():
    emissions = pd.read_csv(DATA_PATH, parse_dates=["date"])
    companies = pd.read_csv(COMPANIES_PATH)
    return emissions, companies


def build_training_frame():
    emissions, companies = load_data()
    df = emissions.merge(companies, on="company_id", how="left").sort_values(["company_id", "date"]).copy()
    df["month_num"] = df["date"].dt.month
    df["lag_1"] = df.groupby("company_id")["emissions_tco2e"].shift(1)
    rolling = df.groupby("company_id")["emissions_tco2e"].rolling(3).mean().reset_index(level=0, drop=True)
    df["lag_3_mean"] = rolling.shift(1)
    df["target"] = df.groupby("company_id")["emissions_tco2e"].shift(-1)
    return df.dropna(subset=["lag_1", "lag_3_mean", "target"]).reset_index(drop=True)


def _fit_model(X: np.ndarray, y: np.ndarray) -> dict:
    xb = np.column_stack([np.ones(len(X)), X])
    coeffs, *_ = np.linalg.lstsq(xb, y, rcond=None)
    return {"intercept": coeffs[0], "weights": coeffs[1:]}


def _predict(model: dict, X: np.ndarray) -> np.ndarray:
    return model["intercept"] + X @ model["weights"]


def train_model():
    df = build_training_frame()
    X = df[FEATURE_COLUMNS].astype(float).to_numpy()
    y = df["target"].astype(float).to_numpy()
    model = _fit_model(X, y)
    preds = _predict(model, X)
    mape = (np.abs((y - preds) / np.clip(y, 1e-6, None))).mean() * 100
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "mape_proxy_pct": round(float(mape), 2)}, MODEL_PATH)
    return {"train_rows": int(len(df)), "mape_proxy_pct": round(float(mape), 2)}


def ensure_model():
    if not MODEL_PATH.exists():
        train_model()


def forecast_company(company_id: str, months: int = 12):
    ensure_model()
    payload = joblib.load(MODEL_PATH)
    model = payload["model"]
    mape = payload["mape_proxy_pct"]

    emissions, companies = load_data()
    hist = emissions.loc[emissions["company_id"] == company_id].sort_values("date").copy()
    if hist.empty:
        raise ValueError(f"Unknown company_id: {company_id}")

    meta = companies.loc[companies["company_id"] == company_id].iloc[0].to_dict()
    history = hist.tail(12).copy()
    last_values = hist["emissions_tco2e"].tolist()
    current_date = hist["date"].max()
    forecast = []

    for _ in range(months):
        next_date = current_date + pd.offsets.MonthBegin(1)
        row = {
            "month_num": float(next_date.month),
            "employees": float(meta["employees"]),
            "revenue_musd": float(meta["revenue_musd"]),
            "energy_consumption_mwh": float(meta["energy_consumption_mwh"]),
            "renewable_share_pct": float(meta["renewable_share_pct"]),
            "environmental_score": float(meta["environmental_score"]),
            "social_score": float(meta["social_score"]),
            "governance_score": float(meta["governance_score"]),
            "controversies_count": float(meta["controversies_count"]),
            "lag_1": float(last_values[-1]),
            "lag_3_mean": float(np.mean(last_values[-3:])),
        }
        x = np.array([[row[c] for c in FEATURE_COLUMNS]], dtype=float)
        pred = max(float(_predict(model, x)[0]), 0.0)
        forecast.append({"period": next_date.strftime("%Y-%m"), "value": round(pred, 2), "kind": "forecast"})
        last_values.append(pred)
        current_date = next_date

    hist_rows = [{"period": d.strftime("%Y-%m"), "value": round(float(v), 2), "kind": "history"} for d, v in zip(history["date"], history["emissions_tco2e"])]
    last_12_avg = float(history["emissions_tco2e"].mean())
    next_12_avg = float(np.mean([x["value"] for x in forecast]))
    reduction_potential = max(0.0, min(40.0, (meta["renewable_share_pct"] / 100) * 22 + meta["environmental_score"] * 0.14))
    delta = (next_12_avg - last_12_avg) / max(last_12_avg, 1e-6)

    if delta > 0.08 or meta["controversies_count"] >= 3:
        risk = "high"
    elif delta > 0.01:
        risk = "medium"
    else:
        risk = "low"

    commentary = (
        f"{meta['company_name']} shows a projected average of {next_12_avg:.1f} tCO2e/month "
        f"over the next {months} months. Risk is {risk.upper()} based on trajectory, renewable share, and controversy count."
    )

    return {
        "company_id": company_id,
        "company_name": meta["company_name"],
        "months": months,
        "history": hist_rows,
        "forecast": forecast,
        "mape_proxy_pct": float(round(mape, 2)),
        "reduction_potential_pct": round(reduction_potential, 1),
        "risk_level": risk,
        "commentary": commentary,
    }
