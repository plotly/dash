import pandas as pd
import datetime

from backend import Dash
from backend.components import *

df = pd.read_csv('/Users/chriddyp/Repos/react-world/'
                 'consumer_complaints_50k.csv',
                 index_col='Date sent to company', parse_dates=True)

dash = Dash('html layouts')

dash.layout = div([
    h2('Consumer Complaints'),

    blockquote([
        ('''
         Each week we send thousands of consumers' complaints about
         financial products and services to companies for response.
         Complaints are listed in the database after the company responds
         or after they\'ve had the complaint for 15 calendar days,
         whichever comes first.
         '''),
        br(),
        ('''
         We publish the consumer\'s description of what happened if the
         consumer opts to share it and after taking steps to remove
         personal information. See our '''),
        a('Scrubbing Standard',
          href="http://files.consumerfinance.gov/a/assets/"
               "201503_cfpb_Narrative-Scrubbing-Standard.pdf",
          target="_blank"),
        (''' for more details.
         We don\'t verify all the facts alleged in these complaints,
         but we take steps to confirm a commercial relationship.
         We may remove complaints if they don\'t meet all of the
         publication criteria. Data is refreshed nightly.'''),
        br(),
        a('More about the Consumer Complaint Database',
          href="http://www.consumerfinance.gov/complaintdatabase/",
          target="_blank")
    ], style={'borderLeft': 'thick lightgrey solid',
              'paddingLeft': '20px', 'fontStyle': 'italic'}),

    hr(),

    h4('Sample Complaint'),
    div(id='sample-complaint', content=[]),

    hr(),

    div(className='row', content=[h5('Complaints by Company')]),

    div(className='row', content=[
        div(className='four columns', content=[
            TextInput(id='company-search', label='filter companies', value=''),
            table(id='company-complaint-table',
                  className='u-full-width')
        ]),
        div(className='eight columns', content=[
            PlotlyGraph(
                id='company-complaint-graph'
            )
        ])
    ]),

    hr(),

    div(className='row', content=[
        h5('Complaints by Company over Time, Product, and State')
    ]),

    div(className='row', content=[
        div(className='three columns', content=[
            div([
                CheckList(
                    id='company-checklist',
                    options=[
                        {'id': option, 'label': option, 'checked': False}
                        for option in list(df.Company.value_counts().index)
                    ]
                )
            ], style={
                'maxHeight': '700px', 'overflowY': 'scroll',
                'borderRight': 'thin lightgrey solid'
            })
        ]),

        div(className='nine columns', content=[
            PlotlyGraph(
                id='complaint-time-series',
                bindHover=True,
                height=300
            ),
            pre('filter complaints by week by hovering over the bars'),
            div([
                div([
                    PlotlyGraph(id='complaint-by-product',
                                height=400, bindHover=True)
                ]),
                div([
                    PlotlyGraph(
                        id='complaint-by-state',
                        height=500
                    )
                ])
            ])

        ])

    ]),

    div(className='row', content=[
        pre(id='display-hover', content=''),
        pre(id='display-click', content='')
    ])

], className='container')
# Initialize checklist
dash.layout['company-checklist'].options[0]['checked'] = True
dash.layout['company-checklist'].options[1]['checked'] = True

# Fill in sample-complaint
for i, dfrow in df.iterrows():
    if not pd.isnull(dfrow['Consumer complaint narrative']):
        break

row = []
for i, (k, v) in enumerate(dfrow.iteritems()):
    if not pd.isnull(v) and k != 'Consumer complaint narrative':
        row.append(
            div(className='three columns', content=[
                b(k.upper()),  # <b> - bold
                p(str(v)),     # <p> - paragraph
            ])
        )

    if i % 4 == 0 and i != 0:
        dash.layout['sample-complaint'].extend([
            div(className='row', content=row),
            hr()
        ])
        row = []

dash.layout['sample-complaint'].append(
    b('Consumer complaint narrative'.upper()))
dash.layout['sample-complaint'].append(
    p(dfrow['Consumer complaint narrative']))

most_common_complaints = df['Company'].value_counts()

# Graphs are described declaritively: every attribute of the graph
# has a configurable key-value pair
# More on this: https://plot.ly/python/reference
dash.layout['company-complaint-graph'].figure = {
    'data': [{
        'x': most_common_complaints.index,
        'y': most_common_complaints,
        'type': 'bar'
    }],
    'layout': {
        'yaxis': {
            'type': 'log',
        },
        'xaxis': {
            'range': [-1, 50],
            'tickangle': 40
        },
        'margin': {'t': 5, 'r': 0, 'l': 40, 'b': 200}
    }
}


def gen_table(rows, header=[]):
    tbl = table([
        thead([
            tr([
                th(str(h)) for h in header
            ])
        ]),
        tbody([
            tr([
                td(str(cell)) for cell in row
            ]) for row in rows
        ])
    ])
    return tbl

sample_table = gen_table(zip(
    list(most_common_complaints.index),
    list(most_common_complaints))[0:7])
dash.layout['company-complaint-table'].content = sample_table.content


