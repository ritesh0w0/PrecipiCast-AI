import docx
import shutil
import os

doc_path = r"C:\Users\rites\Downloads\RWH CCA.docx"
output_path = r"C:\Users\rites\Downloads\RWH CCA_Updated.docx"

doc = docx.Document(doc_path)

print("--- Modifying Paragraphs ---")
# 1. Update Splitting of Data Section
splitting_found = False
for idx, p in enumerate(doc.paragraphs):
    if "Splitting of data: YEAR WISE" in p.text:
        print(f"Found splitting section at paragraph {idx}")
        splitting_found = True
        # Let's insert the content in the next empty paragraph
        next_p = doc.paragraphs[idx + 1]
        next_p.text = (
            "To ensure a robust and realistic validation of our machine learning models, "
            "the dataset was strictly split chronologically by year:\n"
            "• Training & Validation Block (1995-2020): This historical 26-year subset was sliced "
            "sequentially for model development. A random 80/20 train/test split was applied within "
            "this block (X_train/X_test) to evaluate generalizability and prevent overfitting.\n"
            "• Unseen Testing Validation Block (2021-2025): This 5-year block was completely "
            "hidden from all model training and scaling procedures. It serves as an isolated test set "
            "to evaluate real-world forecasting utility on future anomalies."
        )
        print("Updated Year-Wise Splitting text successfully!")
        break

if not splitting_found:
    print("Warning: Could not find 'Splitting of data: YEAR WISE' paragraph.")

print("\n--- Modifying Tables ---")
# 2. Find and update Table 3 (Model comparison table)
table3_found = False
for i, table in enumerate(doc.tables):
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    if "Model" in headers and any("R²" in h or "R2" in h for h in headers):
        print(f"Found Model Comparison Table at Table index {i}")
        table3_found = True
        
        # Extended model results
        results = [
            ["Decision Tree", "0.559", "0.373", "6.276", "7.789", "4.331", "4.943", "39.391", "60.673"],
            ["Random Forest", "0.778", "0.475", "4.448", "7.124", "3.180", "4.496", "19.781", "50.751"],
            ["XGBoost", "0.838", "0.467", "3.803", "7.181", "2.658", "4.478", "14.461", "51.570"],
            ["Linear Regression", "0.377", "0.384", "7.460", "7.717", "4.829", "4.940", "55.650", "59.552"],
            ["Ridge Regression", "0.376", "0.382", "7.466", "7.730", "4.830", "4.945", "55.739", "59.747"],
            ["Gradient Boosting", "0.621", "0.481", "5.815", "7.081", "3.962", "4.480", "33.817", "50.136"],
            ["MLP Regressor", "0.572", "0.498", "6.181", "6.970", "4.001", "4.329", "38.204", "48.576"]
        ]
        
        # Remove original data rows (excluding header)
        num_rows = len(table.rows)
        print(f"Original table rows: {num_rows}")
        for _ in range(num_rows - 1):
            table._tbl.remove(table.rows[1]._tr)
            
        # Now append all 7 rows
        for row_data in results:
            new_row = table.add_row()
            for col_idx, text in enumerate(row_data):
                new_row.cells[col_idx].text = text
                
        print("Updated Table 3 with all 7 models successfully!")
        break

if not table3_found:
    print("Warning: Could not find Model Comparison Table.")

# 3. Find and update Table 4 (Best ML Model table)
table4_found = False
for i, table in enumerate(doc.tables):
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    if "Best ML Model" in headers or "Training Set" in headers:
        print(f"Found Best Model Table at Table index {i}")
        table4_found = True
        
        metrics = {
            1: ("0.838", "0.467"), # R2
            2: ("3.803", "7.181"), # RMSE
            3: ("2.658", "4.478"), # MAE
            4: ("14.461", "51.570") # MSE
        }
        
        for row_idx, (train_val, test_val) in metrics.items():
            table.rows[row_idx].cells[2].text = train_val
            table.rows[row_idx].cells[3].text = test_val
            
        print("Updated Table 4 with XGBoost metrics successfully!")
        break

if not table4_found:
    print("Warning: Could not find Best ML Model Table.")

# Save document to the new output path
doc.save(output_path)
print(f"Report document successfully updated and saved to copy: {output_path}")

# Also try to overwrite the original path (if Microsoft Word has been closed)
try:
    shutil.copy(output_path, doc_path)
    print(f"Also successfully synchronized back to original report file: {doc_path}")
except PermissionError:
    print(f"Note: Original file '{doc_path}' is currently locked. Saved the updated report as a copy at '{output_path}'. Please save/close Word and replace it.")
