import pandas as pd
UNWANTED = ['.DS_Store', '.gitkeep']

def add_stats(table, axis=1, descriptive_cols=0):
    i = descriptive_cols
    table = table.copy()
    if axis == 0:
        index = ['sum', 'ave']
        df = pd.DataFrame(index=index, columns=table.columns)
        df.loc['sum'] = table.astype(float).sum(axis=axis, numeric_only=True)
        df.loc['ave'] = table.astype(float).mean(axis=axis)
    else:
        df = pd.DataFrame(index=table.index)
        df['sum'] = table.iloc[:,i:].astype(float).sum(axis=axis, numeric_only=True)
        df['ave'] = table.iloc[:,i:].astype(float).mean(axis=axis)
    return pd.concat([table, df], axis=axis)
