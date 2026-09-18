import os
from datetime import date

import joblib
from fastapi import FastAPI
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


# Load trained ML model
model = joblib.load(
    r"C:\Users\arvind rawat\OneDrive\Desktop"
    r"\Shopkeeper-AI-An-Agentic-AI-Based-Daily-Business-Assistant"
    r"\ml\models\demand_forecast_model.joblib"
)


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
    1. Retrieve recent weekly sales history from MySQL.
    2. Append the target week.
    3. Apply the same feature engineering used during training.
    4. Predict demand using the trained ML model.
    """

    history_df = get_weekly_history_from_db(
        item_id,
        weeks_back=10
    )

    history_df = append_target_week(
        history_df,
        target_week,
        current_sell_price
    )

    features_df = engineer_features(history_df)

    X_new = features_df.iloc[[-1]][
        categorical_cols + numeric_cols
    ]

    predicted_demand = model.predict(X_new)[0]

    return max(0, predicted_demand)


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

    predicted_demand = predict_item_demand(
        req.item_id,
        req.target_week,
        req.current_sell_price
    )

    return {
        "item_id": req.item_id,
        "target_week": req.target_week,
        "predicted_demand": round(predicted_demand, 2)
    }


@app.post(
    "/reorder-recommendation",
    summary="Generate inventory reorder recommendation",
    description=(
        "Calculate the recommended order quantity using "
        "predicted demand, safety stock, and current inventory."
    )
)
def reorder_recommendation(request: ReorderRequest):

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

    return {
        "item_id": request.item_id,
        "target_week": request.target_week,
        "predicted_demand": round(predicted_demand, 2),
        "recommended_order": max(0, round(recommended_order))
    }