@dash.react('company-complaint-graph', ['company-search'])
def update_graph_when_input_changes(company_search_input):
    ''' This function gets called whenever the input
    with the id 'company-search' changes. This function returns
    properties of the PlotlyGraph component with the id 'graph'.
    Dash updates the front-end with these new properties.
    '''
    # company_search_input is a components.TextInput object with the value
    # from the front end
    user_input = company_search_input.value
    if user_input == '':
        updated_complaints = most_common_complaints
    else:
        updated_complaints = most_common_complaints.filter(regex=user_input)

    graph_component = dash.layout['company-complaint-graph']
    figure = graph_component.figure
    figure['data'][0]['x'] = updated_complaints.index
    figure['data'][0]['y'] = updated_complaints
    return {
        'figure': figure
    }


@dash.react('company-complaint-table', ['company-search'])
def update_table_when_input_changes(company_search_input):
    user_input = company_search_input.value
    print 'user_input: ', user_input
    if user_input == '':
        updated_complaints = most_common_complaints
    else:
        updated_complaints = most_common_complaints.filter(regex=user_input)

    return {
        'content': gen_table(zip(
            list(updated_complaints.index),
            list(updated_complaints))[0:12]
        ).content
    }


@dash.react('complaint-time-series', ['company-checklist'])
def graph_complaints(company_checklist):
    traces = []
    for co in company_checklist.options:
        if co['checked']:
            series = df[df.Company == co['id']]['Company']
            series = series.resample('1W', how='count')
            traces.append({
                'x': series.index,
                'y': series,
                'name': co['id'],
                'type': 'bar'
            })
    return {
        'figure': {
            'data': traces,
            'layout': {
                'showlegend': True,
                'margin': {
                    't': 5, 'l': 30, 'r': 10, 'b': 30
                },
                'legend': {'x': 1, 'xanchor': 'right'},
                'annotations': [{
                    'text': 'complaints per week',
                    'x': 0, 'xanchor': 'left', 'xref': 'paper',
                    'y': 0.95, 'yanchor': 'bottom', 'yref': 'paper',
                    'showarrow': False, 'font': {'size': 14},
                    'bgcolor': 'rgba(255, 255, 255, 0.5)'
                }]
            }
        }
    }


def _filter_by_company_and_week(complaint_time_series_hover_data,
                                company_checklist):
    selected_companies = [c['id'] for c in company_checklist.options
                          if c['checked']]
    dfn = df[df['Company'].isin(selected_companies)]
    date_interval_start = date_interval_end = None

    if hasattr(complaint_time_series_hover_data, 'hover'):
        date_interval_end = datetime.datetime.strptime(
            complaint_time_series_hover_data.hover['points'][0]['x'],
            '%Y-%m-%d'
        )

        date_interval_start = date_interval_end - datetime.timedelta(days=7)
        dfn = dfn[(dfn.index > date_interval_start) &
                  (dfn.index < date_interval_end)]

    return dfn, date_interval_start, date_interval_end, selected_companies


def _annotation_title(title):
    return {
        'text': title,
        'x': 0, 'xanchor': 'left', 'xref': 'paper',
        'y': 0.9, 'yanchor': 'bottom', 'yref': 'paper',
        'showarrow': False, 'font': {'size': 14},
        'bgcolor': 'rgba(255, 255, 255, 0.5)', 'align': 'left'
    }


@dash.react('complaint-by-product',
            ['complaint-time-series', 'company-checklist'])
def graph_complaint_by_product(complaint_time_series_hover_data,
                               company_checklist):

    dfn, start, end, selected_companies = _filter_by_company_and_week(
        complaint_time_series_hover_data,
        company_checklist)

    title = 'complaints by product'
    if start and end:
        title += '<br>{} to {}'.format(
            start.date(),
            end.date()
        )

    return {
        'figure': {
            'data': [{
                'x': dfn[dfn['Company'] == co]['Product'].value_counts().index,
                'y': dfn[dfn['Company'] == co]['Product'].value_counts(),
                'type': 'bar',
                'name': co
            } for co in selected_companies],
            'layout': {
                'annotations': [_annotation_title(title)],
                'margin': {'t': 50, 'l': 30, 'r': 10, 'b': 150}
            }
        }
    }


@dash.react(
    'complaint-by-state', [
        'complaint-time-series',    # hover data
        'company-checklist'])
def graph_complaints_by_state(
    complaint_time_series_hover_data,
        company_checklist):

    dfn, start, end, selected_companies = _filter_by_company_and_week(
        complaint_time_series_hover_data,
        company_checklist)

    title = 'complaints made to {}'.format(', '.join(selected_companies))
    if start and end:
        title += '<br>{} to {}'.format(
            start.date(),
            end.date()
        )

    s = dfn.groupby('State')['Company'].count()

    return {
        'figure': {
            'data': [{
                'locations': s.index,
                'locationmode': 'USA-states',
                'z': s,
                'type': 'choropleth',
                'showscale': False
            }],
            'layout': {
                'geo': {'scope': 'usa'},
                'margin': {'t': 10, 'l': 10, 'r': 10, 'b': 10},
                'annotations': [_annotation_title(title)]
            }
        }
    }


if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)
