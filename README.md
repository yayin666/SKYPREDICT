# 🛫 SkyPredict - Aviation Route Forecasting & Analytics

SkyPredict is an enterprise-grade AI route forecasting and analytics platform designed to help airlines predict passenger demand, calculate network efficiency, and automatically generate capacity recommendations.

## 🚀 Key Features

1. **📊 Executive Dashboard** - High-level network KPIs and health indicators.
2. **🗃️ Data Management** - Seamless ingestion and validation of historical passenger datasets.
3. **📈 AI Forecasting** - Uses ARIMA and Exponential Smoothing models to forecast future passenger demand on a route-by-route basis with automated accuracy grading (RMSE, MAE, MAPE).
4. **🗺️ Route Analytics** - Deep dive into load factors, revenue contributions, and Pareto analyses.
5. **💡 AI Recommendations** - Rule-based engine that scans the network to recommend fleet upgrades, frequency changes, or route expansions.
6. **📥 Report Exports** - Generate CSV, Excel, and PDF reports directly from the dashboards.

## 🛠️ Technology Stack

- **Frontend UI:** Streamlit
- **Backend Database:** PostgreSQL (psycopg2, SQLAlchemy ORM)
- **Data Engineering:** Pandas, Numpy
- **Machine Learning:** statsmodels (ARIMA, Holt-Winters)
- **Data Visualization:** Plotly
- **Export Engine:** ReportLab, OpenPyXL

## 💻 Setup Instructions

1. Ensure Python 3.9+ and PostgreSQL are installed.
2. Clone the repository and navigate to the project directory.
3. Create a virtual environment: python -m venv venv
4. Activate the virtual environment:
   - Windows: .\venv\Scripts\activate
   - Mac/Linux: source venv/bin/activate
5. Install dependencies: pip install -r requirements.txt
6. Create a PostgreSQL database named skypredict.
7. Configure the database connection in database/connection.py.
8. Run the application: streamlit run run.py

## 📊 Sample Data
A sample augmented dataset (PIA_2026_Augmented.csv) is provided in the data/raw/ folder for testing.
with column names:-
Flight_ID
Date
Month
Day_of_Week
Departure_City
Arrival_City
Route_Type
Aircraft_Type
Flight_Duration_Minutes
Passengers
Seat_Capacity
Load_Factor_%
Ticket_Price_USD
Revenue_USD
Delay_Minutes
Delay_Category
On_Time_Status
Weather_Condition
Fuel_Consumption_Liters
CO2_Emissions_kg
Customer_Rating
Customer_Feedback
Year
