"""
Time Series Forecasting for Sales Prediction
Implements both Prophet and ARIMA models for 3-6 month forecasts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class TimeSeriesForecaster:
    """
    Time series forecasting for sales prediction using Prophet and ARIMA methods
    """
    
    def __init__(self, filepath):
        """Initialize forecaster with cleaned data"""
        self.df = pd.read_csv(filepath, parse_dates=['Order_Date'])
        
        # Aggregate daily sales
        self.daily_sales = self.df.groupby(self.df['Order_Date'].dt.date)['Sales'].sum().reset_index()
        self.daily_sales.columns = ['Date', 'Sales']
        self.daily_sales['Date'] = pd.to_datetime(self.daily_sales['Date'])
        
        # Aggregate monthly sales
        self.monthly_sales = self.df.groupby(self.df['Order_Date'].dt.to_period('M')).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count'
        }).reset_index()
        self.monthly_sales['Order_Date'] = self.monthly_sales['Order_Date'].dt.to_timestamp()
        self.monthly_sales.columns = ['Date', 'Sales', 'Profit', 'Orders']
        
        print("="*70)
        print("TIME SERIES FORECASTING - SALES PREDICTION")
        print("="*70)
        print(f"\nDate Range: {self.monthly_sales['Date'].min().date()} to {self.monthly_sales['Date'].max().date()}")
        print(f"Total Months: {len(self.monthly_sales)}")
    
    def forecast_with_prophet(self, periods=6):
        """
        Forecast sales using Facebook Prophet
        
        Parameters:
        -----------
        periods : int
            Number of months to forecast (default: 6)
        
        Returns:
        --------
        forecast_df : DataFrame with forecast results
        """
        try:
            from prophet import Prophet
        except ImportError:
            print("⚠️  Prophet not installed. Installing...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'prophet', '-q'])
            from prophet import Prophet
        
        print("\n" + "-"*70)
        print("PROPHET FORECASTING MODEL")
        print("-"*70)
        
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = self.monthly_sales[['Date', 'Sales']].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            interval_width=0.80
        )
        
        print(f"\nFitting Prophet model...")
        model.fit(prophet_df)
        
        # Make future dataframe
        future = model.make_future_dataframe(periods=periods, freq='MS')
        forecast = model.predict(future)
        
        # Extract forecast results
        forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        forecast_df.columns = ['Date', 'Forecast', 'Lower_CI', 'Upper_CI']
        forecast_df['Forecast'] = forecast_df['Forecast'].round(2)
        forecast_df['Lower_CI'] = forecast_df['Lower_CI'].round(2)
        forecast_df['Upper_CI'] = forecast_df['Upper_CI'].round(2)
        
        # Validation metrics (on test set)
        train_size = int(len(prophet_df) * 0.8)
        train = prophet_df[:train_size]
        test = prophet_df[train_size:]
        
        model_test = Prophet(yearly_seasonality=True, changepoint_prior_scale=0.05)
        model_test.fit(train)
        future_test = model_test.make_future_dataframe(periods=len(test), freq='MS')
        forecast_test = model_test.predict(future_test)
        test_forecast = forecast_test[['yhat']].tail(len(test)).reset_index(drop=True)
        
        mae = mean_absolute_error(test['y'].values, test_forecast['yhat'].values)
        rmse = np.sqrt(mean_squared_error(test['y'].values, test_forecast['yhat'].values))
        mape = np.mean(np.abs((test['y'].values - test_forecast['yhat'].values) / test['y'].values) * 100)
        
        print(f"\n[OK] Model Fit Complete!")
        print(f"\nValidation Metrics (on test set):")
        print(f"  MAE (Mean Absolute Error):     ${mae:>12,.2f}")
        print(f"  RMSE (Root Mean Squared Error): ${rmse:>12,.2f}")
        print(f"  MAPE (Accuracy):                {mape:>12.2f}%")
        
        print(f"\n{periods}-Month Forecast:")
        for idx, row in forecast_df.iterrows():
            month_str = row['Date'].strftime('%B %Y')
            ci_range = row['Upper_CI'] - row['Lower_CI']
            print(f"  {month_str:15} -> ${row['Forecast']:>12,.0f} " +
                  f"(CI: ${row['Lower_CI']:,.0f} - ${row['Upper_CI']:,.0f}, Range: ${ci_range:,.0f})")
        
        # Growth projections
        avg_historical = self.monthly_sales['Sales'].mean()
        avg_forecast = forecast_df['Forecast'].mean()
        growth_rate = ((avg_forecast - avg_historical) / avg_historical * 100)
        
        print(f"\nForecast Analysis:")
        print(f"  Historical Avg Monthly Sales: ${avg_historical:>12,.0f}")
        print(f"  Forecasted Avg Monthly Sales: ${avg_forecast:>12,.0f}")
        print(f"  Expected Growth Rate:         {growth_rate:>12.2f}%")
        
        self.prophet_forecast = forecast_df
        self.prophet_rmse = rmse
        self.prophet_model = model
        self.prophet_df = prophet_df
        
        return forecast_df
    
    def forecast_with_arima(self, periods=6):
        """
        Forecast sales using ARIMA model
        
        Parameters:
        -----------
        periods : int
            Number of months to forecast (default: 6)
        
        Returns:
        --------
        forecast_df : DataFrame with forecast results
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
            from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
        except ImportError:
            print("⚠️  statsmodels not installed. Installing...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'statsmodels', '-q'])
            from statsmodels.tsa.arima.model import ARIMA
        
        print("\n" + "-"*70)
        print("ARIMA FORECASTING MODEL")
        print("-"*70)
        
        sales_data = self.monthly_sales['Sales'].values
        
        # Find best ARIMA order using brute force (simplified AIC)
        best_aic = np.inf
        best_order = (1, 1, 1)
        
        print(f"\nSearching for optimal ARIMA parameters...")
        for p in range(0, 3):
            for d in range(0, 2):
                for q in range(0, 3):
                    try:
                        model = ARIMA(sales_data, order=(p, d, q))
                        model_fit = model.fit()
                        if model_fit.aic < best_aic:
                            best_aic = model_fit.aic
                            best_order = (p, d, q)
                    except:
                        pass
        
        print(f"[OK] Optimal ARIMA Order: {best_order}")
        
        # Fit final ARIMA model
        model = ARIMA(sales_data, order=best_order)
        model_fit = model.fit()
        
        # Forecast
        forecast_result = model_fit.get_forecast(steps=periods)
        forecast_ci = forecast_result.conf_int(alpha=0.20)
        forecast_values = forecast_result.predicted_mean
        if hasattr(forecast_values, 'values'):
            forecast_values = forecast_values.values
        
        # Handle CI - check if dataframe or array
        if isinstance(forecast_ci, pd.DataFrame):
            lower_ci = forecast_ci.iloc[:, 0].values
            upper_ci = forecast_ci.iloc[:, 1].values
        else:
            lower_ci = forecast_ci[:, 0]
            upper_ci = forecast_ci[:, 1]
        
        # Create date range for forecasts
        last_date = self.monthly_sales['Date'].max()
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=periods, freq='MS')
        
        # Build forecast dataframe
        forecast_df_arima = pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Lower_CI': lower_ci,
            'Upper_CI': upper_ci
        })
        
        forecast_df_arima['Forecast'] = forecast_df_arima['Forecast'].round(2)
        forecast_df_arima['Lower_CI'] = forecast_df_arima['Lower_CI'].round(2)
        forecast_df_arima['Upper_CI'] = forecast_df_arima['Upper_CI'].round(2)
        
        # Model diagnostics
        print(f"\nModel Summary:")
        print(f"  AIC:  {model_fit.aic:.2f}")
        print(f"  BIC:  {model_fit.bic:.2f}")
        
        # Validation
        train_size = int(len(sales_data) * 0.8)
        train = sales_data[:train_size]
        test = sales_data[train_size:]
        
        model_test = ARIMA(train, order=best_order)
        model_test_fit = model_test.fit()
        test_forecast = model_test_fit.get_forecast(steps=len(test))
        test_predictions = test_forecast.predicted_mean
        if hasattr(test_predictions, 'values'):
            test_predictions = test_predictions.values
        
        mae = mean_absolute_error(test, test_predictions)
        rmse = np.sqrt(mean_squared_error(test, test_predictions))
        mape = np.mean(np.abs((test - test_predictions) / test) * 100)
        
        print(f"\nValidation Metrics (on test set):")
        print(f"  MAE (Mean Absolute Error):     ${mae:>12,.2f}")
        print(f"  RMSE (Root Mean Squared Error): ${rmse:>12,.2f}")
        print(f"  MAPE (Accuracy):                {mape:>12.2f}%")
        
        print(f"\n{periods}-Month Forecast:")
        for idx, row in forecast_df_arima.iterrows():
            month_str = row['Date'].strftime('%B %Y')
            ci_range = row['Upper_CI'] - row['Lower_CI']
            print(f"  {month_str:15} -> ${row['Forecast']:>12,.0f} " +
                  f"(CI: ${row['Lower_CI']:,.0f} - ${row['Upper_CI']:,.0f}, Range: ${ci_range:,.0f})")
        
        # Growth projections
        avg_historical = self.monthly_sales['Sales'].mean()
        avg_forecast_arima = forecast_df_arima['Forecast'].mean()
        growth_rate_arima = ((avg_forecast_arima - avg_historical) / avg_historical * 100)
        
        print(f"\nForecast Analysis:")
        print(f"  Historical Avg Monthly Sales: ${avg_historical:>12,.0f}")
        print(f"  Forecasted Avg Monthly Sales: ${avg_forecast_arima:>12,.0f}")
        print(f"  Expected Growth Rate:         {growth_rate_arima:>12.2f}%")
        
        self.arima_forecast = forecast_df_arima
        self.arima_rmse = rmse
        self.arima_order = best_order
        
        return forecast_df_arima
    
    def create_forecast_visualizations(self):
        """Generate comprehensive forecast visualizations"""
        print("\n" + "-"*70)
        print("GENERATING FORECAST VISUALIZATIONS")
        print("-"*70)
        
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        
        # 1. Prophet Forecast
        ax1 = axes[0, 0]
        ax1.plot(self.monthly_sales['Date'], self.monthly_sales['Sales'], 
                'o-', label='Historical Sales', linewidth=2, markersize=6, color='#2E86AB')
        ax1.plot(self.prophet_forecast['Date'], self.prophet_forecast['Forecast'], 
                's--', label='Prophet Forecast', linewidth=2.5, markersize=7, color='#E63946')
        ax1.fill_between(self.prophet_forecast['Date'], 
                         self.prophet_forecast['Lower_CI'], 
                         self.prophet_forecast['Upper_CI'], 
                         alpha=0.2, color='#E63946', label='80% Confidence Interval')
        ax1.axvline(self.monthly_sales['Date'].max(), color='gray', linestyle='--', alpha=0.7)
        ax1.set_title('Prophet Forecast - 6 Month Sales Projection', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=11)
        ax1.set_ylabel('Sales ($)', fontsize=11)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax1.legend(fontsize=10, loc='upper left')
        ax1.grid(True, alpha=0.3)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 2. ARIMA Forecast
        ax2 = axes[0, 1]
        ax2.plot(self.monthly_sales['Date'], self.monthly_sales['Sales'], 
                'o-', label='Historical Sales', linewidth=2, markersize=6, color='#2E86AB')
        ax2.plot(self.arima_forecast['Date'], self.arima_forecast['Forecast'], 
                's--', label='ARIMA Forecast', linewidth=2.5, markersize=7, color='#06A77D')
        ax2.fill_between(self.arima_forecast['Date'], 
                         self.arima_forecast['Lower_CI'], 
                         self.arima_forecast['Upper_CI'], 
                         alpha=0.2, color='#06A77D', label='80% Confidence Interval')
        ax2.axvline(self.monthly_sales['Date'].max(), color='gray', linestyle='--', alpha=0.7)
        ax2.set_title(f'ARIMA {self.arima_order} Forecast - 6 Month Sales Projection', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11)
        ax2.set_ylabel('Sales ($)', fontsize=11)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax2.legend(fontsize=10, loc='upper left')
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 3. Model Comparison
        ax3 = axes[1, 0]
        months = range(1, len(self.prophet_forecast) + 1)
        x_pos = np.arange(len(months))
        width = 0.35
        
        bars1 = ax3.bar(x_pos - width/2, self.prophet_forecast['Forecast'].values, 
                       width, label='Prophet Forecast', color='#E63946', alpha=0.8)
        bars2 = ax3.bar(x_pos + width/2, self.arima_forecast['Forecast'].values, 
                       width, label='ARIMA Forecast', color='#06A77D', alpha=0.8)
        
        ax3.set_xlabel('Months Ahead', fontsize=11)
        ax3.set_ylabel('Forecasted Sales ($)', fontsize=11)
        ax3.set_title('Sales Forecast Comparison: Prophet vs ARIMA', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(months)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height/1000:.0f}K', ha='center', va='bottom', fontsize=8)
        
        # 4. Forecast Accuracy Metrics
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        metrics_text = f"""
MODEL PERFORMANCE COMPARISON

Prophet Model:
  • RMSE: ${self.prophet_rmse:,.0f}
  • Method: Additive Seasonality
  • Strengths: Robust to missing data,
    handles seasonality well
  • Best for: High-level trends

ARIMA {self.arima_order} Model:
  • RMSE: ${self.arima_rmse:,.0f}
  • Parameters: AR={self.arima_order[0]},
    I={self.arima_order[1]}, MA={self.arima_order[2]}
  • Strengths: Statistically grounded,
    captures dependencies
  • Best for: Precise short-term forecasts

Recommendation:
  {'Prophet' if self.prophet_rmse < self.arima_rmse else 'ARIMA'} appears more suitable
  for this dataset based on RMSE metric.
  
  Average Historical Monthly Sales:
  ${self.monthly_sales['Sales'].mean():,.0f}
  
  Consensus Forecast (6-month avg):
  ${(self.prophet_forecast['Forecast'].mean() + self.arima_forecast['Forecast'].mean()) / 2:,.0f}
        """
        
        ax4.text(0.05, 0.95, metrics_text, transform=ax4.transAxes, 
                fontsize=11, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        
        # Save figure
        output_path = 'd:/DA/visualizations/forecast_models.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n[OK] Forecast visualization saved: {output_path}")
        
        plt.close()
    
    def run_full_forecast(self, forecast_periods=6):
        """Execute complete forecasting pipeline"""
        print("\n" + "="*70)
        print("STARTING TIME SERIES FORECASTING PIPELINE")
        print("="*70)
        
        self.forecast_with_prophet(periods=forecast_periods)
        self.forecast_with_arima(periods=forecast_periods)
        self.create_forecast_visualizations()
        
        print("\n" + "="*70)
        print("FORECASTING PIPELINE COMPLETE")
        print("="*70)

if __name__ == "__main__":
    
    # Initialize forecaster
    forecaster = TimeSeriesForecaster('d:/DA/data/sales_data_cleaned.csv')
    
    # Run forecasting pipeline (6-month forecast)
    forecaster.run_full_forecast(forecast_periods=6)
    
    print("\n[OK] Forecasting complete! Models ready for deployment.")
