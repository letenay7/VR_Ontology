import re
import pandas as pd
import openpyxl as xl
from rdflib import *
from datetime import datetime

class Headset:
    def __init__(self, name: str, release_date: str, tracking: str,
                 resolution: str, display_type: str, aspect_ratio: str,
                 field_of_view: str, refresh_rate: str):
        self.name = name
        self.release_date = release_date
        self.tracking = tracking
        self.resolution = resolution
        self.display_type = display_type
        self.aspect_ratio = aspect_ratio
        self.field_of_view = field_of_view
        self.refresh_rate = refresh_rate


def parse_headset_names(filename):
    excel_data = pd.ExcelFile(filename)
    sheet1_data = excel_data.parse('Table 2')

    # Ensure columns exist before accessing them
    def safe_column(column_name):
        return sheet1_data[column_name][1:].tolist() if column_name in sheet1_data else []

    vr_headset_names = cleanup_list(safe_column('Column1'))
    release_date = cleanup_list(safe_column('Column2'))
    tracking = cleanup_list(safe_column('Column3'))
    display_type = cleanup_list(safe_column('Column4'))
    resolution = cleanup_list(safe_column('Column6'))
    aspect_ratio = cleanup_list(safe_column('Column9'))
    refresh_rate = cleanup_list(safe_column('Column10'))
    field_of_view = cleanup_list(safe_column('Column11'))

    max_length = len(vr_headset_names)


    headsets = []
    for i in range(max_length):
        has_tracking = tracking[i].strip().lower()
        hmd = Headset(
            name=vr_headset_names[i],
            release_date=convert_to_xsd_date(release_date[i]),
            tracking=has_tracking,
            display_type=display_type[i],
            aspect_ratio=aspect_ratio[i],
            resolution=resolution[i],
            field_of_view=field_of_view[i],
            refresh_rate=refresh_rate[i])
        get_turtle_syntax(hmd)


def convert_to_xsd_date(date_str):

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return Literal(date_obj.isoformat() + "Z", datatype=XSD.dateTime)
    except ValueError:
        return Literal("2000-01-01T00:00:00Z", datatype=XSD.dateTime)  # Default fallback

def convert_to_xsd_bool(value):
    return Literal(bool(value), datatype=XSD.boolean)

def cleanup_list(items):
    pattern = re.compile(r'\[[0-9]*]')  # Remove citation-like text [1]

    clean_list = []
    for item in items:
        if pd.isna(item) or str(item).strip().lower() == "nan":
            clean_list.append("Unknown")
        else:
            cleaned = str(item).replace("\n", " ").strip()  # Replace newlines with spaces
            cleaned = re.sub(pattern, '', cleaned)  # Remove citation-like text
            clean_list.append(cleaned)

    return clean_list

def write_headsets(filename):
    names = parse_headset_names(filename)



def get_turtle_syntax(headset):
    iri = '###  http://www.semanticweb.org/marti/ontologies/2025/virtualreality#'
    type = 'rdf:type owl:NamedIndividual ,'
    name = headset.name
    if ' ' in name:
        name = name.replace(' ', '')
        individual = (f'{iri}{name}\n:{name} {type}\n\t\t\t\t:HeadMountedDisplays ;\n'
                      f'\t\t\t\t:connectedTo'
                      f'\t\t\t\t:Name \"{name}\" ;\n'
                      f'\t\t\t\t:DisplayType \"{headset.display_type}\" ;\n'
                      f'\t\t\t\t:AspectRatio \"{headset.aspect_ratio}\" ;\n'
                      f'\t\t\t\t:FieldOfView \"{headset.field_of_view}\" ;\n'
                      f'\t\t\t\t:RefreshRate \"{headset.refresh_rate}\" ;\n'
                      f'\t\t\t\t:ReleaseDate \"{headset.release_date}\" ;\n'
                      f'\t\t\t\t:Tracking \"{headset.tracking}\" ;\n'
                      f'\t\t\t\t:Resolution \"{headset.resolution}\" .\n')
        print(individual)


def parse_ar_handhelds(filename):
    data = pd.read_csv(filename, usecols=['Manufacturer', 'Model Name'])
    manufacturers = data['Manufacturer'].tolist()
    models = data['Model Name'].tolist()
    pattern = r"[ ()]"
    handhelds = []
    for i in range(len(models)):
        try:
            models[i] = re.sub(pattern, '', models[i]).replace('+', 'plus')
            manufacturers[i] = re.sub(pattern, '', manufacturers[i]).replace('+', 'plus')
            handhelds.append(manufacturers[i] + models[i])
        except TypeError:
            pass
    get_turtle_syntax('HandheldDisplays .')


def parse_controllers(filename):
    data = pd.read_csv(filename, usecols=['Company', 'Device', 'Type'])
    companies = data['Company'].tolist()
    devices = data['Device'].tolist()
    types = data['Type'].tolist()
    controllers = []
    pattern = r"[ ()]"
    for i in range(len(companies)):
        if types[i] == 'Controller':
            companies[i] = re.sub(pattern, '', companies[i]).replace('+', 'plus')
            devices[i] = re.sub(pattern, '', devices[i]).replace('+', 'plus')
            controllers.append(companies[i] + devices[i])
    get_turtle_syntax('Controllers .')


if __name__ == '__main__':
    # graph = Graph()
    # graph.parse('VR_Ontology_Letenay.ttl', format='turtle')
    # print(len(graph))
    write_headsets('headsets.xlsx')
    # parse_ar_handhelds('arcore_devicelist.csv')
    #parse_controllers('VR_Controllers_Table.csv')

