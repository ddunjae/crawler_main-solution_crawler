import pandas as pd


def dataframe(columns, istype):
    if columns:
        df = {i: [] for i in columns}
    else:
        df = {
            "lot": [],
            "img": [],
            "artist_kor": [],
            "artist_eng": [],
            "artist_birth":[],
            "artist_death":[],
            "title_kor": [],
            "title_eng": [],
            "mfg_date": [],
            "height": [],
            "width": [],
            "depth": [],
            "size_table": [],
            "material_kind": [],
            "material_kor": [],
            "material_eng": [],
            "signed": [],
            "exhibited": [],
            "provenance": [],
            "literature": [],
            "catalogue": [],
            "frame": [],
            "certification": [],
            "condition_report": [],
            "company": [],
            "auction_name": [],
            "on_off": [],
            "transact_date": [],
            "location": [],
            "currency": [],
            "start_price": [],
            "hammer_price": [],
            "selling_price": [],
            "estimate_min": [],
            "estimate_max": [],
            "usd_hammer_price": [],
            "usd_selling_price": [],
            "usd_estimate_min": [],
            "usd_estimate_max": [],
            "description": [],
            "competition": [],
        }
    if istype == dict:
        return df
    else:
        return pd.DataFrame(df)
