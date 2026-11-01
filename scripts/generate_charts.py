import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set overall plot styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

def generate_benchmark_chart():
    df = pd.read_csv('extended_models_comparison.csv')
    df['Clean_Name'] = df['Model'].apply(lambda x: x.split('(')[1].replace(')', '') if '(' in x else x)
    
    # Sort by R2_Test descending
    df = df.sort_values('R2_Test', ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, facecolor='#ffffff')
    
    # Palette highlighting XGBoost and MLP
    highlight_color = '#0284c7'   # Sky/Blue
    second_color = '#38bdf8'      # Light Blue
    base_color = '#94a3b8'        # Muted Slate
    colors = [highlight_color if 'XGBoost' in name else second_color if 'MLP' in name or 'Gradient' in name else base_color for name in df['Clean_Name']]
    
    # Chart 1: R2 Score (Train vs Test)
    y_pos = np.arange(len(df))
    height = 0.38
    
    rects1 = ax1.barh(y_pos + height/2, df['R2_Train'], height, label='Train $R^2$', color='#38bdf8', alpha=0.85, edgecolor='none')
    rects2 = ax1.barh(y_pos - height/2, df['R2_Test'], height, label='Test $R^2$', color='#0369a1', alpha=0.95, edgecolor='none')
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df['Clean_Name'], fontsize=11, fontweight='500', color='#1e293b')
    ax1.set_xlabel('Coefficient of Determination ($R^2$ Score)', fontsize=11, fontweight='bold', color='#334155', labelpad=8)
    ax1.set_title('Model Generalization & Accuracy ($R^2$)', fontsize=13, fontweight='bold', color='#0f172a', pad=12)
    ax1.legend(frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0', loc='lower right')
    ax1.grid(axis='x', linestyle='--', alpha=0.5, color='#cbd5e1')
    ax1.set_xlim(0, 1.0)
    
    for r in rects2:
        w = r.get_width()
        ax1.text(w + 0.015, r.get_y() + r.get_height()/2, f'{w:.3f}', va='center', ha='left', fontsize=9.5, fontweight='bold', color='#0369a1')

    # Chart 2: Test RMSE and Test MAE Error (Lower is better)
    rects3 = ax2.barh(y_pos + height/2, df['RMSE_Test'], height, label='Test RMSE (mm)', color='#f43f5e', alpha=0.85, edgecolor='none')
    rects4 = ax2.barh(y_pos - height/2, df['MAE_Test'], height, label='Test MAE (mm)', color='#fb7185', alpha=0.95, edgecolor='none')
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([''] * len(df))
    ax2.set_xlabel('Error in mm/day (Lower is Better)', fontsize=11, fontweight='bold', color='#334155', labelpad=8)
    ax2.set_title('Test Error Metrics (RMSE vs MAE)', fontsize=13, fontweight='bold', color='#0f172a', pad=12)
    ax2.legend(frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0', loc='lower right')
    ax2.grid(axis='x', linestyle='--', alpha=0.5, color='#cbd5e1')
    ax2.set_xlim(0, 9.5)
    
    for r in rects3:
        w = r.get_width()
        ax2.text(w + 0.15, r.get_y() + r.get_height()/2, f'{w:.2f}', va='center', ha='left', fontsize=9.5, fontweight='bold', color='#e11d48')

    plt.suptitle('Rainfall Model Benchmark: 7 Machine Learning Algorithms Evaluated', fontsize=15, fontweight='bold', color='#0f172a', y=0.98)
    plt.tight_layout()
    plt.savefig('assets/model_benchmark_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved assets/model_benchmark_comparison.png")

def generate_feature_importance_chart():
    import pickle
    with open('final_model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    features = [
        ('GWETTOP', 'Topsoil Wetness Ratio (0-1)'),
        ('RH2M', 'Relative Humidity @ 2m (%)'),
        ('QV2M', 'Specific Humidity @ 2m (g/kg)'),
        ('T2M_MAX', 'Maximum Air Temperature (°C)'),
        ('T2M_MIN', 'Minimum Air Temperature (°C)'),
        ('ALLSKY_SFC_SW_DWN', 'Downwelling Solar Irradiance (W/m²)'),
        ('T2MDEW', 'Dew Point Temperature (°C)'),
        ('T2M', 'Average Temperature @ 2m (°C)'),
        ('WS2M', 'Wind Speed @ 2m (m/s)'),
        ('T2MWET', 'Wet Bulb Temperature (°C)'),
        ('ALLSKY_SFC_SW_DNI', 'Direct Normal Irradiance (W/m²)')
    ]
    
    # Feature names in the exact training order:
    cols = ['ALLSKY_SFC_SW_DWN', 'ALLSKY_SFC_SW_DNI', 'T2M', 'T2MDEW', 'T2MWET',
            'T2M_MAX', 'T2M_MIN', 'RH2M', 'QV2M', 'WS2M', 'GWETTOP']
            
    imp_dict = dict(zip(cols, model.feature_importances_))
    
    feature_data = []
    for code, desc in features:
        feature_data.append({
            'code': code,
            'label': f"{code}\n({desc})",
            'importance': imp_dict[code] * 100
        })
        
    f_df = pd.DataFrame(feature_data).sort_values('importance', ascending=True)
    
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300, facecolor='#ffffff')
    
    norm_colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(f_df)))
    bars = ax.barh(f_df['label'], f_df['importance'], color=norm_colors, height=0.65, edgecolor='none')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.grid(axis='x', linestyle='--', alpha=0.5, color='#cbd5e1')
    
    ax.set_title('PrecipiCast XGBoost Feature Importance Breakdown', fontsize=14, fontweight='bold', color='#0f172a', pad=16)
    ax.set_xlabel('Relative Importance Weight (%)', fontsize=11, fontweight='bold', color='#334155', labelpad=10)
    ax.set_xlim(0, 50)
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.6, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', ha='left', fontsize=10, fontweight='bold', color='#0369a1')
        
    plt.tight_layout()
    plt.savefig('assets/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved assets/feature_importance.png")

if __name__ == '__main__':
    generate_benchmark_chart()
    generate_feature_importance_chart()
