# loads unique listings, filters out out of scope listings,
# cleans up the title field, transforms some fields, and saves the cleaned df to a csv

import pandas as pd
import links


def main():
    listings_unique_df = pd.read_csv(links.LISTINGS_UNIQUE)

    # Keywords you wouldn't find in a CANON EF lens listing title
    EXCLUDED_PATTERNS = ['CUP', 'MODE', 'KOFFER', 'CONVERTER', 'EXTENDER', 'KIT', 'HALTERUNG', 'EOS',
                         'BAGUE', 'TAMRON', 'NIKON', 'TOKINA', 'ARTISAN', 'SIGMA', 'SONYSPIEGELLOS',
                         'MODUS', 'KAFFEETASSE', 'T\\d', 'FD', 'BUNDLE', 'LAOWA', 'METABONES',
                         'SONYMIRRORLESS', 'HOOD', 'GEGENLICHTBLENDE', 'KENKO', 'GEHÄUSE', 'FILTER',
                         'ANALOG', 'MOUNT', '\\+', 'KAMERA', 'ET-', 'LH-', '\\sM\\d\\s', 'AUGENMUSCHEL',
                         '1X', 'SONNENBLENDE', 'TELEKONVERTER', 'CAMERA', 'MANUAL', 'ADAPTER', 'SET',
                         'ROKINON', 'EW', 'HAUBE', 'CAP', 'VISOR', 'YONGNUO', 'VERLÄNGERUNG', 'WALIMEX',
                         'RING', 'ZEISS', 'SAMYANG', 'EYECUP', 'SCREEN', 'OBJEKTIVDECKEL', 'CASE',
                         'MEIKE', 'LAUWA', 'STATIVSCHELLE', 'LOWEPRO', 'LENSBABY']

    listings_unique_df['title_upper'] = listings_unique_df.apply(lambda x: x['product_title'].upper(), axis=1)

    listings_unique_df = listings_unique_df[(~listings_unique_df["title_upper"]
                                             .str.contains('|'.join(EXCLUDED_PATTERNS), regex=True))]
    listings_unique_df = listings_unique_df[(listings_unique_df["title_upper"]
                                             .str.contains('\d',regex=True))]
    listings_unique_df = listings_unique_df[(listings_unique_df["title_upper"]
                                             .str.contains('CANON',regex=True))]
    listings_unique_df = listings_unique_df[(~listings_unique_df["product_quality"]
                                             .str.contains('fectueux',regex=True))]


    dic_reg = {
        r"(F)\s*(/)\s*": r"\1",                      # F / 1.2 -> F1.2
        r",": r".",                                  # , -> .
        r"\s*-\s*": "-",                             # " - " -> "-"
        r"\s*:\s*": ":",                             # " : " -> ":"
        r"(\d\.)\s*(\d)":r"\1\2",                    # 2. 2 -> 2.2
        r"(\d)\s+(MM)": r"\1\2",                     # 2 MM -> 2MM
        r"(\d?\d\d)(\s)": r"\1MM ",                  # "120 " -> "120MM" (some titles omit MM)
        "(EF)([SM])":r"\1-\2",                       # EFS -> EF-S
        r"(\d)(L)": r"\1 \2",                        # 8L -> 8 L
        r"(EF)(-[SM])?(\d)": r"\1\2 \3",             # EF2 -> EF 2
        "ULTRASONIC": "USM",                         # ULTRASONIC -> USM
        r"US\s": "USM",                              # "US " -> "USM"
        "LL": "II",                                  # LL -> II
        r"(\d)(\s?MM\s?)(-\s?\d*\s?MM)": r"\1\3",    # 8 MM - 9MM -> 8-9MM
        "--": "-",                                   # -- -> -
        r"(\s)(1:)(\d)": r"\1\3"                     # 1:2.8 -> 2.8
    }
    listings_unique_df.loc[:, "title_upper"] = listings_unique_df.loc[:, "title_upper"].replace(dic_reg, regex=True)


    # translate & shorten the end status field
    end_status_dic = {
        "L'article a été vendu." : "sold",
        "L'article n'a pas été vendu" : "not sold",
        r"^\d+ article sur \d+ a été vendu" : "partly sold",
        "Cet article a été supprimé ou n'est plus disponible" : "deleted",
        "Live" : "live"
    }
    listings_unique_df['end_status'] = listings_unique_df['end_status'].replace(end_status_dic, regex = True)


    # get the unique url code (sometimes the url changes due to a title name update but the url code stays the same)
    # this code allows us to track unique listings and avoid double counting
    listings_unique_df['url_num'] = listings_unique_df['file_url'].str.extract(r"-(\d*)$")[0]

    # the columns below combined are unique to each listing unlike the url_name
    # we use them to identify duplicates
    listings_unique_df['duplicates'] = listings_unique_df.end_date + listings_unique_df.end_status + \
                                       listings_unique_df.price + listings_unique_df.url_num
    duplicates = listings_unique_df.groupby(['duplicates'], as_index=False).size()
    duplicates_list = list(duplicates.loc[duplicates['size'] > 1]['duplicates'])
    listings_unique_df = listings_unique_df.drop(columns=['duplicates'], axis=1)

    # need to remove the ' in 1'000 to get 1000 and allow pandas to recognise the number
    listings_unique_df['price'] = listings_unique_df['price'].replace({r"'": ''}, regex=True).astype(float)

    # converting to int to later merge records
    listings_unique_df['url_num'] = listings_unique_df['url_num'].astype(int)

    listings_unique_df.to_csv(links.LISTINGS_CLEANED, index=False)


if __name__ == "__main__":
    main()




