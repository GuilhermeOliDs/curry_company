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

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

# ---------------------------------------------------------------------------
# Funções
# ---------------------------------------------------------------------------

def country_maps( df1 ):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
            
    folium_static( map, width=1024 , height=600 )

        
def order_share_by_week( df1 ):
    # Quantidade de pedidos dividido por número unico de entregadores por semana
    # count() irá contar quantos ID unicos teve
    df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    # Iremos juntar as duas variaveis usando uma função do PANDA chamada merge
    # O how significa como vou juntar as duas coisas

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')

    return fig


def order_by_week( df1 ):
    # Criamos uma nova coluna chamada week_of_year para transformar o Order_date em coluna de semana

    # Usamos a função strftime(String format time) que irá formatar essa string no tempo

    # Dentro da função strftime, usamos a máscara '%U' que no caso é o formato que eu quero

    # A mascara '%U', irá olhar para o dia da coluna 'Order_Date' e irá mostrar qual é o número da semana que essa data estava

    # A mascara '%U', irá contar a partir de domingo como primeiro dia da semana, se usar o '%W', irá contar como segunda o primeiro
    # dia da semana

    # Uso o .dt para transformar a series strftime de strings para datas
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')


    # Aplicamos a todas as linhas da coluna 'ID' e 'week_of_year' e agrupamos por 'week_of_year', 
    # logo contamos a quantidade de elementos e usamos o reset_index para que o 'week_of_year' se transforme em uma coluna.
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()


    # iremos criar um gráfico de linha, utilizando o comando plotly.express que resumiu como px
    fig = px.line( df_aux, x='week_of_year', y='ID')
            
    return fig


def traffic_order_city( df1 ):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
        
    return fig


def traffic_order_share( df1 ):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN ', :]
    df_aux['entregas_percentual'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values='entregas_percentual', names='Road_traffic_density' )

    return fig


def order_metric( df1 ):
    cols = ['ID', 'Order_Date']

    # utilizei o loc para aplicar o cols em todas as linhas.
    # utilizei o groupby para agrupar na coluna Order_Date
    # utilizei o count para contar 
    # Utilizei o reset_index para iniciar um novo index e transformar novamente o Order_Date como uma coluna
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    # desenhar gráfico de linhas
    # bar de barra
    fig = px.bar(df_aux, x='Order_Date', y='ID')
            
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


# -----------------------------------------------------Início da Estrutura lógica do código---------------------------------------------------------------------------------------------

# -------------------------------------
# Import DataSet
# -------------------------------------
df = pd.read_csv('dataset/train.csv')


# -------------------------------------
# Limpando os dados
# -------------------------------------
df1 = clean_code( df )


# ========================================================================================================================================================================
# BARRA LATERAL
# ========================================================================================================================================================================

st.header('Marktplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        fig = order_metric( df1 )
        st.markdown('# Orders by Day')
        st.plotly_chart( fig, use_container_width=True )
        
                   
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df1 )
            st.header('Traffic Order Share' )
            st.plotly_chart(fig, use_container_width=True )
            
    
        with col2:
            fig = traffic_order_city( df1 )
            st.header('Traffic Order City' )
            st.plotly_chart(fig, use_container_width=True )
            
            
with tab2:
    with st.container():
        fig = order_by_week( df1 )
        st.markdown('# Order by Week')
        st.plotly_chart(fig, use_container_width=True )
    
    
    with st.container():
        fig = order_share_by_week( df1 )
        st.markdown('# Order share by Week') 
        st.plotly_chart(fig, use_container_width=True)
            
    
with tab3:
    st.markdown('# Country Maps')
    country_maps( df1 )