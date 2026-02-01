"""Monte Carlo Risk Analysis Engine - uses split modules"""
from mc_data import download_data, set_starting_prices
from mc_stats import calculate_statistics
from mc_simulation import run_monte_carlo
from mc_percentiles import calculate_percentiles
from mc_viz import create_visualization

class MonteCarloRiskEngine:
    def __init__(self, stock_symbol, benchmark_symbol, starting_capital, days_to_simulate,
                 num_simulations, historical_window, max_tolerable_loss_pct,
                 custom_stock_price=None, custom_benchmark_price=None):
        
        self.stock_symbol = stock_symbol
        self.benchmark_symbol = benchmark_symbol
        self.starting_capital = starting_capital
        self.days_to_simulate = days_to_simulate
        self.num_simulations = num_simulations
        self.historical_window = historical_window
        self.max_tolerable_loss_pct = max_tolerable_loss_pct
        
        # Download data
        self.stock_data, self.benchmark_data = download_data(
            stock_symbol, benchmark_symbol, historical_window
        )
        
        # Set prices
        self.stock_price, self.benchmark_price = set_starting_prices(
            self.stock_data, self.benchmark_data, stock_symbol, benchmark_symbol,
            custom_stock_price, custom_benchmark_price
        )
        
        # Calculate stats
        stats = calculate_statistics(
            self.stock_data, self.benchmark_data, historical_window, stock_symbol, benchmark_symbol
        )
        self.stock_volatility = stats['stock_volatility']
        self.benchmark_volatility = stats['benchmark_volatility']
        self.correlation = stats['correlation']
        self.beta = stats['beta']
        self.stock_expected_return = stats['stock_expected_return']
        self.benchmark_expected_return = stats['benchmark_expected_return']
        
        # Run simulation
        sim_results = run_monte_carlo(
            self.stock_price, self.benchmark_price, stats, days_to_simulate, num_simulations
        )
        self.stock_paths = sim_results['stock_paths']
        self.benchmark_paths = sim_results['benchmark_paths']
        self.stock_final_returns = sim_results['stock_final_returns']
        self.benchmark_final_returns = sim_results['benchmark_final_returns']
        
        # Calculate percentiles
        self.stock_percentiles, self.benchmark_percentiles = calculate_percentiles(
            self.stock_final_returns, self.benchmark_final_returns
        )
        
        print("\n✓ Initialization complete!")
    
    def run_full_analysis(self):
        """Generate visualization"""
        data = {
            "stock_symbol": self.stock_symbol,
            "benchmark_symbol": self.benchmark_symbol,
            "num_simulations": self.num_simulations,
            "days_to_simulate": self.days_to_simulate,
            "stock_paths": self.stock_paths,
            "benchmark_paths": self.benchmark_paths,
            "stock_price": self.stock_price,
            "benchmark_price": self.benchmark_price,
            "stock_final_returns": self.stock_final_returns,
            "benchmark_final_returns": self.benchmark_final_returns,
            "stock_percentiles": self.stock_percentiles,
            "benchmark_percentiles": self.benchmark_percentiles,
            "stock_data": self.stock_data,
            "benchmark_data": self.benchmark_data,
            "historical_window": self.historical_window,
            "beta": self.beta,
            "correlation": self.correlation,
            "stock_volatility": self.stock_volatility,
            "benchmark_volatility": self.benchmark_volatility,
            "stock_expected_return": self.stock_expected_return,
            "benchmark_expected_return": self.benchmark_expected_return,
            "starting_capital": self.starting_capital,
            "max_tolerable_loss_pct": self.max_tolerable_loss_pct,
            "custom_stock_price": getattr(self, 'custom_stock_price', None)
        }
        
        return create_visualization(data)