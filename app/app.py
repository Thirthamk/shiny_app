from shiny import App, render, ui
from pathlib import Path
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing


app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file("file1", "Choose a file to upload:", multiple=True),
            ui.input_radio_buttons("type", "Type:", ["xlsx"]),
        ),
        ui.panel_main(
            ui.h2({"style": "text-align: center;"}, "Product Sales Information"),
            ui.output_plot("result_decompose"),
        )
    )
)


def server(input, output, session):
    @output
    @render.plot(alt="Plot of Product Sales Information data - Decomposed")
    def result_decompose():
        
        # Import data from file
        file_data = input.file1()
        if not file_data:
            return

        if input.type() == "xlsx":
            df = pd.read_excel(file_data[0]['datapath'], parse_dates=True)

        sales_df = df[['PO Date', 'Year', 'Month', 'Sales Amt']].groupby(['PO Date']).sum()
        sales_df['Sales Amt'] = sales_df['Sales Amt'].astype(int)
        
        # Perform Holt-Winters Forecasting model on data
        sales_df.index = pd.DatetimeIndex(sales_df.index).to_period('M')
        sales_df.index.asfreq = 'MS'
        period = 36
        
        # Define smoothing level based on time period
        alpha = 1/(2 * period)
    
        # Perform Holt-Winters Forecasting model on data

        # Determine if trend component is available. If there is a trend, then Holt-Winters Single Exponential Smoothing is not appropriate
        # decompose_result = seasonal_decompose(sales_df[['Sales Amt']], model='additive',period=period)

        sales_df['HWES1'] = SimpleExpSmoothing(sales_df['Sales Amt']).fit(smoothing_level=alpha,optimized=False).fittedvalues
        sales_df['HWES2_ADD'] = ExponentialSmoothing(sales_df['Sales Amt'],trend='add').fit().fittedvalues
        sales_df['HWES3_ADD'] = ExponentialSmoothing(sales_df['Sales Amt'],trend='add',seasonal='add',seasonal_periods=12).fit().fittedvalues
        
        # Split data into train and test set - use 75/25 split
        # rows_number = len(sales_df.index)
        # train_index = int(0.75 * rows_number)
        # train_set = sales_df['HWES3_ADD'][:train_index]
        # test_set = sales_df['HWES3_ADD'][train_index:]
        # fitted_model = ExponentialSmoothing(sales_df['Sales Amt'][],trend='add',seasonal='add',seasonal_periods=12).fit()
        

        plot = sales_df[['Sales Amt','HWES2_ADD','HWES3_ADD']].plot(
            title="Holt Winters Single Exponential Smoothing - Product Sales Information"
        ).ticklabel_format(axis='y', style='plain')

        return plot



app = App(app_ui, server)
