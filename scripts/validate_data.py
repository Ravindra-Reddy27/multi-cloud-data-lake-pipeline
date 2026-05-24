import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.render.renderer import ValidationResultsPageRenderer
from great_expectations.render.view import DefaultJinjaPageView
import os
import json
import sys

def setup_and_validate():
    os.makedirs("great_expectations/expectations", exist_ok=True)
    os.makedirs("great_expectations/uncommitted/data_docs/local_site", exist_ok=True)

    # FIX 1: Added "parse_strings_as_datetimes": True to the timestamp check
    suite_dict = {
        "data_asset_type": None,
        "expectation_suite_name": "clickstream_processed",
        "expectations": [
            {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": "event_id"}},
            {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": "user_id"}},
            {"expectation_type": "expect_column_values_to_be_in_set", "kwargs": {"column": "event_type", "value_set": ["page_view", "product_view", "add_to_cart", "purchase"]}},
            {"expectation_type": "expect_column_values_to_be_of_type", "kwargs": {"column": "user_id", "type_": "int64"}},
            {"expectation_type": "expect_column_values_to_be_between", "kwargs": {"column": "event_timestamp", "min_value": "2000-01-01", "max_value": "2030-12-31", "parse_strings_as_datetimes": True}}
        ],
        "meta": {}
    }

    suite_path = "great_expectations/expectations/clickstream_processed.json"
    with open(suite_path, "w") as f:
        json.dump(suite_dict, f, indent=2)

    print("Validating the processed Parquet dataset...")
    try:
        df = pd.read_parquet("output/processed")
        # FIX 2: Convert the partitioned column from 'category' to standard 'string'
        df['event_type'] = df['event_type'].astype(str)
    except Exception as e:
        print(f"ERROR: Could not read Parquet dataset: {e}")
        sys.exit(1)
    
    dataset = gx.from_pandas(df)
    expectation_suite = ExpectationSuite(**suite_dict)
    validation_result = dataset.validate(expectation_suite=expectation_suite)

    document_model = ValidationResultsPageRenderer().render(validation_result)
    html = DefaultJinjaPageView().render(document_model)

    report_path = "great_expectations/uncommitted/data_docs/local_site/index.html"
    with open(report_path, "w") as f:
        f.write(html)

    # NEW: Terminal Error Reporting
    if not validation_result["success"]:
        print("\n❌ DATA VALIDATION FAILED! Here is the terminal report:")
        for result in validation_result["results"]:
            if not result["success"]:
                exp_type = result["expectation_config"]["expectation_type"]
                col = result["expectation_config"]["kwargs"].get("column", "Unknown")
                print(f"\n- FAILED: {exp_type} on column '{col}'")
                
                # Print sample of bad data if available
                if "partial_unexpected_list" in result["result"]:
                    bad_data = result["result"]["partial_unexpected_list"]
                    print(f"  Unexpected values found: {bad_data[:5]}...")
                
                # Print exact system error if it crashed
                if result.get("exception_info", {}).get("raised_exception"):
                    print(f"  Exception: {result['exception_info']['exception_message']}")
                    
        sys.exit(1)

    print("\n✅ DATA VALIDATION PASSED! Data is clean and ready for AWS.")
    sys.exit(0)

if __name__ == "__main__":
    setup_and_validate()