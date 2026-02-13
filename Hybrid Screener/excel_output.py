"""
Excel Output Writer
Writes screening results with risk flags to Excel
"""
import pandas as pd
from pathlib import Path

def write_results_to_excel(results, output_path, regime_summary=None):
    """
    Write dislocation screening results to Excel
    
    Args:
        results: List of result dicts
        output_path: Path to Excel file
        regime_summary: Optional dict with regime state info
    """
    # Create output directory if needed
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not results:
        print("\nNo results to write")
        return
    
    df = pd.DataFrame(results)
    
    # Sort by Z-score magnitude (most extreme first)
    df['z_score_abs'] = df['z_score'].abs()
    df = df.sort_values('z_score_abs', ascending=False)
    df = df.drop(columns=['z_score_abs'])
    
    # Reorder columns for easy scanning
    column_order = [
        'ticker',
        'signal',
        'sector',
        'z_score',
        'distance_from_mean',
        'current_price',
        'realized_vol_20d',
        'vol_percentile',
        'pe',
        'sector_median_pe',
        'forward_pe',
        'volume',
        'market_cap',
        'cluster_risk',
        'cluster_risk_note',
        'elevated_vol_regime',
        'vol_regime_note',
        'sector_relative'
    ]
    
    # Only include columns that exist
    column_order = [col for col in column_order if col in df.columns]
    df = df[column_order]
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # Main results sheet
        df.to_excel(writer, index=False, sheet_name='Dislocation Signals')
        
        # Format worksheet
        workbook = writer.book
        worksheet = writer.sheets['Dislocation Signals']
        
        # Format numbers
        number_format = workbook.add_format({'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.00%'})
        
        # Apply formats
        worksheet.set_column('D:D', 12, number_format)  # z_score
        worksheet.set_column('E:E', 15, number_format)  # distance_from_mean
        worksheet.set_column('F:F', 12, number_format)  # current_price
        worksheet.set_column('G:G', 15, number_format)  # realized_vol_20d
        worksheet.set_column('H:H', 12, number_format)  # vol_percentile
        worksheet.set_column('I:K', 12, number_format)  # PE metrics
        
        # Conditional formatting for signals
        signal_format_long = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        signal_format_short = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        
        # Apply conditional formatting
        for row_num in range(1, len(df) + 1):
            if df.iloc[row_num - 1]['signal'] == 'LONG':
                worksheet.write(row_num, 1, 'LONG', signal_format_long)
            elif df.iloc[row_num - 1]['signal'] == 'SHORT':
                worksheet.write(row_num, 1, 'SHORT', signal_format_short)
        
        # Add regime summary sheet if provided
        if regime_summary:
            summary_df = pd.DataFrame([regime_summary]).T
            summary_df.columns = ['Value']
            summary_df.to_excel(writer, sheet_name='Regime State')
    
    print(f"\n✓ Results saved to: {output_path}")
    print(f"  Total signals: {len(df)}")
    print(f"  Sorted by Z-score magnitude (most extreme first)")


def print_top_signals(results, n=20):
    """
    Print top N signals to console
    """
    if not results:
        print("\nNo signals to display")
        return
    
    df = pd.DataFrame(results)
    df['z_score_abs'] = df['z_score'].abs()
    df = df.sort_values('z_score_abs', ascending=False)
    
    print("\n" + "="*80)
    print(f"TOP {min(n, len(df))} SIGNALS (by Z-score magnitude)")
    print("="*80)
    
    display_cols = ['ticker', 'signal', 'sector', 'z_score', 'realized_vol_20d', 
                   'pe', 'cluster_risk', 'elevated_vol_regime']
    
    # Only show columns that exist
    display_cols = [col for col in display_cols if col in df.columns]
    
    display_df = df[display_cols].head(n)
    
    print(display_df.to_string(index=False))
    print("\n" + "="*80)