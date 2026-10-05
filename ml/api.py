import json
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

app = FastAPI(
    title="Shopkeeper AI Demand Forecasting API",
    description=(
        "API for predicting product demand and generating "
        "inventory reorder recommendations for small retail stores."
    ),
    version="1.0.0"
)


# Load trained ML model relative to this file so it works from any CWD.
model = None
base_dir = Path(__file__).resolve().parent
default_model_path = base_dir / "models" / "demand_forecast_model.joblib"
model_path = Path(os.getenv("MODEL_PATH", str(default_model_path)))
try:
    model = joblib.load(model_path)
except Exception as exc:
    model = None
    load_err = exc

    def _model_load_error():
        raise RuntimeError(f"Failed to load model from {model_path}: {load_err}")

    _model_loader_error = _model_load_error


@app.get("/", summary="Service status")
def read_root():
    return {
        "message": "Shopkeeper AI Demand Forecast API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", summary="Health check")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None
    }


@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        write_api_log(
            "INFO",
            "ml_api",
            request.method,
            request.url.path,
            "request completed",
            status_code=response.status_code,
        )
        return response
    except Exception as exc:
        write_api_log(
            "ERROR",
            "ml_api",
            request.method,
            request.url.path,
            str(exc),
            exception_type=type(exc).__name__,
        )
        raise


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
API_LOG_DB = Path(__file__).resolve().with_name("api_logs.sqlite")


def init_api_log_db() -> None:
    conn = sqlite3.connect(API_LOG_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            source TEXT,
            method TEXT,
            path TEXT,
            message TEXT,
            meta TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def write_api_log(level: str, source: str, method: str, path: str, message: str, **meta) -> None:
    conn = sqlite3.connect(API_LOG_DB)
    conn.execute(
        "INSERT INTO api_logs (timestamp, level, source, method, path, message, meta) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            datetime.utcnow().isoformat(),
            level,
            source,
            method,
            path,
            message,
            json.dumps(meta or {}, default=str),
        ),
    )
    conn.commit()
    conn.close()


init_api_log_db()

categorical_cols = ["item_id"]
numeric_cols = [
    "lag_1", "lag_2", "lag_4", "lag_8",
    "rolling_mean_4", "rolling_std_4",
    "rolling_mean_8", "rolling_std_8",
    "month", "week_of_year", "year",
    "price_change", "price_lag_1", "sell_price"
]


