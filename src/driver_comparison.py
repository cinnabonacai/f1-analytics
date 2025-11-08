"""
Driver Comparison Tool
Compare two drivers across multiple metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class DriverComparison:
    """Compare F1 drivers across multiple metrics"""
    
    def __init__(self, merged_df, driver_stats, cleaner):
        self.merged_df = merged_df
        self.driver_stats = driver_stats
        self.cleaner = cleaner
    
    def compare_drivers(self, driver1_name, driver2_name):
        """Compare two drivers"""
        driver1_stats = self.driver_stats[self.driver_stats['full_name'] == driver1_name]
        driver2_stats = self.driver_stats[self.driver_stats['full_name'] == driver2_name]
        
        if driver1_stats.empty or driver2_stats.empty:
            raise ValueError("One or both drivers not found")
        
        driver1_id = driver1_stats['driverId'].values[0]
        driver2_id = driver2_stats['driverId'].values[0]
        
        # Get race history
        driver1_history = self.merged_df[self.merged_df['driverId'] == driver1_id]
        driver2_history = self.merged_df[self.merged_df['driverId'] == driver2_id]
        
        # Calculate comparison metrics
        comparison = {
            'driver1': driver1_name,
            'driver2': driver2_name,
            'metrics': {}
        }
        
        # Basic stats
        comparison['metrics']['wins'] = {
            'driver1': int(driver1_stats['wins'].values[0]),
            'driver2': int(driver2_stats['wins'].values[0])
        }
        
        comparison['metrics']['podiums'] = {
            'driver1': int(driver1_stats['podiums'].values[0]),
            'driver2': int(driver2_stats['podiums'].values[0])
        }
        
        comparison['metrics']['total_points'] = {
            'driver1': int(driver1_stats['total_points'].values[0]),
            'driver2': int(driver2_stats['total_points'].values[0])
        }
        
        comparison['metrics']['races'] = {
            'driver1': int(driver1_stats['races'].values[0]),
            'driver2': int(driver2_stats['races'].values[0])
        }
        
        comparison['metrics']['win_rate'] = {
            'driver1': driver1_stats['win_rate'].values[0] * 100,
            'driver2': driver2_stats['win_rate'].values[0] * 100
        }
        
        comparison['metrics']['podium_rate'] = {
            'driver1': driver1_stats['podium_rate'].values[0] * 100,
            'driver2': driver2_stats['podium_rate'].values[0] * 100
        }
        
        comparison['metrics']['dnf_rate'] = {
            'driver1': driver1_stats['dnf_rate'].values[0] * 100,
            'driver2': driver2_stats['dnf_rate'].values[0] * 100
        }
        
        # Average position
        comparison['metrics']['avg_position'] = {
            'driver1': driver1_history['position'].mean(),
            'driver2': driver2_history['position'].mean()
        }
        
        # Best position
        comparison['metrics']['best_position'] = {
            'driver1': driver1_history['position'].min(),
            'driver2': driver2_history['position'].min()
        }
        
        # Position change (overtaking)
        comparison['metrics']['avg_position_change'] = {
            'driver1': driver1_history['position_change'].mean(),
            'driver2': driver2_history['position_change'].mean()
        }
        
        # Common races (if they raced in same period)
        common_years = set(driver1_history['year'].unique()) & set(driver2_history['year'].unique())
        comparison['common_years'] = len(common_years)
        
        return comparison
    
    def create_comparison_chart(self, comparison):
        """Create visualization comparing two drivers"""
        metrics_to_plot = ['wins', 'podiums', 'total_points', 'win_rate', 'podium_rate']
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, metric in enumerate(metrics_to_plot):
            if metric in comparison['metrics']:
                values = [
                    comparison['metrics'][metric]['driver1'],
                    comparison['metrics'][metric]['driver2']
                ]
                labels = [comparison['driver1'], comparison['driver2']]
                
                axes[idx].bar(labels, values, color=['#E10600', '#1E41FF'], alpha=0.7)
                axes[idx].set_title(f'{metric.replace("_", " ").title()}', fontweight='bold')
                axes[idx].set_ylabel('Value')
                axes[idx].grid(alpha=0.3, axis='y')
        
        # Performance over time (if common years exist)
        if comparison['common_years'] > 0:
            driver1_id = self.driver_stats[self.driver_stats['full_name'] == comparison['driver1']]['driverId'].values[0]
            driver2_id = self.driver_stats[self.driver_stats['full_name'] == comparison['driver2']]['driverId'].values[0]
            
            driver1_yearly = self.merged_df[self.merged_df['driverId'] == driver1_id].groupby('year')['points'].sum()
            driver2_yearly = self.merged_df[self.merged_df['driverId'] == driver2_id].groupby('year')['points'].sum()
            
            common_years = sorted(set(driver1_yearly.index) & set(driver2_yearly.index))
            
            axes[5].plot(common_years, [driver1_yearly[y] for y in common_years], 
                        marker='o', label=comparison['driver1'], linewidth=2, color='#E10600')
            axes[5].plot(common_years, [driver2_yearly[y] for y in common_years], 
                        marker='s', label=comparison['driver2'], linewidth=2, color='#1E41FF')
            axes[5].set_title('Points Over Common Years', fontweight='bold')
            axes[5].set_xlabel('Year')
            axes[5].set_ylabel('Points')
            axes[5].legend()
            axes[5].grid(alpha=0.3)
        else:
            axes[5].text(0.5, 0.5, 'No common racing years', 
                         ha='center', va='center', transform=axes[5].transAxes)
            axes[5].set_title('Points Over Time', fontweight='bold')
        
        plt.suptitle(f"Driver Comparison: {comparison['driver1']} vs {comparison['driver2']}", 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return fig
    
    def print_comparison(self, comparison):
        """Print formatted comparison"""
        print("=" * 80)
        print(f"DRIVER COMPARISON: {comparison['driver1']} vs {comparison['driver2']}")
        print("=" * 80)
        
        for metric, values in comparison['metrics'].items():
            driver1_val = values['driver1']
            driver2_val = values['driver2']
            
            # Format based on metric type
            if isinstance(driver1_val, float):
                if 'rate' in metric:
                    print(f"{metric.replace('_', ' ').title():25s} {driver1_val:>8.2f}%  vs  {driver2_val:>8.2f}%")
                else:
                    print(f"{metric.replace('_', ' ').title():25s} {driver1_val:>8.2f}  vs  {driver2_val:>8.2f}")
            else:
                print(f"{metric.replace('_', ' ').title():25s} {driver1_val:>8}  vs  {driver2_val:>8}")
        
        print(f"\nCommon Racing Years: {comparison['common_years']}")
        print("=" * 80)


if __name__ == "__main__":
    from src.data_cleaner import F1DataCleaner
    
    # Load data
    data_dir = Path("../data")
    cleaner = F1DataCleaner(data_dir=data_dir)
    cleaner.load_data()
    cleaner.clean_all()
    merged_df = cleaner.merge_data()
    aggregated = cleaner.create_aggregated_tables()
    
    # Compare drivers
    comparator = DriverComparison(merged_df, aggregated['driver_stats'], cleaner)
    
    # Example comparison
    driver_list = sorted(aggregated['driver_stats']['full_name'].dropna().unique())
    print("Available drivers:", driver_list[:10])
    
    if len(driver_list) >= 2:
        comparison = comparator.compare_drivers(driver_list[0], driver_list[1])
        comparator.print_comparison(comparison)
        fig = comparator.create_comparison_chart(comparison)
        plt.savefig("../reports/driver_comparison.png", dpi=300, bbox_inches='tight')
        print("\nComparison chart saved to reports/driver_comparison.png")

