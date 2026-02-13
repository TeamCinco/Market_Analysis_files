"""Excel output - clean and simple"""
import pandas as pd
from pathlib import Path

def write_results_to_excel(results, output_path):
    """
    Write screening results to Excel
    Columns optimized for finding selling opportunities
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(results)
    
    # Sort by drop_from_high_pct (most dropped first)
    df = df.sort_values('drop_from_high_pct')
    
    # Reorder columns for easy scanning
    column_order = [
        'ticker',
        'current_price', 
        'recent_high',
        'drop_from_high_pct',
        'p10',
        'volatility',
        'p5',
        'p50',
        'success'
    ]
    
    df = df[column_order]
    
    # Write to Excel
    df.to_excel(output_path, index=False, sheet_name='Screening Results')
    
    print(f"\nResults saved to: {output_path}")
    print(f"Sorted by drop_from_high_pct (biggest drops first)")