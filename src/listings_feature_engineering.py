# Creates features from the cleaned listings title field
import pandas as pd
import links

# The fields created are as follows:
# - CANON
# - EF, EF-S, EF-M
# - FX or  FX-X stop
# - XMM or X-XMM focal range
# - Other indicators (MACRO)
# - USM, STM or None
# - I, II or III or None
# - L series
# - IS
# - Zoom lens or not
# - Prime lens MM
# - Zoom lens MM 1
# - Zoom lens MM 2
# - Multi Focal Range
# - Single Focal range Number
# - Multi Focal range Number 1
# - Multi Focal range Number 2


def return_lens_type(x):
    if "EF-S" in x:
        return "EF-S"
    elif "EF-M" in x:
        return "EF-M"
    elif "EF" in x:
        return "EF"
    else:
        return None


def main():

    listings_cleaned = pd.read_csv(links.LISTINGS_CLEANED)

    listings_cleaned["canon"] = listings_cleaned["title_upper"].str.contains(r"CANON")

    listings_cleaned["lens_type"] = listings_cleaned.loc[:, "title_upper"].apply(lambda x: return_lens_type(x))

    listings_cleaned["f_stop"] = listings_cleaned["title_upper"] \
        .str.extract(r"((F(\d)(\.)?(\d)?(-\d)?(\.)?(\d)?)|([^\:\/](\d\.\d)(-\d)?(\.\d)?)|((\d\.)?(\d\-\d\.\d)))")[0] \
        .replace({r"F": r""}, regex=True).str.strip().replace({r"^(\d)$": r"\1.0", r"^(\d)(\-)": r"\1.0\2"}, regex=True)

    listings_cleaned["IS"] = listings_cleaned["title_upper"].str.contains(r"IS")

    listings_cleaned["focal_range"] = listings_cleaned["title_upper"] \
        .str.extract(r"(\d*?-?\d{2}\d*?M)") \
        .replace({r"M*": r""}, regex=True)

    listings_cleaned["L_series"] = listings_cleaned["title_upper"] \
        .str.extract(r"(\sL\s|\sL$)") \
        .replace({r"L": True}, regex=True) \
        .fillna(False)

    listings_cleaned["Macro"] = listings_cleaned["title_upper"].str.contains("MACRO|MAKRO", regex=True)

    listings_cleaned["motor"] = listings_cleaned["title_upper"].str.extract(r"(USM|STM)")[0]

    listings_cleaned["version"] = listings_cleaned["title_upper"].str.extract(r"(\sI*\s)")[0]

    listings_cleaned["zoom"] = listings_cleaned["title_upper"] \
        .str.extract(r"(\d)(-)(\d+)(MM)")[1] \
        .replace({r"-": 1, None: 0}, regex=True)

    listings_cleaned["zoom_r"] = listings_cleaned["title_upper"].str.extract(r"(\d+)(-)(\d+)(MM)")[2]

    listings_cleaned["zoom_l"] = listings_cleaned["title_upper"].str.extract(r"(\d+)(-)(\d+)(MM)")[0]

    listings_cleaned["fixed_range"] = listings_cleaned["title_upper"].str.extract(r"(\s)(\d+)(MM)")[1]

    listings_cleaned["f_stop_ranged"] = listings_cleaned["f_stop"] \
        .str.extract(r"\d(-)\d")[0] \
        .replace({r"-": 1, None: 0}, regex=True)

    listings_cleaned["f_stop_ranged_l"] = listings_cleaned["f_stop"].str.extract(r"(\d?.?\d?)(-)")[0]

    listings_cleaned["f_stop_ranged_r"] = listings_cleaned["f_stop"].str.extract(r"(-)(\d?.?\d?)")[1]

    listings_cleaned["f_stop_fixed"] = listings_cleaned["f_stop"].str.extract(r"(^\d*?.?\d*?$)")[0]

    with pd.ExcelWriter(links.LISTINGS_WITH_FEATURES) as writer:
        listings_cleaned.to_excel(writer, index=False, sheet_name='source')


if __name__ == "__main__":
    main()
