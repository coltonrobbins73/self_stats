from pathlib import Path
from typing import List

from self_stats.munger.input_output import save_to_csv
from self_stats.munger.changepoint_analysis import trim_date
from self_stats.munger.parse_and_process import main as parse_and_process
from self_stats.munger.impute_time_data import main as imputer

def main(directory: str, input_file_name: str, mappings: List[str]) -> None:

    if mappings[0] == 'Text Title':
        data_source = 'search'
    elif mappings[0] == 'Video URL':
        data_source = 'watch'

    cleaned_data = parse_and_process(directory, input_file_name, mappings)

    out_dir = Path(f'{directory}/output')
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {out_dir}\n")
    save_to_csv(cleaned_data, f'{directory}/output/extracted_{data_source}_history.csv', mappings)
    print(f"Search data extraction complete. Results saved to '{directory}/output/extracted_{data_source}_data.csv'.\n")
    
    dash_ready_data = trim_date(cleaned_data, mappings)
    save_to_csv(dash_ready_data, f'{directory}/output/dash_ready_{data_source}_data.csv', mappings)
    print(f"Data processing complete. Results saved to '{directory}/output/dash_ready_{data_source}_data.csv'.\n")

    imputed_data = imputer(dash_ready_data, mappings)
    save_to_csv(imputed_data, f'{directory}/output/imputed_{data_source}_data.csv', mappings)
    print(f"Data processing complete. Results saved to '{directory}/output/imputed_{data_source}_data.csv'.\n")

    