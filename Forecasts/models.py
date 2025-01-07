import pandas as pd

from sktime.forecasting.ets import AutoETS
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from sktime.transformations.series.detrend import Deseasonalizer, Detrender
from statsmodels.tsa.vector_ar.vecm import *
from sklearn.metrics import mean_absolute_percentage_error


from sklearn.experimental import enable_halving_search_cv  # noqa



from sktime.forecasting.compose import (
    EnsembleForecaster,
    TransformedTargetForecaster,
    make_reduction,
)

from sktime.forecasting.trend import PolynomialTrendForecaster

from sktime.forecasting.tbats import TBATS

from sktime.forecasting.arima import (AutoARIMA)



def VECM_Modell_Automatic(df, steps, seasons):

    lag_order = select_order(data=df, maxlags=10, deterministic='cili', seasons=seasons)
    print(lag_order.summary())

    # cointegration rank
    rank_opt = select_coint_rank(df, 0, 4, method='trace', signif=0.05)
    print(rank_opt)
    vecm = VECM(endog=df, k_ar_diff=lag_order.aic, seasons=seasons, coint_rank=rank_opt.rank, deterministic='cili')
    vecm_fit = vecm.fit()

    fc = vecm_fit.predict(steps=steps)


    fc = pd.DataFrame(fc, columns=df.columns)
    return fc


def model_fit(model, df, fh, sp):
    model = str(model).lower()
    fh = np.arange(1, fh + 1)  # forecasting horizon

    if len(df) < 1:
        # Dataframe with multiple rows.  Implement desired behavior.
        pass
    else:
        df = pd.Series() if df.empty else df.iloc[:, 0]
        print(df)

    if (model == 'knn'):
        regressor_param_grid = {"n_neighbors": [1, 5, 10, 20, 250]
                               # "learning_rate": [0.1, 0.01, 0.001, 0.0001]
                                }
        forecaster_param_grid = {"window_length": [5, 10, 15, 20]}
        regressor = GridSearchCV(KNeighborsRegressor(), param_grid=regressor_param_grid)
        forecaster = TransformedTargetForecaster(
            [
                ("deseasonalize", Deseasonalizer(model="multiplicative", sp=sp)),
                ("detrend", Detrender(forecaster=PolynomialTrendForecaster(degree=1))),
                (
                    "forecast",
                    make_reduction(
                        regressor,
                        scitype="tabular-regressor",
                        window_length=20,
                        strategy="recursive",
                    ),
                ),
            ]
        )

    elif (model == 'rf'):
        regressor_param_grid = {"n_estimators": [100, 200, 300, 1000, 3000]
                              #  "learning_rate": [0.1, 0.01, 0.001, 0.0001]
                                }
        forecaster_param_grid = {"window_length": [5, 10, 15, 20]}
        regressor = GridSearchCV(RandomForestRegressor(), param_grid=regressor_param_grid)
        forecaster = TransformedTargetForecaster(
            [
                ("deseasonalize", Deseasonalizer(model="multiplicative", sp=sp)),
                ("detrend", Detrender(forecaster=PolynomialTrendForecaster(degree=1))),
                (
                    "forecast",
                    make_reduction(
                        regressor,
                        scitype="tabular-regressor",
                        window_length=20,
                        strategy="recursive",
                    ),
                ),
            ]
        )

    elif (model == 'gbr'):
        regressor_param_grid = {"n_estimators": [100, 200, 300],
                               # "learning_rate": [0.1, 0.01, 0.001, 0.0001]
                                }
        forecaster_param_grid = {"window_length": [5, 10, 15, 20]}
        regressor = GridSearchCV(GradientBoostingRegressor(), param_grid=regressor_param_grid)
        forecaster = TransformedTargetForecaster(
            [
                ("deseasonalize", Deseasonalizer(model="multiplicative", sp=sp)),
                ("detrend", Detrender(forecaster=PolynomialTrendForecaster(degree=1))),
                (
                    "forecast",
                    make_reduction(
                        regressor,
                        scitype="tabular-regressor",
                        window_length=20,
                        strategy="recursive",
                    ),
                ),
            ]
        )
    elif (model == 'tbats'):
        forecaster = TBATS(sp=sp, n_jobs=-1)
    elif (model == 'autoarima'):
        forecaster = AutoARIMA(sp=sp, n_jobs=-1, suppress_warnings=True)
    elif (model == 'ets'):
        forecaster = AutoETS(auto=True, sp=sp, n_jobs=-1)
    elif (model == 'ensemble'):
        autoets = AutoETS(auto=True, sp=sp, n_jobs=-1)
        tbats = TBATS(sp=sp, n_jobs=-1)
        arima = AutoARIMA(sp=sp, n_jobs=-1, suppress_warnings=True)
        forecaster = EnsembleForecaster(
            [
                ("autoets", autoets),
                ("arima", arima),
                ("tbats", tbats)
            ]
        )

    forecaster.fit(df)
    y_pred = forecaster.predict(fh)

    return y_pred


