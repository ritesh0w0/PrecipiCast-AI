import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_architecture():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300, facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    
    # Hide axes
    ax.axis('off')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    
    # Title
    ax.text(7, 8.0, "PrecipiCast AI & RWH Engine Architecture", fontsize=18, fontweight='bold', 
            ha='center', va='center', color='#f8fafc', fontfamily='sans-serif')
    ax.text(7, 7.6, "End-to-End Pipeline: NASA POWER Meteorological Data -> XGBoost Regressor -> RWH Estimation Engine", 
            fontsize=10.5, ha='center', va='center', color='#94a3b8', fontfamily='sans-serif')

    boxes = [
        {
            "title": "1. Data Acquisition & Ingestion",
            "subtitle": "NASA POWER Satellite & Agroclimatology",
            "items": [
                "• 11 Daily Meteorological Features",
                "• Solar Irradiance (SW_DWN, SW_DNI)",
                "• Multi-Level Temp (Avg, Max, Min, Wet)",
                "• Atmospheric Moisture (RH2M, QV2M, Dew)",
                "• Wind Speed & Soil Wetness (GWETTOP)"
            ],
            "x": 0.6, "y": 2.2, "w": 2.8, "h": 4.8,
            "color": "#1e293b", "border": "#38bdf8", "header_bg": "#0369a1"
        },
        {
            "title": "2. Preprocessing & Validation",
            "subtitle": "Temporal Split & Scaling Pipeline",
            "items": [
                "• Missing Value Sentinel (-999) Filter",
                "• Chronological Block Splitting:",
                "  - Train/Val Block: 1995-2020 (80/20)",
                "  - Isolated Test Block: 2021-2025",
                "• Robust Z-Score Standardization",
                "• Feature Persistence (final_scaler.pkl)"
            ],
            "x": 3.9, "y": 2.2, "w": 2.9, "h": 4.8,
            "color": "#1e293b", "border": "#818cf8", "header_bg": "#4338ca"
        },
        {
            "title": "3. Machine Learning Core",
            "subtitle": "Optimized XGBoost Regressor",
            "items": [
                "• Benchmark vs 6 Alternative Models",
                "  (RandomForest, GradientBoost, MLP...)",
                "• 300 Gradient-Boosted Trees",
                "• Non-Negative Rectification: max(0, y)",
                "• Test R²: 0.467 | Train R²: 0.838",
                "• Serialized Artifact (final_model.pkl)"
            ],
            "x": 7.3, "y": 2.2, "w": 2.9, "h": 4.8,
            "color": "#1e293b", "border": "#34d399", "header_bg": "#059669"
        },
        {
            "title": "4. Serving & Harvesting Engine",
            "subtitle": "Flask API & RWH Hydrology Engine",
            "items": [
                "• REST Endpoints: /predict, /health",
                "• Real-Time Inference Latency < 15ms",
                "• RWH Hydrological Sizing Formula:",
                "  V = P × A × C × η",
                "• Runoff Coefficient & Filter Efficacy",
                "• Household Water Offset Estimation"
            ],
            "x": 10.7, "y": 2.2, "w": 2.8, "h": 4.8,
            "color": "#1e293b", "border": "#f59e0b", "header_bg": "#d97706"
        }
    ]

    for b in boxes:
        # Draw main card
        rect = patches.FancyBboxPatch((b['x'], b['y']), b['w'], b['h'],
                                      boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=b['color'], edgecolor=b['border'],
                                      linewidth=1.8, alpha=0.95)
        ax.add_patch(rect)
        
        # Header banner
        header_rect = patches.FancyBboxPatch((b['x'], b['y'] + b['h'] - 1.1), b['w'], 1.1,
                                            boxstyle="round,pad=0.08,rounding_size=0.15",
                                            facecolor=b['header_bg'], edgecolor='none', alpha=0.9)
        ax.add_patch(header_rect)
        
        # Title text
        ax.text(b['x'] + b['w']/2, b['y'] + b['h'] - 0.4, b['title'],
                fontsize=10.5, fontweight='bold', ha='center', va='center', color='#ffffff', fontfamily='sans-serif')
        ax.text(b['x'] + b['w']/2, b['y'] + b['h'] - 0.8, b['subtitle'],
                fontsize=8.5, ha='center', va='center', color='#e2e8f0', fontfamily='sans-serif')
        
        # Items list
        curr_y = b['y'] + b['h'] - 1.45
        for item in b['items']:
            ax.text(b['x'] + 0.15, curr_y, item, fontsize=8.5, va='top', ha='left',
                    color='#cbd5e1', fontfamily='sans-serif', linespacing=1.3)
            curr_y -= 0.52

    # Draw connection arrows between the 4 stages
    arrow_props = dict(facecolor='#38bdf8', edgecolor='none', width=2.5, headwidth=8, headlength=7)
    ax.annotate('', xy=(3.85, 4.6), xytext=(3.45, 4.6), arrowprops=arrow_props)
    ax.annotate('', xy=(7.25, 4.6), xytext=(6.85, 4.6), arrowprops=arrow_props)
    ax.annotate('', xy=(10.65, 4.6), xytext=(10.25, 4.6), arrowprops=arrow_props)

    # Bottom Client Interface Bar
    client_rect = patches.FancyBboxPatch((0.6, 0.4), 12.9, 1.3,
                                         boxstyle="round,pad=0.08,rounding_size=0.15",
                                         facecolor='#1e293b', edgecolor='#38bdf8',
                                         linewidth=1.5, alpha=0.95)
    ax.add_patch(client_rect)
    ax.text(7, 1.25, "5. Modern Responsive Web Interface & Client Dashboards",
            fontsize=11.5, fontweight='bold', ha='center', va='center', color='#38bdf8', fontfamily='sans-serif')
    ax.text(7, 0.78, "Interactive Glassmorphism UI  •  Preset Weather Scenarios  •  Dynamic RWH Storage Estimator  •  Live Intensity Visualizer",
            fontsize=9.5, ha='center', va='center', color='#94a3b8', fontfamily='sans-serif')
            
    # Connector from serving to client
    arrow_down = dict(facecolor='#f59e0b', edgecolor='none', width=2.5, headwidth=8, headlength=7)
    ax.annotate('', xy=(12.1, 1.75), xytext=(12.1, 2.15), arrowprops=arrow_down)

    plt.tight_layout()
    plt.savefig('assets/architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved assets/architecture_diagram.png")

if __name__ == '__main__':
    generate_architecture()
