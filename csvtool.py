#!/usr/local/bin/python
#
# process CSVs for schools DB
#

import pandas as pd
import sys, argparse, csv

from transforms import drop, select, pretty_cols, rename_cols
from procedures.registry import do_procedures
from error import eprint

def get_args():
    parser = argparse.ArgumentParser(description='CSV toolkit')
    parser.add_argument('-s','--skiprows', help='Number of rows to skip',
                        type=int, required=False)
    parser.add_argument('-t','--transpose', action='store_true',
                        help='Transpose table', required=False)
    parser.add_argument('-d','--drop', action='append', type=str,
                        help='Drop (exclude) a column', required=False)
    parser.add_argument('-a','--add', action='append', type=str,
                        help='Add (include) a column (supercedes drop)', required=False)
    parser.add_argument('-p','--pretty', action='store_true',
                        help='Prettify column names', required=False)
    parser.add_argument('-j','--json', action='store_true', required=False,
                        default=False)
    parser.add_argument('-i','--input', action='store', type=str,
                        help='File to process', required=False)
    parser.add_argument('-c','--colnames', action='store',type=str,
                        help='set columns: --colnames=[COL1,COL2,COL3,...]')
    parser.add_argument('-r','--rows', action='store', type=int,
                        help='print N rows', required=False)
    parser.add_argument('-l','--load', action='append', type=str,
                        help='load registered procedure', required=False)
    
    return vars(parser.parse_args())

def get_df(args):

    fname = sys.stdin

    if args["input"] != None:
        fname = args["input"]
    
    try:
        df = pd.read_csv(fname, skiprows=args["skiprows"])
        return df
    except Exception, e:
        eprint("Error loading CSV: " + str(e))
        exit(1)

def main():
    a = get_args()
    df = get_df(a)

    # add or drop columns (add takes precedent)
    if a["add"] is None:
        df = drop( df, a["drop"] )
    else:
        df = select(df, a["add"] )


    # prettify column names
    if a["pretty"] is True:
        df = pretty_cols( df )

    # rename columns
    df = rename_cols( df, a["colnames"] )

    # run custom routines
    if a["load"] is not None:
        df = do_procedures( df, a["load"] )

    # truncate output
    if a["rows"] is not None:
        df = df.head(a["rows"])

    # output json or csv
    if a["json"] is True:
        print df.to_json()
    else:
        print df.to_csv(index=False,encoding="utf-8",
                           quoting=csv.QUOTE_NONNUMERIC)

main()