def get_weekly_history_from_db(item_id: str, weeks_back: int = 10) -> pd.DataFrame:
    """Build the same weekly sales history used during model training."""
    item_id = str(item_id)
    sales_path = DATA_DIR / "sales_train_validation.csv"
    calendar_path = DATA_DIR / "calendar.csv"
    prices_path = DATA_DIR / "sell_prices.csv"

    if not sales_path.exists() or not calendar_path.exists() or not prices_path.exists():
        raise FileNotFoundError(
            "Forecasting data files not found under the project data directory. "
            "Expected calendar.csv, sales_train_validation.csv, and sell_prices.csv."
        )

    sales_df = pd.read_csv(sales_path)
    calendar = pd.read_csv(calendar_path)
    sell_prices = pd.read_csv(prices_path)

    item_rows = sales_df[sales_df["item_id"] == item_id].copy()
    if item_rows.empty:
        raise ValueError(f"No sales history found for item_id '{item_id}' in the training dataset.")

    id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    day_cols = [col for col in item_rows.columns if col.startswith("d_")]

    melted = item_rows.melt(
        id_vars=id_cols,
        value_vars=day_cols,
        var_name="d",
        value_name="sales"
    )
    melted = melted.merge(calendar[["d", "date", "wm_yr_wk"]], on="d", how="left")
    melted["date"] = pd.to_datetime(melted["date"])
    melted = melted.merge(sell_prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")
    melted = melted.dropna(subset=["sell_price"])
    melted = melted[melted["sell_price"] > 0].copy()
    melted["week"] = melted["date"].dt.to_period("W").apply(lambda r: r.start_time)

    weekly_df = (
        melted.groupby(["item_id", "week"], as_index=False)
        .agg(sales=("sales", "sum"), sell_price=("sell_price", "mean"))
        .sort_values("week")
        .reset_index(drop=True)
    )
    weekly_df["week"] = pd.to_datetime(weekly_df["week"])

    if weekly_df.empty:
        raise ValueError(f"No usable weekly history for item_id '{item_id}'.")

    return weekly_df.tail(max(1, int(weeks_back))).reset_index(drop=True)


def append_target_week(history_df: pd.DataFrame, target_week: date, current_sell_price: float) -> pd.DataFrame:
    """Append the future target week as a new row for prediction."""
    if history_df.empty:
        raise ValueError("Cannot append a target week to an empty history DataFrame.")

    item_id = str(history_df["item_id"].iloc[0])
    target_dt = pd.Timestamp(target_week)
    target_week_start = target_dt.to_period("W").start_time
    new_row = {
        "item_id": item_id,
        "week": pd.Timestamp(target_week_start),
        "sales": 0,
        "sell_price": float(current_sell_price),
    }
    out = pd.concat([history_df.copy(), pd.DataFrame([new_row])], ignore_index=True)
    return out.sort_values("week").reset_index(drop=True)


def engineer_features(history_df: pd.DataFrame) -> pd.DataFrame:
    """Apply the same lag and rolling features used during model training."""
    df = history_df.copy()

    for lag in [1, 2, 4, 8]:
        df[f"lag_{lag}"] = df.groupby("item_id")["sales"].transform(lambda s: s.shift(lag))

    for window in [4, 8]:
        df[f"rolling_mean_{window}"] = df.groupby("item_id")["sales"].transform(
            lambda s: s.shift(1).rolling(window).mean()
        )
        df[f"rolling_std_{window}"] = df.groupby("item_id")["sales"].transform(
            lambda s: s.shift(1).rolling(window).std()
        )

    df["month"] = df["week"].dt.month
    df["week_of_year"] = df["week"].dt.isocalendar().week.astype(int)
    df["year"] = df["week"].dt.year
    df["price_change"] = df.groupby("item_id")["sell_price"].transform(lambda s: s.diff())
    df["price_lag_1"] = df.groupby("item_id")["sell_price"].transform(lambda s: s.shift(1))

    df = df.dropna().reset_index(drop=True)
    return df


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class DemandPredictionRequest(BaseModel):
    """Request schema for product demand prediction."""

    item_id: str = Field(
        ...,
        description="Unique identifier of the product.",
        examples=["HOBBIES_1_001"]
    )

    target_week: date = Field(
        ...,
        description="Week for which demand should be predicted.",
        examples=["2026-09-21"]
    )

    current_sell_price: float = Field(
        ...,
        gt=0,
        description="Current selling price of the product.",
        examples=[99.50]
    )


class ReorderRequest(BaseModel):
    """Request schema for inventory reorder recommendations."""

    item_id: str = Field(
        ...,
        description="Unique identifier of the product.",
        examples=["HOBBIES_1_001"]
    )

    target_week: date = Field(
        ...,
        description="Target week for demand forecasting.",
        examples=["2026-09-21"]
    )

    current_sell_price: float = Field(
        ...,
        gt=0,
        description="Current selling price of the product.",
        examples=[99.50]
    )

    safe_stock: int = Field(
        default=10,
        ge=0,
        description="Minimum safety stock to maintain.",
        examples=[10]
    )

    current_stock: int = Field(
        ...,
        ge=0,
        description="Current available stock of the product.",
        examples=[15]
    )


# --------------------------------------------------
# Helper Function
# --------------------------------------------------

def predict_item_demand(
    item_id: str,
    target_week: date,
    current_sell_price: float
):
    """
    Generate demand prediction for a product.

    Steps:
    1. Retrieve recent weekly sales history from the local M5 training data.
    2. Append the target week.
    3. Apply the same feature engineering used during training.
    4. Predict demand using the trained ML model.
    """
    if model is None:
        raise RuntimeError(f"Prediction model could not be loaded from {model_path}")

    history_df = get_weekly_history_from_db(item_id, weeks_back=10)
    history_df = append_target_week(history_df, target_week, current_sell_price)
    features_df = engineer_features(history_df)

    X_new = features_df.iloc[[-1]][categorical_cols + numeric_cols]
    predicted_demand = model.predict(X_new)[0]

    return max(0, float(predicted_demand))


# --------------------------------------------------
# API Endpoints
# --------------------------------------------------

@app.post(
    "/predict-demand",
    summary="Predict product demand",
    description=(
        "Predict the expected demand for a product during "
        "the selected target week using historical sales data "
        "and the trained ML model."
    )
)
def predict_demand(req: DemandPredictionRequest):

    write_api_log(
        "INFO",
        "ml_api",
        "POST",
        "/predict-demand",
        "prediction request received",
        item_id=req.item_id,
        target_week=req.target_week.isoformat(),
        current_sell_price=req.current_sell_price,
    )

    predicted_demand = predict_item_demand(
        req.item_id,
        req.target_week,
        req.current_sell_price
    )

    result = {
        "item_id": req.item_id,
        "target_week": req.target_week,
        "predicted_demand": round(predicted_demand, 2)
    }
    write_api_log(
        "INFO",
        "ml_api",
        "POST",
        "/predict-demand",
        "prediction completed",
        item_id=req.item_id,
        target_week=req.target_week.isoformat(),
        predicted_demand=result["predicted_demand"],
    )
    return result


@app.post(
    "/reorder-recommendation",
    summary="Generate inventory reorder recommendation",
    description=(
        "Calculate the recommended order quantity using "
        "predicted demand, safety stock, and current inventory."
    )
)
def reorder_recommendation(request: ReorderRequest):

    write_api_log(
        "INFO",
        "ml_api",
        "POST",
        "/reorder-recommendation",
        "reorder request received",
        item_id=request.item_id,
        target_week=request.target_week.isoformat(),
        current_sell_price=request.current_sell_price,
        safe_stock=request.safe_stock,
        current_stock=request.current_stock,
    )

    predicted_demand = predict_item_demand(
        request.item_id,
        request.target_week,
        request.current_sell_price
    )

    recommended_order = (
        predicted_demand
        + request.safe_stock
        - request.current_stock
    )

    result = {
        "item_id": request.item_id,
        "target_week": request.target_week,
        "predicted_demand": round(predicted_demand, 2),
        "recommended_order": max(0, round(recommended_order))
    }
    write_api_log(
        "INFO",
        "ml_api",
        "POST",
        "/reorder-recommendation",
        "reorder recommendation completed",
        item_id=request.item_id,
        target_week=request.target_week.isoformat(),
        predicted_demand=result["predicted_demand"],
        recommended_order=result["recommended_order"],
    )
    return result
