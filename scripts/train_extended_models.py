import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 1. Load data & filter headers
header_idx = 0
csv_path = r"C:\Users\rites\Downloads\Bandar Seri Begawan.csv"

with open(csv_path, 'r') as file:
    for i, line in enumerate(file):
        if "-END HEADER-" in line:
            header_idx = i + 1
            break

df = pd.read_csv(csv_path, skiprows=header_idx)

# 2. Data Cleaning
rows_before = len(df)
df.replace([-999.0, -999], np.nan, inplace=True)
df.dropna(inplace=True)
df['DATE'] = pd.to_datetime(df['YEAR'] * 1000 + df['DOY'], format='%Y%j')

print(f"Data Cleaning: Rows Before: {rows_before} | Rows After: {len(df)}")

features_11 = [
    'ALLSKY_SFC_SW_DWN', 'ALLSKY_SFC_SW_DNI', 'T2M', 'T2MDEW', 'T2MWET',
    'T2M_MAX', 'T2M_MIN', 'RH2M', 'QV2M', 'WS2M', 'GWETTOP'
]

# 3. Data Splitting
df = df.sort_values('DATE')
df_train_test = df[df['YEAR'] <= 2020]
df_unseen = df[df['YEAR'] > 2020]

X_train_test = df_train_test[features_11]
y_train_test = df_train_test['PRECTOTCORR']

X_unseen = df_unseen[features_11]
y_unseen = df_unseen['PRECTOTCORR']

# Split the 1995-2020 block into 80% Train, 20% Evaluate
X_train, X_test, y_train, y_test = train_test_split(
    X_train_test, y_train_test, test_size=0.20, random_state=42
)

# 4. Standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_unseen_scaled = scaler.transform(X_unseen)

# 5. Evaluate helper
def evaluate_model(model, X, y_true):
    y_pred = np.maximum(0, model.predict(X))  # Rain cannot be negative
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    return r2, rmse, mae, mse

# 6. Train Models
models = {
    "Model 1 (Decision Tree)": DecisionTreeRegressor(max_depth=6, random_state=42),
    "Model 2 (Random Forest)": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    "Model 3 (XGBoost)": XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42, n_jobs=-1),
    "Model 4 (Linear Regression)": LinearRegression(),
    "Model 5 (Ridge Regression)": Ridge(alpha=1.0),
    "Model 6 (Gradient Boosting)": GradientBoostingRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42),
    "Model 7 (MLP Regressor)": MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
}

results = []
print("Training the 7 models...")
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train_scaled, y_train)
    r2_tr, rmse_tr, mae_tr, mse_tr = evaluate_model(model, X_train_scaled, y_train)
    r2_te, rmse_te, mae_te, mse_te = evaluate_model(model, X_test_scaled, y_test)
    
    results.append({
        "Model": name,
        "R2_Train": round(r2_tr, 3),
        "R2_Test": round(r2_te, 3),
        "RMSE_Train": round(rmse_tr, 3),
        "RMSE_Test": round(rmse_te, 3),
        "MAE_Train": round(mae_tr, 3),
        "MAE_Test": round(mae_te, 3),
        "MSE_Train": round(mse_tr, 3),
        "MSE_Test": round(mse_te, 3)
    })

# Convert to DataFrame
df_results = pd.DataFrame(results)
print("\n--- MODEL COMPARISON TABLE ---")
print(df_results.to_string(index=False))

# Export results to CSV for record
df_results.to_csv("extended_models_comparison.csv", index=False)
print("\nResults successfully saved to extended_models_comparison.csv!")
