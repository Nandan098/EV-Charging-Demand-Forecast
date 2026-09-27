from data_cleaning import clean_data
from create_dimensions import build_dims
from eda import run_eda
from feature_engineering import build_features
from train_model import train
from load_sqlite import build_db
from forecast_next_7_days import forecast

if __name__=='__main__':
    clean_data()
    build_dims()
    run_eda()
    build_features()
    metrics=train()
    # train_model.py creates the full model artifact; use it to build a recursive 7-day forecast.
    forecast(7)
    build_db()
    print('Full pipeline complete.')
    print(metrics)
