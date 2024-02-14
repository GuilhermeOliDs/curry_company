# Bibliotecas
import pandas as pd
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )


# ---------------------------------------------------------------------------
# Funções
# ---------------------------------------------------------------------------

def mean_time_on_traffic( df1 ):
            
    df_aux = df1.loc[:, ['City', 'Road_traffic_density','Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)' : ['mean', 'std']})

    df_aux.columns = ['mean_time', 'std_time']

    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='mean_time', color='std_time', color_continuous_scale='RdBu', 
                                                                                         color_continuous_midpoint=np.average(df_aux['std_time']))
    fig.update_layout(width=400)
            
    return fig


def mean_std_time_graph( df1 ):
    df_aux = round(df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']}),2 )

    # RENOMEEI AS COLUNAS DE df_aux
    df_aux.columns = ['mean_time', 'std_time']

    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['mean_time'], error_y=dict( type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    fig.update_layout(width=350)
                
    return fig

def mean_std_time_delivery(df1, festival, op):
    '''
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
    Input:
        - df: Dataframe com os dados necessários para o cálculo
        - op: Tipo de operação que precisa ser calculada
        'mean_time': Calcula o tempo médio
        'std_time': Calcula o desvio padrão do tempo.
                                
    Output:
        - df: Dataframe com 2 colunas e 1 linha.
    '''
                
    df_aux = df1.loc[:, ['Festival','Time_taken(min)']].groupby(['Festival']).agg({'Time_taken(min)' : ['mean', 'std']})

    df_aux.columns = ['mean_time', 'std_time']

    df_aux = df_aux.reset_index()

    df_aux = round(df_aux.loc[df_aux['Festival'] == 'Yes', op], 2)
                
    return df_aux


def distance( df1, fig ):
    if fig == False:
        colunas = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

        df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)

        mean_distance = round(df1['distance'].mean(), 2)
        
        return mean_distance
    
    else:
        colunas = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

        df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)

        mean_distance = round(df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index(), 2)
        fig = go.Figure( data=[go.Pie( labels=mean_distance['City'], values=mean_distance['distance'], pull=[0, 0.1, 0])])
        fig.update_layout(width=350)
               
        return fig

def clean_code( df1 ):
    ''' Esta funcao tem a responsabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas 
        5. Limpeza da coluna de tempo( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe
    '''
    
    # 1. convertendo a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )


    # 2. convertendo a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )


    # 3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')



    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )

    # peguei informacoes diferentes de strings
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')

    # puxei loc para selecionar o filtro e aplicar as colunas
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # removi os valores nulos com o dropna e selecionei a coluna com o comando subset
    df1 = df1.dropna(subset=['multiple_deliveries'])

    # logo em seguida, transformei a coluna em int utilizando o comando astype
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )



    # 5. removendo os espacos dentro de strings/texto/object

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()


    # 6. Limpando a coluna de time taken

    # O comando .apply() permite que apliquemos um outro comando linha a linha
    # O comando lambda x: x.  permite que usamos uma função para cada linha, que é representado pelo x.
    # O comando split('')[1] faz a separação do (item que quero remover) e do número o valor dentro de colchete 
    # permite escolher qual item quero, neste caso como foi separado em dois itens, posso escolher entre 0 e 1'''

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] ) 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

# ------------------------------------
# Import DataSet
# ------------------------------------

df = pd.read_csv('dataset/train.csv')

# ------------------------------------
# Cleaning Code
# ------------------------------------
df1 = clean_code( df )

# ---------------------------------------------------VISÃO_DOS_RESTAURANTES-----------------------------------------------------------------------------------------------



# ========================================================================================================================================================================
# BARRA LATERAL
# ========================================================================================================================================================================

st.header('Marktplace - Visão Restaurantes')


# image_path = 'logo1.png'
image = Image.open( 'logo1.png' )
st.sidebar.image( image, width=200 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?', 
    value=datetime.datetime(2022, 4, 13), 
    min_value=datetime.datetime(2022, 2, 11), 
    max_value=datetime.datetime(2022, 4, 6), 
    format='DD-MM-YYYY' )



st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown('''---''')

st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ========================================================================================================================================================================
# LAYOUT NO Stremlit
# ========================================================================================================================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.markdown('''___''')
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            entreg_unicos = len( df1.loc[:, 'Delivery_person_ID'].unique() )
            col1.metric('Entregadores', entreg_unicos)
            
# ========================================================================================================================================================================

                        
        with col2:
            mean_distance = distance( df1, fig=False )
            col2.metric( 'A distância média', mean_distance )
            
            
# ========================================================================================================================================================================
            
            
        with col3:
            df_aux = mean_std_time_delivery( df1, 'Yes', 'mean_time' )
            col3.metric( 'Tempo Médio', df_aux )         
            
# ========================================================================================================================================================================
            
            
        with col4:
            df_aux = mean_std_time_delivery( df1, 'Yes', 'std_time' )
            col4.metric( 'STD Entrega', df_aux )
            
            
# ========================================================================================================================================================================
            
            
        with col5:
            df_aux = mean_std_time_delivery( df1, 'No', 'mean_time' )
            col5.metric( 'Tempo médio', df_aux )
           
            
# ========================================================================================================================================================================
            
            
        with col6:
            df_aux = mean_std_time_delivery( df1, 'No', 'std_time' )
            col6.metric( 'STD Entrega', df_aux )
            
# ========================================================================================================================================================================
            
        
    with st.container():
        st.markdown('''___''')
        col1, col2 = st.columns([3, 3]) #Dessa forma consigo mover para esquerda e direita a coluna
        
        with col1:            
            fig = mean_std_time_graph( df1 )
            st.plotly_chart( fig )
            
# ========================================================================================================================================================================
            
            
        with col2:
            st.markdown('''___''')
            df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)' : ['mean', 'std']})

            df_aux.columns = ['mean_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
            
# ========================================================================================================================================================================
            
                
    with st.container():
        st.markdown('''___''')
        st.title('Distribuição do Tempo')
    
        col1, col2 = st.columns(2)
        with col1:            
            fig = distance( df1, fig=True )
            st.plotly_chart(fig)
                
# ========================================================================================================================================================================

        
        with col2:
            fig= mean_time_on_traffic( df1 ) 
            st.plotly_chart( fig )

    
        
    