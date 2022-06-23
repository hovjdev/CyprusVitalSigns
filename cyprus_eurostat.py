import eurostat
import datetime

DEBUG=True


def db_print(s, debug=DEBUG):
    if debug:
        print(s)


def get_codes(keyword = 'tourist'):
    avail_sdmx_df = eurostat.get_avail_sdmx_df()
    subset = eurostat.subset_avail_sdmx_df(avail_sdmx_df, keyword)
    db_print(subset.to_string())


    codes = subset.index.values.tolist()
    db_print(codes)
    return codes



def get_data(code, filters):

    avail_sdmx_df = eurostat.get_avail_sdmx_df()


    db_print(f">>>Getting data for code {code}")
    dims = eurostat.get_sdmx_dims(code)
    has_cy = False
    dim_cy=None
    for dim in dims:
        dic = eurostat.get_sdmx_dic(code, dim)
        db_print(dic)
        if not dic:
            continue
        if 'CY' in dic:
            dim_cy=dim
            break
    if not dim_cy:
        db_print("CY not found")
        return None
    

    for dim in dims:
        db_print(dim)
        dic = eurostat.get_sdmx_dic(code, dim)
        db_print(dic)


    db_print(code)
    db_print(avail_sdmx_df.loc[[code]].to_string())
    db_print(dim_cy)
    dic = eurostat.get_sdmx_dic(code, dim_cy)
    db_print(dic)

    flags = eurostat.get_sdmx_dic(code, 'OBS_STATUS')
    db_print(flags)
    

    StartPeriod = 2000
    currentDateTime = datetime.datetime.now()
    date = currentDateTime.date()
    year = date.strftime("%Y")
    EndPeriod = int(year)
    filter_pars = filters[code]
    
    df=eurostat.get_sdmx_data_df(code, StartPeriod, EndPeriod, filter_pars, flags = False, verbose=True)
    db_print(df)
    db_print(df.columns.to_list())

    return df
        


if __name__ == "__main__":

    codes = get_codes(keyword = 'goals')

    code_selection=['avia_tf_cm',
                    'tour_occ_arm',
                    't2020_rd300',

    ]

    filters = {
        'avia_tf_cm': {'GEO': ['CY'], 'UNIT':['NR']},
        'tour_occ_arm': {'GEO': ['CY'], 'UNIT':['NR'], 'NACE_R2':['I551'], 'C_RESID':['FOR']},
        't2020_rd300' : {'GEO': ['CY']},    
    }


    for code in code_selection:
        df = get_data(code, filters)
        print(df)


