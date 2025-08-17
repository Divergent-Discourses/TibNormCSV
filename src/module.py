import glob
import os
import pandas as pd
import re

def load_tables(config):
    """
    Load normalisation tables from TSV files.
    Tables are stored in a dictionary where keys are filenames and values are pandas DataFrames.
    """
    tables = {}
    pattern = os.path.join(config['paths']['table_path'], '*.tsv')
    flag = int(config['parameters']['flag'])
    files = [file for file in glob.glob(pattern, recursive=True) if os.path.isfile(file)]
    flag_tables = ['abbreviations', 'table3']

    for file in files:
        file_name = os.path.basename(file).split('.')[0]
        df = pd.read_csv(file, sep='\t', escapechar='\\', index_col=None, encoding="utf-8")
        if file_name in flag_tables:
            df['flag'] = df['flag'].apply(pd.to_numeric, errors='coerce').astype('Int64')
            tables[file_name] = df[df['flag'] == flag]  # Apply flag filter
        else:
            tables[file_name] = df

    return tables


def norm_text(text, tables):
    """
    Apply all normalisation steps sequentially to a single text string.
    """
    if not isinstance(text, str):
        return text  # Ensure NaN or other types are not processed

    def apply_replacements(text, table_name):
        """
        Generic function to apply replacements using a given normalisation table.
        """
        if table_name not in tables:
            return text
        table = tables[table_name].set_index('transcription')['normalisation'].to_dict()
        for key, value in table.items():
            text = text.replace(key, value) if table_name != 'table2' else re.sub(key, value, text)
        return text

    # Apply normalisations
    text = apply_replacements(text, 'abbreviations')
    text = apply_replacements(text, 'table1')
    text = apply_replacements(text, 'table2')

    # Handling table3 with exceptions
    if 'table3' in tables:
        table3 = tables['table3']
        text_list = list(text)
        for _, row in table3.iterrows():
            transcription, norm, exc, exc_len, scope = row['transcription'], row['normalisation'], row['exception'], row['exc_len'], row['scope']
            exception = re.compile(exc)

            for i in range(len(text_list)):
                pos_end = i + len(transcription)
                start, end = max(0, i - exc_len), min(len(text_list) - 1, pos_end + exc_len)
                str_range = ''.join(text_list[start:i]) if scope == 'left' else (
                    ''.join(text_list[i+1:end]) if scope == 'right' else ''.join(text_list[start:end])
                )
                if not exception.search(str_range):
                    if len(transcription) > 1 and text_list[i:pos_end] == list(transcription):
                        text_list[i:pos_end] = [norm] + [''] * (pos_end - i - 1)
                    elif text_list[i] == transcription:
                        text_list[i] = norm
        text = ''.join(text_list)

    return text


def process_csv(input_csv, output_csv, tables):
    """
    Load a CSV file, normalise the text in the 'paragraph' column, and save a new CSV.
    """
    df = pd.read_csv(input_csv, encoding='utf-8')

    if 'paragraph' not in df.columns:
        print(f"File {input_csv} does not contain a 'paragraph' column. Skipping.")
        return

    # Check if 'normalised_paragraph' already exists
    if 'normalised_paragraph' in df.columns:
        print(f"File {input_csv} already has 'normalised_paragraph'. Skipping.")
        return

    df.insert(df.columns.get_loc('paragraph') + 1, 'normalised_paragraph', df['paragraph'].apply(lambda text: norm_text(text, tables)))

    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"Processed CSV saved as: {output_csv}")
