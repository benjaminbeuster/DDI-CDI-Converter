from __future__ import annotations
import typing as t
from pathlib import Path
import pandas as pd
import pyreadstat as pyr
pd.set_option('display.max_rows', 2500)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

def read_sav(filename: Path, encoding="utf-8", missings=True):
    kwargs = dict(
        filename_path=str(filename),
        user_missing=missings,
        dates_as_pandas_datetime=True,
    )
    try:
        df, meta = pyr.read_sav(encoding=encoding, **kwargs)
    except Exception:
        df, meta = pyr.read_sav(encoding="LATIN1", **kwargs)
    # recode dtype
    df = df.convert_dtypes()
    # recode string variables
    for var in df.columns:
        if df[var].dtype == 'string':
            df[[var]].replace({'': pd.NA}, inplace=True)
    df.attrs["datafile"] = "file"
    return df, meta

###################################################################

def create_variable_view(df_meta):
    # Extract the attributes from df_meta
    label = df_meta.column_names_to_labels
    values = df_meta.variable_value_labels
    missing = df_meta.missing_ranges
    format = df_meta.original_variable_types
    measure = df_meta.variable_measure

    # Convert dictionaries into individual dataframes
    df_label = pd.DataFrame(list(label.items()), columns=['name', 'label'])
    df_format = pd.DataFrame(list(format.items()), columns=['name', 'format'])
    df_measure = pd.DataFrame(list(measure.items()), columns=['name', 'measure'])

    # For values and missing, we will handle them differently since they have dictionaries/lists inside
    df_values_list = [{'name': k, 'values': str(v)} for k, v in values.items()]  # Convert values to string
    df_values = pd.DataFrame(df_values_list)

    df_missing_list = [{'name': k, 'missing': str(v)} for k, v in missing.items()]  # Convert missing values to string
    df_missing = pd.DataFrame(df_missing_list)

    # Merge dataframes on the 'name' column
    variable_view = df_label.merge(df_values, on='name', how='outer') \
        .merge(df_missing, on='name', how='outer') \
        .merge(df_format, on='name', how='outer') \
        .merge(df_measure, on='name', how='outer')

    return variable_view[['name', 'format', 'measure', 'label', 'values', 'missing']]

