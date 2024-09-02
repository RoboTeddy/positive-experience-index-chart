import csv
import json
from typing import Dict, Union

def get_gdp_lookup() -> Dict[str, float]:
    gdp_data = {}
    
    with open('input/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_3401652/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_3401652.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip the first rows (metadata and blank lines)
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        headers = next(reader)
        for row in reader:
            if row:  # Skip empty rows
                country_code = row[headers.index('Country Code')]
                gdp_2023 = row[headers.index('2023')]
                gdp_2022 = row[headers.index('2022')]
                
                if gdp_2023 and gdp_2023 != '':
                    gdp_data[country_code] = float(gdp_2023)
                elif gdp_2022 and gdp_2022 != '':
                    gdp_data[country_code] = float(gdp_2022)
                else:
                    gdp_data[country_code] = None
    
    return gdp_data

def get_population_lookup() -> Dict[str, int]:
    population_data = {}
    
    with open('input/API_SP.POP.TOTL_DS2_en_csv_v2_3401680/API_SP.POP.TOTL_DS2_en_csv_v2_3401680.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip the first rows (metadata)
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        headers = next(reader)
        for row in reader:
            if row:  # Skip empty rows
                country_code = row[headers.index('Country Code')]
                population_2023 = row[headers.index('2023')]
                population_2022 = row[headers.index('2022')]
                
                
                if population_2023 and population_2023 != '':
                    population_data[country_code] = int(float(population_2023))
                elif population_2022 and population_2022 != '':
                    population_data[country_code] = int(float(population_2022))
                else:
                    population_data[country_code] = None
    
    return population_data

def get_gallup_emotions_data() -> Dict[str, Dict[str, Union[float, None]]]:
    with open('input/gallup-global-emotions-2024.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    emotions_data = {}
    label_map = {f'q{i}': data['qInfo'][f'q{i}']['label'] for i in range(1, 11)}
    
    for country in data['data']:
        emotions_data[country['name']] = {}
        for q_key, label in label_map.items():
            value = country[q_key]['yes']
            emotions_data[country['name']][label] = float(value) if value != '' else None
    
    return emotions_data

def get_region_lookup() -> Dict[str, str]:
    region_lookup = {}
    with open('input/country-continent-codes.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            region_lookup[row['iso3']] = row['continent']
    return region_lookup

def check_for_missing_gdp_entries():
    gdp_data = get_gdp_lookup()
    gallup_emotions_data = get_gallup_emotions_data()
    
    with open('input/gallup_country_codes.json', 'r', encoding='utf-8') as file:
        country_codes = json.load(file)
    
    missing_entries = []
    
    for country in gallup_emotions_data.keys():
        if country in country_codes:
            code = country_codes[country]
            if code not in gdp_data or gdp_data[code] is None:
                missing_entries.append(country)
        else:
            missing_entries.append(f"{country} (No country code found)")
    
    if missing_entries:
        print("Countries in Gallup data without corresponding GDP data:")
        for country in missing_entries:
            print(f"- {country}")
    else:
        print("All Gallup countries have corresponding GDP data.")

    return missing_entries

def write_emotions_gdp_population_csv():
    gdp_data = get_gdp_lookup()
    emotions_data = get_gallup_emotions_data()
    population_data = get_population_lookup()
    region_data = get_region_lookup()
    
    with open('input/gallup_country_codes.json', 'r', encoding='utf-8') as file:
        country_codes = json.load(file)
    
    missing_entries = []
    with open('output/emotions_gdp_population.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Region', 'GDP', 'Population', 'Enjoyment', 'Well-Rested', 'Learned', 'Smiled', 'Respect', 'Positive Experience Index']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for country, emotions in emotions_data.items():
            row = {'Country': country}
            
            # Get GDP, Population, and Region
            code = country_codes[country]
            row['GDP'] = gdp_data.get(code)
            row['Population'] = population_data.get(code)
            row['Region'] = region_data.get(code, 'Unknown')
            if row['GDP'] is None or row['Population'] is None:
                missing_entries.append(country)
            
            # Get emotion data
            positive_emotions = ['Enjoyment', 'Well-Rested', 'Learned', 'Smiled', 'Respect']
            
            for emotion in positive_emotions:
                row[emotion] = emotions[emotion]
            
            # Calculate Positive Experience Index
            row['Positive Experience Index'] = sum(row[emotion] for emotion in positive_emotions if row[emotion] is not None) / len([e for e in positive_emotions if row[e] is not None])
            
            writer.writerow(row)
    
    print("CSV file 'emotions_gdp_population.csv' has been created.")
    
    if missing_entries:
        print("Countries in Gallup data without corresponding GDP or Population data:")
        for country in missing_entries:
            print(f"- {country}")
    else:
        print("All Gallup countries have corresponding GDP and Population data.")

if __name__ == "__main__":
    write_emotions_gdp_population_csv()
