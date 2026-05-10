from pathlib import Path
import pandas as pd
from functions import (
    normalize_company,
    normalize_address,
    match_company,
    score_match,
    build_full_address,
)

incoming_folder = Path("incoming")
output_folder = Path("output")
output_folder.mkdir(exist_ok=True)
files = list(incoming_folder.glob("*.xlsx"))

for file in files:
    print(f"Processing {file.name}")

    # Load files
    # TODO: make xlsx files more general to accept multiple files
    known_df = pd.read_excel("known/known_companies.xlsx")
    incoming_df = pd.read_excel("incoming/file.xlsx")

    # Rename column names
    known_df = known_df.rename(
        columns={
            "DBA/ENTITY": "company",
            "ADDRESS": "address",
            "CITY": "city",
            "STATE": "state",
            "ZIP": "zip",
        }
    )

    known_df = known_df.rename(
        columns={
            "Consignor Name": "company",
            "Consignor Address": "address",
            "City": "city",
            "State": "state",
            "Zip": "zip",
        }
    )

    # Row tracking
    known_df["known_row"] = known_df.index + 3
    incoming_df["incoming_row"] = incoming_df.index + 5

    # Normalize
    known_df["company_norm"] = known_df["company"].apply(normalize_company)
    incoming_df["company_norm"] = incoming_df["company"].apply(normalize_company)

    known_df["address_norm"] = known_df.apply(
        lambda r: normalize_address(build_full_address(r)), axis=1
    )
    incoming_df["address_norm"] = incoming_df.apply(
        lambda r: normalize_address(build_full_address(r)), axis=1
    )

    known_names = known_df["company_norm"].tolist()

    results = []
    for _, row in incoming_df.iterrows():
        match = match_company(row["company_norm"], known_names)

        if match is None:
            results.append(
                {
                    "Incoming Row": row["incoming_row"],
                    "Incoming Company": row["Company"],
                    "Matched Company": None,
                    "Status": "COMPANY NOT FOUND",
                }
            )

            continue

        best_match, company_score, index = match

        known_row = known_df.iloc[index]

        address_score = score_match(row["address_norm"], known_row["address_norm"])

        # Determine status
        if company_score < 85:
            status = "LOW CONFIDENCE MATCH"
        elif address_score < 80:
            status = "ADDRESS MISMATCH"
        else:
            status = "OK"

    # Export results
    results_df = pd.DataFrame(results)

    output_file = output_folder / f"validated_{file.stem}.xlsx"

    results_df.to_excel(output_file, index=False)

print("Validation complete. Output save to 'output/validation_results.xlsx'")
