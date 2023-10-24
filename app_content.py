import datetime

# Modified html_text to use markdown
markdown_text = """
## DDI-CDI Subset

This profile utilizes 20 classes from the DDI-CDI model and 2 classes from the SKOS model:

| DDI-CDI Model                  | SKOS Model          |
|--------------------------------|---------------------|
| DataStore                      | skos:ConceptScheme  |
| PhysicalDataset                | skos:Concept        |
| PhysicalRecordSegment          |                     |
| PhysicalSegmentLayout          |                     |
| ValueMapping                   |                     |
| ValueMappingPosition           |                     |
| DataPoint                      |                     |
| DataPointPosition              |                     |
| InstanceValue                  |                     |
| LogicalRecord                  |                     |
| WideDataSet                    |                     |
| WideDataStructure              |                     |
| IdentifierComponent            |                     |
| MeasureComponent               |                     |
| PrimaryKey                     |                     |
| PrimaryKeyComponent            |                     |
| InstanceVariable               |                     |
| SubstantiveConceptualDomain    |                     |
| SentinelConceptualDomain       |                     |
| ValueAndConceptDescription     |                     |
"""

app_title = 'DDI-CDI Converter: Wide Table Generation for STATA & SPSS'
app_description = ''

colors = {'background': '#111111', 'text': '#7FDBFF'}

style_dict = {
    'backgroundColor': colors['background'],
    'textAlign': 'center',
    'color': 'white',
    'fontSize': 14
}

header_dict = {
    'backgroundColor': colors['background'],
    'textAlign': 'center',
    'color': colors['text'],
    'fontSize': 14
}


table_style = {'overflowX': 'auto', 'overflowY': 'auto', 'maxHeight': '350px',
               'maxWidth': 'auto', 'marginTop': '10px'}