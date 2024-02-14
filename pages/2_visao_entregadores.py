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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )


# ---------------------------------------------------------------------------
# Funções
# ---------------------------------------------------------------------------

def top_delivers( df1, top_asc ):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']].groupby(['City', 'Delivery_person_ID'])
                                                   .max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())
                
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    # drop=True  remove os index antigo, deixando somente o reset_index
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
                
    return df3

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

# Import DataSet

df = pd.read_csv('dataset/train.csv')

df1 = clean_code( df )


# ---------VISÃO_DOS_ENTREGADORES-----------------------------------------------------------------------------------------------------------------------------------------



# ========================================================================================================================================================================
# BARRA LATERAL
# ========================================================================================================================================================================

st.header('Marktplace - Visão Entregadores')


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
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade )
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
            
            
        with col3:
            melhor_condição = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição', melhor_condição )
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao )
    
                        
    with st.container():
        st.markdown( '''___''' )
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliações medias por Entregador' )
            va_mean_entr = df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe( va_mean_entr )
        
        with col2:
            st.markdown( '##### Avaliação media por trânsito' )
            df_mean_std_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density')
                                                                               .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudança de nome das colunas
            df_mean_std_traffic.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_mean_std_traffic = df_mean_std_traffic.reset_index()
            st.dataframe( df_mean_std_traffic )
            
            st.markdown( '##### Avaliação media por clima' )
            df_mean_std_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions')
                                                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudança de nome das colunas
            df_mean_std_weather.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_mean_std_weather = df_mean_std_weather.reset_index()
            st.dataframe( df_mean_std_weather )
    
    with st.container():
        st.markdown( '''___''' )
        st.title( 'Velocidade de Entrega' )
                   
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rapidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
        
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )