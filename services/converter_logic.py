# services/converter_logic.py
import csv
import json
import os
import psycopg2
from config import get_db_connection, CSV_FILE_PATH

# --- 1. Custom CSV Parsing and JSON Structure Builder ---
def build_nested_json(headers, row_data):
    """Converts a flat CSV row into a nested JSON object."""
    result = {}
    for header, value in zip(headers, row_data):
        header = header.strip()
        value = value.strip()
        if not value: continue
        path_parts = header.split('.')
        current_level = result
        for key in path_parts[:-1]:
            if key not in current_level or not isinstance(current_level[key], dict):
                current_level[key] = {}
            current_level = current_level[key]
        final_key = path_parts[-1]
        current_level[final_key] = value
    return result

# --- 2. Mapping to Database Schema ---
def map_to_db_schema(user_json):
    """Maps the nested JSON object to the public.users DB schema."""
    db_object = {}
    additional_info = user_json.copy()

    # Mandatory properties mapping
    first_name = additional_info.pop('name', {}).pop('firstName', '')
    last_name = additional_info.pop('name', {}).pop('lastName', '')
    db_object['name'] = f"{first_name} {last_name}".strip()

    age_str = additional_info.pop('age', '0')
    try:
        db_object['age'] = int(age_str)
    except ValueError:
        db_object['age'] = 0 

    # Designated complex property
    db_object['address'] = additional_info.pop('address', {})
    
    # Cleanup and remaining properties
    if 'name' in additional_info and not additional_info['name']: del additional_info['name']

    db_object['additional_info'] = additional_info
    return db_object

# --- 3. Age Distribution Calculation ---
def calculate_age_distribution(ages):
    """Calculates the age distribution percentage."""
    total_count = len(ages)
    if total_count == 0: return {}
    
    # ... (Age counting logic) ...
    count_less_20 = sum(1 for age in ages if age < 20)
    count_20_to_40 = sum(1 for age in ages if 20 <= age <= 40)
    count_40_to_60 = sum(1 for age in ages if 40 < age <= 60)
    count_greater_60 = sum(1 for age in ages if age > 60)

    def to_percent(count):
        return f"{(count / total_count) * 100:.2f}%"

    return {
        "< 20": to_percent(count_less_20),
        "20 to 40": to_percent(count_20_to_40),
        "40 to 60": to_percent(count_40_to_60),
        "> 60": to_percent(count_greater_60),
    }

# --- 4. Main Processing and Database Insertion ---
def process_and_upload_csv(file_path):
    """Reads CSV, processes data, and uploads to PostgreSQL."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at: {file_path}")

    db_records = []
    all_ages = []

    # Read and parse CSV
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            raise Exception("CSV file is empty.")

        for row in reader:
            if not row or not any(row): continue
            if len(row) != len(headers): continue
            try:
                nested_json = build_nested_json(headers, row)
                db_record = map_to_db_schema(nested_json)
                db_records.append(db_record)
                all_ages.append(db_record['age'])
            except Exception as e:
                print(f"Error processing row {row}: {e}")

    # Database Insertion
    if db_records:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO public.users ("name", age, address, additional_info)
        VALUES (%s, %s, %s::jsonb, %s::jsonb);
        """
        insert_data = []
        for record in db_records:
            insert_data.append((
                record['name'],
                record['age'],
                json.dumps(record['address']), 
                json.dumps(record['additional_info'])
            ))

        try:
            cursor.executemany(sql, insert_data)
            conn.commit()
            print(f"✅ Successfully inserted {len(db_records)} records.")
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Database insertion failed: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("No valid records found to upload.")

    return calculate_age_distribution(all_ages)