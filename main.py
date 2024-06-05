import logging
import os
from gmail import process_gmail_email
from outlook import process_outlook_email
import pandas as pd

CORRECT = 'Correct'
INCORRECT = 'Incorrect'


def process_row(row, result_excel_file_path, driver, log: logging):
    result_g = process_gmail_email(driver, row['EMAIL'], log=log)
    row["GMAIL RESULT"] = result_g
    result_o = process_outlook_email(driver, row['EMAIL'], log=log)
    row["OUTLOOK RESULT"] = result_o
    validation_score = 0
    if result_g == CORRECT and result_o == CORRECT:
        validation_score = 100
    elif result_g == CORRECT or result_o == CORRECT:
        validation_score = 50

    row["VALIDATION SCORE"] = validation_score

    df = pd.DataFrame(row).T
    if os.path.exists(result_excel_file_path):
        existing_df = pd.read_excel(
            result_excel_file_path, names=["EMAIL", "GMAIL RESULT", "OUTLOOK RESULT", "VALIDATION SCORE"], engine="openpyxl"
        )
        existing_df = pd.concat([existing_df, df], ignore_index=True)
        df = existing_df
    else:
        with open(result_excel_file_path, "w"):
            pass
    return df

