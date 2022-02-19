import pandas as pd
import links


def main():

    listings_with_features_df = pd.read_excel(links.LISTINGS_WITH_FEATURES, sheet_name='source')

    concat_columns = ['lens_type',
                      'f_stop',
                      'focal_range',
                      'L_series',
                      'Macro',
                      'motor',
                      'version']
    to_label_df = listings_with_features_df.fillna("")
    to_label_df['combined'] = to_label_df[concat_columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

    to_label_df = to_label_df[['file_url',
                               'page_url',
                               'product_title',
                               'end_date',
                               'end_status',
                               'price',
                               'product_quality',
                               'header_description',
                               'body_description',
                               'url_num',
                               'lens_type',
                               'f_stop',
                               'canon',
                               'IS',
                               'focal_range',
                               'L_series',
                               'Macro',
                               'motor',
                               'version',
                               'zoom',
                               'zoom_r',
                               'zoom_l',
                               'fixed_range',
                               'f_stop_ranged',
                               'f_stop_ranged_l',
                               'f_stop_ranged_r',
                               'f_stop_fixed',
                               'combined',
                               'title_upper']]
    labels_df = pd.read_excel(links.LISTINGS_WITH_LABELS, sheet_name="to_label")

    to_label_df_merge = pd.merge(to_label_df,
                                 labels_df[['url_num', 'target']],
                                 how='left',
                                 on='url_num').sort_values('target', ascending=False)

    to_label_df_merge = to_label_df_merge.drop_duplicates(subset=['url_num'])

    print(f"old label df : {labels_df.shape}")
    print(f"new to_label df : {to_label_df_merge.drop_duplicates(subset=['url_num']).shape}")
    print(f"of which labelled values : {to_label_df_merge.query('~target.isna()').shape[0]}")
    print(f"to be newly labelled: {to_label_df_merge.query('target.isna()').shape[0]}")

    proceed = input("Proceed? y/n: ")
    if proceed == "y":
        print("overwrote listings_with_labels")
        with pd.ExcelWriter(links.LISTINGS_WITH_LABELS) as writer:
            to_label_df_merge.to_excel(writer, index=False, sheet_name='to_label')
    else:
        print("aborted")


if __name__ == "__main__":
    main()
