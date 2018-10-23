def get_best_cut(d, good_total, bad_total):
    good = d.good.sum()
    bad = d.bad.sum()
    iv0=(1.0*good/good_total-1.0*bad/bad_total)*np.log(1.0*good*bad_total/(bad*good_total))
    max_ind = -1
    for ind in d.index[:-1]:
        good1 = d[d.index<=ind].good.sum()
        bad1 = d[d.index<=ind].bad.sum()
        good2 = d[d.index>ind].good.sum()
        bad2 = d[d.index>ind].bad.sum()
        good1_ratio = 1.0*good1/good_total
        bad1_ratio = 1.0*bad1/bad_total
        good2_ratio = 1.0*good2/good_total
        bad2_ratio = 1.0*bad2/bad_total
        iv = (good1_ratio-bad1_ratio)*np.log(good1_ratio/bad1_ratio) + (good2_ratio-bad2_ratio)*np.log(good2_ratio/bad2_ratio)
        if iv > iv0:
            iv0 = iv
            max_ind = ind
    if max_ind != -1:
        cut_point = d.loc[max_ind]['bins'].right
        return iv0, max_ind, cut_point
    else:
        return iv0, max_ind

def get_best_iv(d):
    good_total = d.good.sum()
    bad_total = d.bad.sum()
    cut1  = get_best_cut(d, good_total, bad_total)
    d1 = d[d.index<=cut1[1]]
    d2 = d[d.index>cut1[1]]
    cut2 = get_best_cut(d1, good_total, bad_total)
    cut3 = get_best_cut(d2, good_total, bad_total)
    if cut2[1] != -1:
        if cut3[1] != -1:
            return {'cut_points': (cut2[2], cut1[2], cut3[2]), 'iv': cut2[0]+cut3[0]}
        else:
            return {'cut_points': (cut2[2], cut1[2]), 'iv': cut2[0]+cut3[0]}
    else:
        if cut3[1] != -1:
            return {'cut_points': (cut1[2], cut3[2]), 'iv': cut2[0]+cut3[0]}
        else:
            return {'cut_points': (cut2[2]), 'iv': cut2[0]+cut3[0]}
def get_bin(x, y, min_pct = 0.01, rounding=2, mono=True):
    df = pd.DataFrame([x, y]).T
    df.columns = ['x','y']
    df.sort_values('x', inplace=True)
    cut_points0 = np.unique(np.round([min(x)-1]+[np.percentile(x, min_pct*k*100) for k in range(1, int(1/min_pct))]+[max(x)+1], rounding))
    df['ind'] = pd.cut(df.x, cut_points0, precision=rounding)
    df1 = df.groupby(['ind','y']).count().reset_index()
    to_remove = set(list(df1[df1.x.isnull()].apply(lambda x: x.ind.right,1)))
    if max(to_remove) > max(x):
        cut_points = np.round([k for k in cut_points0[:-1] if k not in to_remove][:-1]+[max(x)+1], rounding)
    else:
        cut_points = np.round([k for k in cut_points0 if k not in to_remove], rounding)
    df['ind'] = pd.cut(df.x, cut_points, precision=rounding)
    df1 = df.groupby(['ind','y']).count().reset_index().pivot(index='ind', columns='y', values='x')
    df1.reset_index(inplace=True)
    df1.columns = ['bins', 'good', 'bad']
    print(df1)
    cut_points = np.round([min(x)-1]+ list(get_best_iv(df1)['cut_points'])+ [max(x)+1], rounding)
    df['ind'] = pd.cut(df.x, cut_points, precision=rounding)
    df1 = df.groupby(['ind','y']).count().reset_index().pivot(index='ind', columns='y', values='x')
    df1.reset_index(inplace=True)
    df1.columns = ['bins', 'good', 'bad']
    good_total = df1.good.sum()
    bad_total = df1.bad.sum()
    df1['total'] = df1.good+df1.bad
    df1['bad_rate'] = df1.bad/df1.total
    df1['good_ratio'] = df1.good/good_total
    df1['bad_ratio'] = df1.bad/bad_total
    df1['woe'] = (df1.good_ratio/df1.bad_ratio).apply(np.log)
    df1['iv'] = (df1.good_ratio-df1.bad_ratio)*df1.woe
    df1['good_cum'] = df1.good.cumsum()/good_total
    df1['bad_cum'] = df1.bad.cumsum()/bad_total
    df1['KS'] = df1.good_cum-df1.bad_cum
    return df1
