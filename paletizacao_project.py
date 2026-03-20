import streamlit as st
import plotly.graph_objects as go
import math
import pandas as pd

# Titulo da página
st.markdown('<h1 style="text-align: center; font-size: 30px;">Simulador de paletização</h1>', unsafe_allow_html=True)
# Subtitulo
st.markdown('<h1 style="text-align: center; font-size: 20px;">Rotina para simular a quantidade de caixas por fileira ou palete fechado!</h1>', unsafe_allow_html=True)    

# Upload da planilha
uploaded_file = st.file_uploader('Faça o upload da planilha Excel:', type=['xlsx', 'csv'])

if uploaded_file is not None:
    produtos = pd.read_excel(uploaded_file, engine='openpyxl')

    # Excluindo colunas desncessárias para o calculo.
    produtos = produtos.drop(columns=['SALDO', 'CÓD. BARRAS UNID.', 'USA MASTER', 'IMG. VENDA', 'IMG. MASTER', 'TIPO DE MOMV', 'SHELF LIFE', 'FRAGIL', 'CLASS. LOG', 'DATA', 'INMETRO'])                                  

    # Convertendo colunas type object para os formatos corretos
    produtos['DESCRIÇÃO COMPLETA'] = produtos['DESCRIÇÃO COMPLETA'].astype(str)
    produtos['FORNECEDOR'] = produtos['FORNECEDOR'].astype(str)
    produtos['ÁREA'] = produtos['ÁREA'].astype(str)

    # SKUs master que não possuem medidas no campo master - Substituindo pela informação cadastrada da embalagem de venda.
    produtos.loc[(produtos['ALTURA MASTER'] == 0) & (produtos['QTD. MASTER'] == 1), 'ALTURA MASTER'] = produtos['ALTURA']
    produtos.loc[(produtos['LARGURA MASTER'] == 0) & (produtos['QTD. MASTER'] == 1), 'LARGURA MASTER'] = produtos['LARGURA']
    produtos.loc[(produtos['COMPRIMENTO MASTER'] == 0) & (produtos['QTD. MASTER'] == 1), 'COMPRIMENTO MASTER'] = produtos['COMPRIMENTO']

    # Removendo SKUs sem medidas master cadastrada (evitando erros de calculo)
    produtos = produtos[produtos['ALTURA MASTER'] != 0]

    # Verificar se a coluna 'Cod' está no formato string e converter se necessário
    if produtos['CÓD.'].dtype != 'object':
        produtos['CÓD.'] = produtos['CÓD.'].astype(str)

    produtos['CÓD.'] = produtos['CÓD.'].str.strip()
    produtos['ALTURA MASTER'] = produtos['ALTURA MASTER'].astype(int)
    produtos['LARGURA MASTER'] = produtos['LARGURA MASTER'].astype(int)
    produtos['COMPRIMENTO MASTER'] = produtos['COMPRIMENTO MASTER'].astype(int)
    produtos['FORNECEDOR'] = produtos['FORNECEDOR'].str.strip()

    fornecedores = produtos['FORNECEDOR'].unique()
    fornecedor_selecionado = st.selectbox('Selecione o fornecedor:', sorted(fornecedores))

    fornecedor_selecionado = fornecedor_selecionado.strip().upper()

    produtos_fornecedor = produtos[(produtos['FORNECEDOR'] == fornecedor_selecionado)]  

    produtos_fornecedor

    simular_paletizacao = ["--", "Simular paletização (uma fileira)", "Simular paletização (fechada)"]
    simulacao_selecionada = st.selectbox('Selecione a simulação:', simular_paletizacao)

    if simulacao_selecionada == "Simular paletização (uma fileira)":
        if not produtos_fornecedor.empty:
            resultados = produtos_fornecedor.copy()

            # SKUs master que não possuem medidas no campo master - Substituindo pela informação cadastrada da embalagem de venda.
            resultados.loc[(resultados['ALTURA MASTER'] == 0) & (resultados['QTD. MASTER'] == 1), 'ALTURA MASTER'] = resultados['ALTURA']
            resultados.loc[(resultados['LARGURA MASTER'] == 0) & (resultados['QTD. MASTER'] == 1), 'LARGURA MASTER'] = resultados['LARGURA']
            resultados.loc[(produtos['COMPRIMENTO MASTER'] == 0) & (resultados['QTD. MASTER'] == 1), 'COMPRIMENTO MASTER'] = resultados['COMPRIMENTO']

            # Removendo SKUs sem medidas master cadastrada (evitando erros de calculo)
            resultados = resultados[resultados['ALTURA MASTER'] != 0]

            palete_largura = 100
            palete_comprimento = 120

            colunas_resultado = {
                '75cm (1 fileira PBR)': [],
                '115cm (1 fileira PBR)': [],
                '155cm (1 fileira PBR)': []
            }

            for altura_max in [75, 115, 155]:
                col = f"{altura_max}cm (1 fileira PBR)"
                temp_result = []

                for _, row in produtos_fornecedor.iterrows():
                    comprimento_master = row['COMPRIMENTO MASTER']
                    largura_master = row['LARGURA MASTER']
                    altura_master = row['ALTURA MASTER']

                    # Testar duas orientações para melhor aproveitamento do comprimento do palete
                    colunas_opcao1 = math.floor(palete_comprimento / comprimento_master)
                    colunas_opcao2 = math.floor(palete_comprimento / largura_master)
                    n_colunas_fileira = max(colunas_opcao1, colunas_opcao2)

                    # Empilhamento vertical
                    n_empilhadas = math.floor(altura_max / altura_master)

                    total_caixas = n_colunas_fileira * n_empilhadas
                    temp_result.append(total_caixas)

                colunas_resultado[col] = temp_result

            for coluna, valores in colunas_resultado.items():
                resultados[coluna] = valores

            # Palete X
            palete_x_largura = 110
            palete_x_comprimento = 110

            colunas_resultado_x = {
                '75cm (1 fileira X)': [],
                '115cm (1 fileira X)': [],
                '155cm (1 fileira X)': []
            }

            for altura_max_x in [75, 115, 155]:
                col = f"{altura_max_x}cm (1 fileira X)"
                temp_result = []

                for _, row in produtos_fornecedor.iterrows():
                    comprimento_master = row['COMPRIMENTO MASTER']
                    largura_master = row['LARGURA MASTER']
                    altura_master = row['ALTURA MASTER']

                    # Testar duas orientações para melhor aproveitamento do comprimento do palete
                    colunas_opcao1 = math.floor(palete_x_comprimento / comprimento_master)
                    colunas_opcao2 = math.floor(palete_x_comprimento / largura_master)
                    n_colunas_fileira = max(colunas_opcao1, colunas_opcao2)

                    # Empilhamento vertical
                    n_empilhadas = math.floor(altura_max_x / altura_master)

                    total_caixas = n_colunas_fileira * n_empilhadas
                    temp_result.append(total_caixas)

                colunas_resultado_x[col] = temp_result

            for coluna, valores in colunas_resultado_x.items():
                resultados[coluna] = valores

            # Excluindo colunas desnecessárias para exibição
            resultados = resultados.drop(columns=['PESO KG', 'CÓD. BARRAS NFE (EAN)', 'PESO MASTER KG', 'ALTURA', 'LARGURA', 'COMPRIMENTO', 'M3', 'ÁREA',
                                                'ALTURA MASTER', 'LARGURA MASTER', 'FORNECEDOR','COMPRIMENTO MASTER'])

            rename = {'CÓD. BARRAS UNID. NFE (EANTRIB)': 'CÓD. BARRAS UNID.'}
            resultados.rename(columns=rename, inplace=True)

            st.dataframe(resultados)

            output_excel = f"Simulação de Paletização (fileira) - {fornecedor_selecionado}.xlsx"
            resultados.to_excel(output_excel, index=False)
            st.success("Simulação de paletização (uma fileira) salva com sucesso!")
            st.download_button("📥 Baixar DataFrame", data=open(output_excel, "rb"), file_name=output_excel)

    if simulacao_selecionada == "Simular paletização (fechada)":
        if not produtos_fornecedor.empty:
            resultados = []

            palete_largura = 100
            palete_comprimento = 120
                    
            for altura_max in [75, 115, 155]:
                for _, row in produtos_fornecedor.iterrows():
                    comprimento_master = row['COMPRIMENTO MASTER']
                    largura_master = row['LARGURA MASTER']
                    altura_master = row['ALTURA MASTER']

                    caixas_l1 = math.floor(palete_largura / largura_master)
                    caixas_c1 = math.floor(palete_comprimento / comprimento_master)
                    total1 = caixas_l1 * caixas_c1

                    caixas_l2 = math.floor(palete_largura / comprimento_master)
                    caixas_c2 = math.floor(palete_comprimento / largura_master)
                    total2 = caixas_l2 * caixas_c2

                    if total2 > total1:
                        caixas_por_camada = caixas_l2 * caixas_c2
                    else:
                        caixas_por_camada = caixas_l1 * caixas_c1

                    numero_camadas = math.floor(altura_max / altura_master)
                    total_caixas = caixas_por_camada * numero_camadas

                    resultados.append({
                        'CÓD.': row['CÓD.'],
                        'DESCRIÇÃO COMPLETA': row['DESCRIÇÃO COMPLETA'],
                        'ENDEREÇO': row['ENDEREÇO'],
                        'REFERÊNCIA': row['REFERÊNCIA'],
                        'CÓD. BARRAS': row['CÓD. BARRAS'],
                        'CÓD. BARRAS UNID': row['CÓD. BARRAS NFE (EAN)'],
                        'CÓD. BARRAS MASTER': row['CÓD. BARRAS MASTER'],
                        'QTDE MASTER': row['QTD. MASTER'],
                        'EMBALAGEM': row['EMBALAGEM'],
                        'ALTURA MAX PALETE': altura_max,
                        'TOTAL DE CAIXAS': total_caixas,
                        'LASTRO': caixas_por_camada,
                        'CAMADAS': numero_camadas
                    })

            df_resultado = pd.DataFrame(resultados)
            df_pivot = df_resultado.pivot(index=['CÓD.', 'DESCRIÇÃO COMPLETA', 'ENDEREÇO', 'REFERÊNCIA', 'CÓD. BARRAS', 'CÓD. BARRAS UNID', 'CÓD. BARRAS MASTER', 
                                                        'QTDE MASTER', 'EMBALAGEM'], columns='ALTURA MAX PALETE', values='TOTAL DE CAIXAS').reset_index()
            df_pivot.columns.name = None
            st.subheader('DataFrame com os resultados:')
            st.dataframe(df_pivot, use_container_width=True)

            # Salvando a planilha em um arquivo excel
            with pd.ExcelWriter("Simulação de Paletização.xlsx") as writer:
                df_pivot.to_excel(writer, sheet_name='Simulação de Paletização', index=False)
                st.success("Simulação de paletização (fechada) salva com sucesso!")

            # Botão para donwload
            with open("Simulação de Paletização.xlsx", 'rb') as f:
                    t.download_button("📥 Baixar DataFrame", f, file_name="Simulação de Paletização.xlsx")

    st.write('_________')
    codigo = st.text_input('Digite o código do produto:').strip()

    palete_pbr_largura = 100
    palete_pbr_comprimento = 120

    palete_x_largura = 110
    palete_x_comprimento = 110

    st.markdown('<h1 style="text-align: center; font-size: 30px;">📏​ Altura Máxima do Palete (em cm)</h1>', unsafe_allow_html=True)
    medidas = [50, 75, 80, 110, 115, 155]
    altura_max_palete = st.selectbox('Selecione a altura máxima do palete (em cm):', medidas)

    tipo_palete = ["--", "Palete PBR", "Palete X"]
    palete_selecionado = st.selectbox("Selecione o tipo do palete:", tipo_palete)

    if palete_selecionado == "Palete PBR" and uploaded_file is not None:
        produto_selecionado = produtos_fornecedor[produtos_fornecedor['CÓD.'].str.upper() == codigo.upper()]
        if not produto_selecionado.empty:
            comprimento_master = produto_selecionado['COMPRIMENTO MASTER'].values[0]
            largura_master = produto_selecionado['LARGURA MASTER'].values[0]
            altura_master = produto_selecionado['ALTURA MASTER'].values[0]
        else:
            st.warning("Código do produto não encontrado.")

        descricao = produto_selecionado['DESCRIÇÃO COMPLETA'].values[0]
        fornecedor = produto_selecionado['FORNECEDOR'].values[0]
        st.write(f"**Produto selecionado:** {descricao}")
        st.write(f"**Fornecedor:** {fornecedor}")

        caixas_l1 = math.floor(palete_pbr_largura / largura_master)
        caixas_c1 = math.floor(palete_pbr_comprimento / comprimento_master)
        total1 = caixas_l1 * caixas_c1

        caixas_l2 = math.floor(palete_pbr_largura / comprimento_master)
        caixas_c2 = math.floor(palete_pbr_comprimento / largura_master)
        total2 = caixas_l2 * caixas_c2

        if total2 > total1:
            largura_caixa, comprimento_caixa = comprimento_master, largura_master
            caixas_por_linha = caixas_l2
            caixas_por_coluna = caixas_c2
            orientacao = "Caixa girada (melhor aproveitamento)"
        else:
            largura_caixa, comprimento_caixa = largura_master, comprimento_master
            caixas_por_linha = caixas_l1
            caixas_por_coluna = caixas_c1
            orientacao = "Caixa na orientação original"

        caixas_por_camada = caixas_por_linha * caixas_por_coluna
        numero_camadas = math.floor(altura_max_palete / altura_master)
        total_caixas = caixas_por_camada * numero_camadas

        fig = go.Figure()

        for camada in range(numero_camadas):
            for i in range(caixas_por_linha):
                for j in range(caixas_por_coluna):
                    x0 = i * largura_caixa
                    y0 = j * comprimento_caixa
                    z0 = camada * altura_master

                    x = [x0, x0+largura_master, x0+largura_master, x0, x0, x0+largura_master, x0+largura_master, x0]
                    y = [y0, y0, y0+comprimento_master, y0+comprimento_master, y0, y0, y0+comprimento_master, y0+comprimento_master]
                    z = [z0, z0, z0, z0, z0+altura_master, z0+altura_master, z0+altura_master, z0+altura_master]

                    fig.add_trace(go.Mesh3d(
                        x=x, y=y, z=z,
                        color='lightblue',
                        opacity=0.5,
                        showscale=False
                    ))

        fig.update_layout(
            scene=dict(
                xaxis_title='Largura do Palete (cm)',
                yaxis_title='Comprimento do Palete (cm)',
                zaxis_title='Altura Empilhada (cm)',
                xaxis=dict(range=[0, palete_pbr_largura]),
                yaxis=dict(range=[0, palete_pbr_comprimento]),
                zaxis=dict(range=[0, altura_max_palete + altura_master])
        ),
            margin=dict(r=10, l=10, b=10, t=10),
            width=2000,
            height=600
        )

        st.plotly_chart(fig)
        st.subheader("📊 Resultado do Cálculo")
        st.write(f"**Orientação usada:** {orientacao}")
        st.write(f"**Caixas por camada:** {caixas_por_camada}")
        st.write(f"**Número de camadas possíveis:** {numero_camadas}")
        st.success(f"**Total de caixas que cabem no palete PBR: {total_caixas} caixas**")
    
    if palete_selecionado == "Palete X" and uploaded_file is not None:
        produto_selecionado = produtos_fornecedor[produtos_fornecedor['CÓD.'].str.upper() == codigo.upper()]
        if not produto_selecionado.empty:
            comprimento_master = produto_selecionado['COMPRIMENTO MASTER'].values[0]
            largura_master = produto_selecionado['LARGURA MASTER'].values[0]
            altura_master = produto_selecionado['ALTURA MASTER'].values[0]
        else:
            st.warning("Código do produto não encontrado.")

        descricao = produto_selecionado['DESCRIÇÃO COMPLETA'].values[0]
        fornecedor = produto_selecionado['FORNECEDOR'].values[0]
        st.write(f"**Produto selecionado:** {descricao}")
        st.write(f"**Fornecedor:** {fornecedor}")

        caixas_l1 = math.floor(palete_x_largura / largura_master)
        caixas_c1 = math.floor(palete_x_comprimento / comprimento_master)
        total1 = caixas_l1 * caixas_c1

        caixas_l2 = math.floor(palete_x_largura / comprimento_master)
        caixas_c2 = math.floor(palete_x_comprimento / largura_master)
        total2 = caixas_l2 * caixas_c2

        if total2 > total1:
            largura_caixa, comprimento_caixa = comprimento_master, largura_master
            caixas_por_linha = caixas_l2
            caixas_por_coluna = caixas_c2
            orientacao = "Caixa girada (melhor aproveitamento)"
        else:
            largura_caixa, comprimento_caixa = largura_master, comprimento_master
            caixas_por_linha = caixas_l1
            caixas_por_coluna = caixas_c1
            orientacao = "Caixa na orientação original"

        caixas_por_camada = caixas_por_linha * caixas_por_coluna
        numero_camadas = math.floor(altura_max_palete / altura_master)
        total_caixas = caixas_por_camada * numero_camadas

        fig = go.Figure()

        for camada in range(numero_camadas):
            for i in range(caixas_por_linha):
                for j in range(caixas_por_coluna):
                    x0 = i * largura_caixa
                    y0 = j * comprimento_caixa
                    z0 = camada * altura_master

                    x = [x0, x0+largura_master, x0+largura_master, x0, x0, x0+largura_master, x0+largura_master, x0]
                    y = [y0, y0, y0+comprimento_master, y0+comprimento_master, y0, y0, y0+comprimento_master, y0+comprimento_master]
                    z = [z0, z0, z0, z0, z0+altura_master, z0+altura_master, z0+altura_master, z0+altura_master]

                    fig.add_trace(go.Mesh3d(
                        x=x, y=y, z=z,
                        color='lightblue',
                        opacity=0.5,
                        showscale=False
                    ))

        fig.update_layout(
            scene=dict(
                xaxis_title='Largura do Palete (cm)',
                yaxis_title='Comprimento do Palete (cm)',
                zaxis_title='Altura Empilhada (cm)',
                xaxis=dict(range=[0, palete_x_largura]),
                yaxis=dict(range=[0, palete_x_comprimento]),
                zaxis=dict(range=[0, altura_max_palete + altura_master])
        ),
            margin=dict(r=10, l=10, b=10, t=10),
            width=2000,
            height=600
        )

        st.plotly_chart(fig)
        st.subheader("📊 Resultado do Cálculo")
        st.write(f"**Orientação usada:** {orientacao}")
        st.write(f"**Caixas por camada:** {caixas_por_camada}")
        st.write(f"**Número de camadas possíveis:** {numero_camadas}")
        st.success(f"**Total de caixas que cabem no palete PBR: {total_caixas} caixas**")
