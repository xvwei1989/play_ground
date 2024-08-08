import pandas as pd
import numpy as np
def cal_iv(df, feats, target='flag', bins=10, return_all=False): 
    df = df[[feats,target]].copy()
    if df[feats].nunique()<=5:
        pass
    else:
        df[feats] = pd.qcut(df[feats], q=10, duplicates='drop')
        d1 = pd.crosstab(df[feats],df[target])
        d1['bad_ratio'] = d1[1]/(d1[0]+d1[1])
        d1['bad_pct'] = d1[1]/d1[1].sum()
        d1['good_pct'] = d1[0]/d1[0].sum()
        d1['iv'] = d1.apply(lambda x: (x.bad_pct-x.good_pct)*np.log((x.bad_pct+0.0001)/(x.good_pct+0.0001)), axis=1)
    if return_all:
        return d1.iv.sum(), d1
    else:
        return d1.iv.sum()
