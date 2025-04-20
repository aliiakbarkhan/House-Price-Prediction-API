from fastapi import FastAPI
import joblib
from pydantic import BaseModel
import numpy as np
import pandas as pd

from custom_transformers import CombinedAttributesAdder  # needed for loading

class CombinedAttributesAdder:
    def __init__(self, add_bedrooms_per_room=True):
        self.add_bedrooms_per_room = add_bedrooms_per_room

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        rooms_per_household = X[:, 3] / X[:, 5]
        population_per_household = X[:, 4] / X[:, 5]
        if self.add_bedrooms_per_room:
            bedrooms_per_room = X[:, 2] / X[:, 3]
            return np.c_[X, rooms_per_household, population_per_household, bedrooms_per_room]
        else:
            return np.c_[X, rooms_per_household, population_per_household]



app = FastAPI()

# Load model
pipeline = joblib.load("pipeline.pkl")

class HouseFeatures(BaseModel):
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str

@app.post("/predict")
def predict(features: HouseFeatures):
    input_dict = features.dict()
    input_df = pd.DataFrame([input_dict])  # wrap input in a DataFrame

    prediction = pipeline.predict(input_df)
    return {"prediction": prediction[0]}
