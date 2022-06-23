import eurostat



avail_sdmx_df = eurostat.get_avail_sdmx_df()
keyword = 'tourist'
subset = eurostat.subset_avail_sdmx_df(avail_sdmx_df, keyword)
print(subset.to_string())


codes = subset.index.values.tolist()
print(codes)


code_selection=['tour_occ_nim',
                #'tour_occ_ninat'
                ]

for code in code_selection:
    dims = eurostat.get_sdmx_dims(code)
    has_cy = False
    dim_cy=None
    for dim in dims:
        dic = eurostat.get_sdmx_dic(code, dim)
        if not dic:
            continue
        if 'CY' in dic:
            dim_cy=dim
            break
    if not dim_cy:
        continue
    

    for dim in dims:
        print(dim)
        dic = eurostat.get_sdmx_dic(code, dim)
        print(dic)


    print(code)
    print(subset.loc[[code]].to_string())
    print(dim_cy)
    dic = eurostat.get_sdmx_dic(code, dim_cy)
    print(dic)

    flags = eurostat.get_sdmx_dic(code, 'OBS_STATUS')
    print(flags)
    

    StartPeriod = 2000
    EndPeriod = 2022
    filter_pars = {dim_cy: ['CY']}
    
    df=eurostat.get_sdmx_data_df(code, StartPeriod, EndPeriod, filter_pars, flags = False, verbose=True)
    print(df)
    print(df.columns.to_list())
    