def VECM_Forecast_Lower_Upper(data, steps, seasons, response, start_date, freq, test=False):
    colnames_numerics_only = data.select_dtypes(include=np.number).columns.tolist()
    col=[]
    for c in colnames_numerics_only:
        if c in ['open', 'high','close','low']:
            col.append(c)
    columns = col
    df=data[col]
    try:
        # Lag order Selection
        lag_order = select_order(data=df, maxlags=20, deterministic='cili', seasons=seasons)
        print(lag_order.summary())
        # det_order = 1, k_ar_diff = 1, method = 'maxeig', signif=0.01
        # cointegration rank
        rank_opt = select_coint_rank(df, det_order=0, k_ar_diff=lag_order.aic, method='trace', signif=0.05)
        print(rank_opt)

        date = pd.DataFrame(pd.bdate_range(start=start_date, periods=steps, freq=freq), columns=(['prediction_date']))
        print(date)

        if test:
            df_train = df[:(len(df) - steps)]
            df_test = df[-steps:]
            vecm = VECM(endog=df_train, k_ar_diff=lag_order.aic, seasons=seasons, coint_rank=rank_opt.rank,
                        deterministic='cili')
            vecm_fit = vecm.fit()

            fc = vecm_fit.predict(steps=steps)
            df_fc = pd.DataFrame(fc, columns=df.columns)

            df_final = df_fc
            print("-------------------------Print Test Forecast")
            print(df_final)
            print("-------------------------------Print Actuals ")
            print(df_test)

            for c in columns:
                mape = mean_absolute_percentage_error(df_test[[str(c)]].values, df_fc[[str(c)]].values)

                print("-----Mean absolute percentage  error ")

                print(mape)



        else:

            vecm = VECM(endog=df, k_ar_diff=lag_order.aic, seasons=seasons, coint_rank=rank_opt.rank, deterministic='cili')
            vecm_fit = vecm.fit()
            forecast, lower, upper = vecm_fit.predict(steps, 0.20)

            lower = lower.round(3)
            lower_columns = [var + '_lower' for var in columns]
            df_lower = pd.DataFrame(lower, columns=lower_columns)
            granger_results = vecm_fit.test_granger_causality(caused=response, signif=0.05)
            # Granger Causality Test
            #print(granger_results.summary())
            #print(granger_results)
            # Diagonistic
            """

    
    
    
            """
            # Normal distribution Test
            #print(vecm_fit.test_normality().summary())

            #print(vecm_fit.test_normality())

            # White Noise tests for autocorrelation
            white_noise = vecm_fit.test_whiteness(nlags=steps, adjusted=True)

            print(white_noise.summary())

            # print(white_noise)

            point_forecast = forecast.round(3)
            df_pointF = pd.DataFrame(point_forecast, columns=columns)
            upper_columns = [var + '_upper' for var in columns]
            upper = upper.round(3)
            df_upper = pd.DataFrame(upper, columns=upper_columns)
            df_final = (pd.concat([df_lower, df_pointF], axis=1, join='outer')).reset_index(drop=True)
            df_final = (pd.concat([df_final, df_upper], axis=1, join='outer')).reset_index(drop=True)
            df_final=   (pd.concat([df_final, date], axis=1, join='outer')).reset_index(drop=True)


        return df_final

    except Exception as error:
        print(error)

    return ""

#  pred = VECM_Forecast_Lower_Upper(data_df,steps=10,seasons=252,response='close',start_date=td, freq='D')

if __name__ == '__main__':
 #df_numerics_only = df.select_dtypes(include=np.number)
 #colnames_numerics_only = df.select_dtypes(include=np.number).columns.tolist()
    import os
    import pandas as pd
    print(os.getcwd())
