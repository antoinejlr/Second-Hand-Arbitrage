# trains a classification model
# using the features extracted from the listing titles
# to predict the product featured in each listing
# serialises the model and encoder

import links
import numpy as np
import pandas as pd
import pickle

from collections import defaultdict
from sklearn.naive_bayes import GaussianNB
from sklearn.base import BaseEstimator, TransformerMixin


# Encoding class that ensures that the model can predict the product
# event if new feature values appear in production
class PandasLabelEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.label_dict = defaultdict(list)

    def fit(self, X):
        X = X.astype('category')
        cols = X.columns
        values = list(map(lambda col: X[col].cat.categories, cols))
        self.label_dict = dict(zip(cols, values))
        return self

    def transform(self, X):
        # check missing columns
        missing_col = set(X.columns) - set(self.label_dict.keys())
        if missing_col:
            raise ValueError(
                f'the column named {missing_col} is not in the label dictionary. Check your fitting data.')
        return X.apply(lambda x: x.astype('category').cat.set_categories(self.label_dict[x.name]).cat.codes.astype(
            'category').cat.set_categories(np.arange(len(self.label_dict[x.name]))))

    def inverse_transform(self, X):
        return X.apply(lambda x: pd.Categorical.from_codes(codes=x.values,
                                                           categories=self.label_dict[x.name]))


# keeping the features that together gave the best accuracy across models tested through test/train splits
FEATURES = ['lens_type',
            'f_stop',
            # 'canon',
            'IS',
            'focal_range',
            'L_series',
            # 'Macro',
            # 'motor',
            'version',
            'zoom',
            'zoom_r',
            'zoom_l',
            'fixed_range',
            # 'f_stop_ranged',
            # 'f_stop_ranged_l',
            # 'f_stop_ranged_r',
            # 'f_stop_fixed'
            ]


def main():
    labels_df = pd.read_excel(links.LISTINGS_WITH_LABELS, sheet_name="to_label")

    df_train = labels_df[labels_df['target'].notna()]
    X_train = df_train[FEATURES]
    y_train = df_train['target']

    enc = PandasLabelEncoder()
    for feat in X_train.columns:
        X_train.loc[:, feat] = X_train[feat].fillna("NONE").astype(str).values
    X_train_enc = enc.fit_transform(X_train)

    # Gaussian Naive Bayes gave the best accuracy among the models tested
    model = GaussianNB()
    model.fit(X_train_enc, y_train)

    filename = links.MODEL_PICKLE
    pickle.dump(model, open(filename, 'wb'))

    filename = links.ENCODING_PICKLE
    pickle.dump(enc, open(filename, 'wb'))


if __name__ == "__main__":
    main()
