import pandas as pd
import json
import re

# Load Naukri CSV data
try:
    naukri_df = pd.read_csv('./Data/clean/naukri_selenium_fixed.csv')
    naukri_df['source'] = 'Naukri'
    print("Naukri CSV columns:", naukri_df.columns.tolist())
    print(f"Naukri records: {len(naukri_df)}")
except FileNotFoundError:
    print("Error: 'naukri_selenium_fixed.csv' not found in './Data/clean/'")
    exit(1)

# Load Indeed JSON data (JSONL format)
indeed_data = []
try:
    with open('./Data/clean/indeed_selenium_fixed.json', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    indeed_data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON line: {e}")
                    continue
except FileNotFoundError:
    print("Error: 'indeed_selenium_fixed.json' not found in './Data/clean/'")
    exit(1)

if not indeed_data:
    print("Error: No valid data found in 'indeed_selenium_fixed.json'")
    exit(1)

indeed_df = pd.DataFrame(indeed_data)
indeed_df['source'] = 'Indeed'
print("Indeed JSON columns:", indeed_df.columns.tolist())
print(f"Indeed records: {len(indeed_df)}")

# Standardize column names
column_mapping = {
    'Title': 'title',
    'Company': 'company',
    'Location': 'location',
    'Salary': 'salary',
    'Role': 'role',
    'Skills': 'skills'
}

# Rename columns for consistency
naukri_df = naukri_df.rename(columns={k: v for k, v in column_mapping.items() if k in naukri_df.columns})
indeed_df = indeed_df.rename(columns={k: v for k, v in column_mapping.items() if k in indeed_df.columns})

# Ensure both DataFrames have the same columns
common_columns = ['title', 'company', 'location', 'salary', 'description', 'role', 'skills', 'source']
naukri_df = naukri_df.reindex(columns=common_columns)
indeed_df = indeed_df.reindex(columns=common_columns)

# Merge the DataFrames
merged_df = pd.concat([naukri_df, indeed_df], ignore_index=True)
print(f"Total records after merge: {len(merged_df)}")

# Debug column types
print("Merged DataFrame column types:\n", merged_df.dtypes)

# Clean the data
def clean_salary(salary):
    if pd.isna(salary) or salary == 'Not Disclosed' or not salary:
        return 'Not Disclosed'
    salary = str(salary).lower().replace('₹', '').replace('$', '').replace(',', '').strip()
    if not re.search(r'\d', salary):
        return 'Not Disclosed'
    match = re.match(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', salary)
    if match:
        low, high = match.group(1), match.group(2)
        if 'lac' in salary:
            low = str(float(low) * 100000)
            high = str(float(high) * 100000)
        return f"{low}-{high}"
    match = re.match(r'(\d+\.?\d*)', salary)
    if match:
        return match.group(1)
    return 'Not Disclosed'

def clean_location(location):
    if pd.isna(location):
        return 'Unknown'
    return ' '.join(str(location).split()).title()

def clean_skills(skills):
    if pd.isna(skills) or skills == [] or skills == '[]' or not skills:
        return 'None'
    if isinstance(skills, list):
        return ', '.join([str(skill).strip().title() for skill in skills if skill])
    return str(skills).strip().title()

def clean_description(description):
    if pd.isna(description):
        return 'No description'
    return str(description).strip()

# Apply cleaning functions
merged_df['salary'] = merged_df['salary'].apply(clean_salary)
merged_df['location'] = merged_df['location'].apply(clean_location)
merged_df['title'] = merged_df['title'].astype(str).str.strip().str.title()
merged_df['company'] = merged_df['company'].astype(str).str.strip().str.title()
merged_df['description'] = merged_df['description'].apply(clean_description)
merged_df['role'] = merged_df['role'].astype(str).str.strip().str.title().fillna('Unknown')
# merged_df['skills'] = merged_df['skills'].apply(clean_skills)

# Handle missing values
merged_df.fillna({'salary': 'Not Disclosed', 'location': 'Unknown', 'description': 'No description', 'role': 'Unknown', 'skills': 'None'}, inplace=True)

# Identify and save duplicates
duplicates = merged_df[merged_df.duplicated(subset=['title', 'company', 'location', 'source', 'salary'], keep=False)]
duplicates.to_csv('duplicates.csv', index=False)
print(f"Number of duplicate records (including salary): {len(duplicates)}")
print(f"Naukri duplicates: {len(duplicates[duplicates['source'] == 'Naukri'])}")
print(f"Indeed duplicates: {len(duplicates[duplicates['source'] == 'Indeed'])}")

# Remove duplicates
merged_df = merged_df.drop_duplicates(subset=['title', 'company', 'location', 'source', 'salary'], keep='first')

# Save cleaned data
merged_df.to_csv('cleaned_job_data.csv', index=False)

print(f"Cleaned data saved to 'cleaned_job_data.csv' with {len(merged_df)} records.")