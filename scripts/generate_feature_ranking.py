import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the style
if 'seaborn-v0_8-whitegrid' in plt.style.available:
    plt.style.use('seaborn-v0_8-whitegrid')
else:
    plt.style.use('default')
sns.set_theme(style="whitegrid")

# Features and scores
features = [
    "RH2M (Relative Humidity)",
    "GWETTOP (Surface Soil Wetness)",
    "T2MDEW (Dew Point Temp)",
    "QV2M (Specific Humidity)",
    "WS2M (Wind Speed)"
]
scores = [0.424, 0.413, 0.225, 0.223, 0.123]

# Create figure
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

# Generate a professional color gradient
colors = sns.color_palette("mako", n_colors=len(features))

# Draw the horizontal bar chart
bars = ax.barh(features[::-1], scores[::-1], color=colors[::-1], edgecolor='none', height=0.6)

# Customize grid and spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Add scores as labels next to the bars
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.008, 
        bar.get_y() + bar.get_height() / 2, 
        f'{width:.3f}', 
        va='center', 
        ha='left', 
        fontsize=11, 
        fontweight='bold', 
        color='#2c3e50'
    )

# Formatting
ax.set_title("Top 5 Meteorological Drivers of Daily Rainfall\n(Pearson Correlation Coefficients)", fontsize=14, fontweight='bold', pad=20, color='#2c3e50')
ax.set_xlabel("Pearson Correlation Coefficient (r)", fontsize=11, fontweight='bold', labelpad=10, color='#34495e')
ax.set_xlim(0, 0.5)

# Tight layout
plt.tight_layout()

# Save the plot
output_path = r"C:\Users\rites\Downloads\feature_ranking.png"
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print(f"Feature ranking chart successfully generated and saved to: {output_path}")
