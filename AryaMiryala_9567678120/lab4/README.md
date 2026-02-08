

---

##  Project Overview

This project implements an end-to-end algorithmic trading system using Python. We collected real-time stock data (via `yfinance`) and developed four distinct trading strategies to analyze price trends and execute buy/sell signals:

1.  **Simple Moving Average (SMA):** A baseline trend-following strategy.
2.  **ARIMA:** A statistical model for time-series forecasting.
3.  **Hybrid Strategy (SMA + RSI):** A combined approach using momentum (RSI) to filter trend signals.
4.  **LSTM (Long Short-Term Memory):** A deep learning neural network for price prediction.

The performance of these models was evaluated in a mock trading environment using metrics such as **Total Portfolio Value**, **Annualized Returns**, and the **Sharpe Ratio**.

##  Requirements & Dependencies

The solution is designed to run in a Python environment (specifically Google Colab). The following libraries are required:

* `yfinance` (Data collection)
* `pandas` & `numpy` (Data manipulation)
* `statsmodels` (ARIMA modeling)
* `tensorflow` / `keras` (LSTM modeling)
* `sklearn` (Metrics and preprocessing)
* `matplotlib` (Visualization)

##  Files Included

* **`Lab4_DSCI560.ipynb`**: The primary executable file containing the complete code for data collection, algorithm implementation, backtesting, and evaluation.
* **`Meeting_Minutes.pdf`**: Documentation of daily team discussions and workflow.

## Installation & Execution Instructions (Google Colab)

For the most reliable execution, we recommend running the solution via Google Colab, as it pre-configures the necessary environment for the LSTM and ARIMA models.

1.  **Open Google Colab:** Go to [https://colab.research.google.com/](https://colab.research.google.com/).
2.  **Upload the Notebook:** Click `File` > `Upload notebook` and select the submitted `Lab4_DSCI560.ipynb` file.
3.  **Install Dependencies:** The first cell of the notebook contains the command `!pip install yfinance`. Ensure this cell is run first to install the necessary data fetcher.
4.  **Run All Cells:** Go to `Runtime` > `Run all` (or `Run all cells`).
    * *Note: The LSTM model training may take a few moments to complete.*
5.  **View Results:** The notebook will output the dataframe heads, training logs, and a final summary comparing the performance metrics of all four models.

##  Summary of Results & Rationale

After backtesting all strategies on Apple (AAPL) stock data from 2024–2026:

* **Best Model:** The Hybrid Model (SMA + RSI).

### Rationale
While the Simple Moving Average generated slightly higher raw profits, the **Hybrid Model achieved the highest Sharpe Ratio (0.77)**. This indicates that it generated the best risk-adjusted returns by using the RSI (Relative Strength Index) to avoid buying into overextended (overbought) positions, offering a more stable investment strategy than the standalone SMA or the predictive ARIMA/LSTM models.