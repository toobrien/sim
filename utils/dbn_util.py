import polars as pl


def strptime(
    df:         pl.DataFrame,
    from_col:   str,
    to_col:     str, 
    FMT:        str, 
    tz:         str
) -> pl.DataFrame:

    if df[from_col].dtype == pl.String:

        df = df.with_columns(
            pl.col(
                from_col
            ).cast(
                pl.Datetime
            ).dt.convert_time_zone(
                tz
            ).dt.strftime(
                FMT
            ).alias(
                to_col
            )
        )
    
    else:

        # datetime

        df = df.with_columns(
            pl.col(
                from_col
            ).dt.convert_time_zone(
                tz
            ).dt.strftime(
                FMT
            ).alias(
                to_col
            )
        )

    return df