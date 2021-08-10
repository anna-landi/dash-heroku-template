import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                  encoding = 'cp1252', na_values = ['IAP', 'IAP,DK,NA,uncodeable', 'NOT SURE',
                                                    'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]

gss_clean = gss_clean.rename({'wtss':'weight',
                              'educ':'education',
                              'coninc':'income',
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige',
                              'papres10':'father_job_prestige',
                              'sei10':'socioeconomic_index',
                              'fechld':'relationship',
                              'fefam':'male_breadwinner',
                              'fehire':'hire_women',
                              'fejobaff':'preference_hire_women',
                              'fepol':'men_bettersuited',
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'}, axis = 1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
The Gender Wage Gap:

the following article from the Center for American Progress (https://www.americanprogress.org/issues/women/reports/2020/03/24/482141/quick-facts-gender-wage-gap/) discusses what exactly the gender wage gap is, what drives it, and how it impacts women and their families.

the articles states that "the gender wage gap refers to the difference in earnings between women and men".

there are many factors that cause the gender wage gap to persist and these include:
- differences in industries or jobs worked
- differences in years of experience
- differences in hours worked
- discrimination

the article concludes by saying that we must address this issue through policy reform and shifts in cultural attitudes

The General Social Survey:

the GSS "is a nationally representative survey of adults in the United States conducted since 1972".

the goal of the survey is to "monitor and explain trends in opinions, attitudes and behaviors".

the survey asks respondents for demographic information and about certain behaviors and attitudes.

according to the official website, the GSS "is the single best source for sociological and attitudinal trend data covering the United States".

(http://www.gss.norc.org/About-The-GSS)
'''

my_table1 = gss_clean.groupby('sex').agg({'income':'mean',
                                          'job_prestige':'mean',
                                          'socioeconomic_index':'mean',
                                          'education':'mean'}).round(2).reset_index()
my_table1 = my_table1.rename({'sex':'Gender',
                              'income':'Income',
                              'job_prestige':'Occupational Prestige',
                              'socioeconomic_index':'Socioeconomic Index',
                              'education':'Years of Education'}, axis = 1)
my_table1

table = ff.create_table(my_table1)
table.show()

my_table2 = gss_clean.groupby(['sex', 'male_breadwinner'], sort = False).size().reset_index()
my_table2 = my_table2.rename({0:'count'}, axis = 1)
my_table2

fig_bar = px.bar(my_table2, x = 'male_breadwinner', y = 'count', color = 'sex', barmode = 'group',
                 labels = {'male_breadwinner':'Level of Agreement', 'count':'Number of People'})
fig_bar.show()

gss_scatter = gss_clean[~gss_clean.sex.isnull()]

fig_scatter = px.scatter(gss_scatter, x = 'job_prestige', y = 'income',
                         color = 'sex',
                         trendline = 'ols',
                         height = 600, width = 600,
                         labels = {'job_prestige':'Occupational Prestige',
                                   'income':'Income',
                                   'education':'Years of Education',
                                   'socioeconomic_index':'Socioeconomic Index'},
                         hover_data = ['education', 'socioeconomic_index'])
fig_scatter.show()

fig_boxplot_income = px.box(gss_clean, x = 'income', y = 'sex', color = 'sex',
                            labels = {'income':'Income', 'sex':''})
fig_boxplot_income.update_layout(showlegend = False)
fig_boxplot_income.show()

fig_boxplot_job_prestige = px.box(gss_clean, x = 'job_prestige', y = 'sex', color = 'sex',
                                  labels = {'job_prestige':'Occupational Prestige', 'sex':''})
fig_boxplot_job_prestige.update_layout(showlegend = False)
fig_boxplot_job_prestige.show()

gss_new = gss_clean[['income', 'sex', 'job_prestige']]
gss_new['job_prestige_levels'] = pd.cut(gss_new.job_prestige, bins = [14, 25, 36, 47, 58, 69, 80],
                                        labels = ('15-25', '26-36', '37-47', '48-58', '59-69', '70-80'))
gss_new = gss_new.dropna()
gss_new

fig_boxplot_grid = px.box(gss_new, x = 'income', y = 'sex', color = 'sex', color_discrete_map = {'male':'green', 'female':'purple'},
                          facet_col = 'job_prestige_levels', facet_col_wrap = 2,
                          labels = {'income':'Income', 'sex':'Sex'})
fig_boxplot_grid.show()

x_axis_columns = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
groupby_columns = ['sex', 'region', 'education']
gss_interactive_barplot = gss_clean[x_axis_columns + groupby_columns].dropna()
gss_interactive_barplot

app = JupyterDash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div(
    [
        html.H1("The 2019 GSS: Gender Wage Gap"),
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Table Comparing Variables by Gender"),
        
        dcc.Graph(figure = table),
        
        html.H2("Barplot Comparing Views about Male Breadwinners"),
        
        dcc.Graph(figure = fig_bar),
        
        html.H2("Scatterplot Comparing Job Prestige & Income by Gender"),
        
        dcc.Graph(figure = fig_scatter),
        
        html.Div([
            
            html.H2("Boxplot Showing Income by Gender"),
            
            dcc.Graph(figure = fig_boxplot_income)
        
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Boxplot Showing Job Prestige by Gender"),
            
            dcc.Graph(figure = fig_boxplot_job_prestige)
        
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2("Boxplot Showing Income & Gender by Level of Job Prestige"),
        
        dcc.Graph(figure = fig_boxplot_grid),
        
        html.H2("Interactive Barplot"),
        
        html.Div([
            html.H3("x-axis feature"),
            dcc.Dropdown(id = "x-axis",
                         options = [{"label":i, "value":i} for i in x_axis_columns],
                         value = "male_breadwinner"),
            html.H3("color"),
            dcc.Dropdown(id = "color",
                        options = [{"label":i, "value":i} for i in groupby_columns],
                        value = "sex")], style = {"width":"25%", "float":"left"}),
        html.Div([dcc.Graph(id = "graph", style = {"width":"70%", "display":"inline-block"})])
        
    ]
)

@app.callback(Output(component_id = "graph", component_property = "figure"),
              [Input(component_id = "x-axis", component_property = "value"),
               Input(component_id = "color", component_property = "value")])

def make_figure(x, color):
    return px.bar(
        gss_interactive_barplot,
        x = x,
        color = color,
        barmode = "group",
        height = 700
)

if __name__ == '__main__':
    app.run_server(debug = True)
