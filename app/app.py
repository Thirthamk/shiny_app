from shiny import App, render, ui
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns


app_ui = ui.page_fluid(
    ui.output_table("table"),
)


def server(input, output, session):
    @output
    @render.table
    def table():
        infile = Path(__file__).parent / "../data.tsv"
        df = pd.read_csv(infile, sep="\t")
        return df


app = App(app_ui, server)
