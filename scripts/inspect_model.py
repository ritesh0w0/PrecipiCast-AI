import pickle
import xgboost as xgb

with open("final_model.pkl", "rb") as f:
    model = pickle.load(f)

print(type(model))
print(dir(model))

try:
    if hasattr(model, 'evals_result'):
        print("Evals Result:", model.evals_result())
    if hasattr(model, 'best_score'):
        print("Best Score:", model.best_score)
except Exception as e:
    print(e)
