# encodes listings with features using encoder used to train model
# predicts the product of each listing and saves the df to csv

import links
import pickle
import pandas as pd
from model_training import FEATURES, PandasLabelEncoder
pd.set_option('mode.chained_assignment', None)


def main():
    source_df = pd.read_excel(links.LISTINGS_WITH_FEATURES, sheet_name="source")
    loaded_model = pickle.load(open(links.MODEL_PICKLE, 'rb'))
    enc = pickle.load(open(links.ENCODING_PICKLE, 'rb'))

    X_prod = source_df[FEATURES]
    for feat in FEATURES:
        X_prod.loc[:, feat] = X_prod[feat].fillna("NONE").astype(str).values

    X_prod_enc = enc.transform(X_prod)
    res = loaded_model.predict(X_prod_enc)
    df_res = pd.DataFrame(list(res), columns=['target'])
    source_df['model_product'] = df_res['target']

    source_df.to_csv(links.LISTINGS_WITH_PREDICTIONS, index=False)


if __name__ == "__main__":
    main()
