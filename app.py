import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from tri_engine import TRIEngine

# Configuração da página
st.set_page_config(
    page_title="SIMULADOR TRI ENEM - Prof.Gezys",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo customizado
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Título e Descrição
st.title("🎯 SIMULADOR TRI/ENEM - Prof.Gezys")
st.markdown("""
Ferramenta de análise de desempenho baseada em **Teoria de Resposta ao Item (TRI)**.
Descubra sua nota estimada e identifique padrões de coerência pedagógica.
""")

# Sidebar para configurações
st.sidebar.header("⚙️ Configurações")

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["📝 Entrada de Dados", "📊 Análise", "📚 Sobre TRI", "❓ Como Usar"])

with tab1:
    st.header("Entrada de Dados da Prova")
    
    # SEÇÃO 1: Carregar Parâmetros de Referência
    st.subheader("1️⃣ Carregar Parâmetros de Referência (Opcional)")
    st.info("""
    **O que é isso?** Você pode fornecer um arquivo CSV com os parâmetros (a, b, c) das questões que você escolheu.
    Isso torna a nota 100% precisa para seu simulado.
    
    **Sem arquivo:** O sistema usa parâmetros realistas simulados (estimativa confiável).
    """)
    
    parametros_fornecidos = False
    params_a = None
    params_b = None
    params_c = None
    
    col_param1, col_param2 = st.columns(2)
    
    with col_param1:
        arquivo_parametros = st.file_uploader(
            "📁 Upload do arquivo CSV com parâmetros (a, b, c)",
            type="csv",
            key="parametros_upload"
        )
        
        if arquivo_parametros is not None:
            try:
                df_params = pd.read_csv(arquivo_parametros)
                
                # Validar colunas
                colunas_necessarias = ['a', 'b', 'c']
                if all(col in df_params.columns for col in colunas_necessarias):
                    params_a = df_params['a'].values
                    params_b = df_params['b'].values
                    params_c = df_params['c'].values
                    parametros_fornecidos = True
                    
                    st.success(f"✅ {len(params_a)} parâmetros carregados com sucesso!")
                    st.write(f"**Primeiras 5 linhas:**")
                    st.dataframe(df_params.head())
                else:
                    st.error(f"❌ O arquivo deve conter as colunas: {colunas_necessarias}")
            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
    
    with col_param2:
        if st.button("📖 Ver Exemplo de CSV"):
            st.write("**Formato esperado do arquivo CSV:**")
            exemplo_csv = pd.DataFrame({
                'a': [1.5, 1.2, 1.8],
                'b': [-2.0, 0.0, 2.0],
                'c': [0.20, 0.20, 0.20]
            })
            st.dataframe(exemplo_csv)
            st.code("""a,b,c
1.5,-2.0,0.20
1.2,0.0,0.20
1.8,2.0,0.20""", language="csv")
    
    st.divider()
    
    # SEÇÃO 2: Número de Questões
    st.subheader("2️⃣ Configurar Prova")
    
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        num_questoes = st.slider("Quantas questões tem a prova?", 5, 180, 45)
    
    with col_q2:
        st.write(f"**Questões configuradas:** {num_questoes}")
    
    st.divider()
    
    # SEÇÃO 3: Tipo de Entrada de Respostas
    st.subheader("3️⃣ Inserir Respostas")
    
    tipo_entrada = st.radio(
        "Como deseja inserir as respostas?",
        ["Manualmente", "Upload CSV", "Usar Exemplo"]
    )
    
    respostas = None
    
    if tipo_entrada == "Manualmente":
        st.info("Digite 1 para acerto e 0 para erro, separados por vírgula ou espaço.")
        
        respostas_input = st.text_area(
            "Respostas (ex: 1 0 1 1 0 1...)",
            height=100,
            placeholder="1 1 1 0 1 0 1 1 0 1..."
        )
        
        if respostas_input:
            try:
                # Limpar e converter
                respostas_str = respostas_input.replace(",", " ").split()
                respostas = np.array([int(r) for r in respostas_str])
                
                if len(respostas) != num_questoes:
                    st.warning(f"⚠️ Você inseriu {len(respostas)} respostas, mas selecionou {num_questoes} questões.")
                else:
                    st.success(f"✅ {len(respostas)} respostas carregadas com sucesso!")
            except ValueError:
                st.error("❌ Erro ao processar as respostas. Use apenas 0 e 1.")
                respostas = None
    
    elif tipo_entrada == "Upload CSV":
        st.info("O arquivo deve ter uma coluna com as respostas (1 ou 0).")
        
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv", key="respostas_upload")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head())
                
                # Tentar extrair coluna de respostas
                colunas_disponiveis = df.columns.tolist()
                coluna_respostas = st.selectbox("Selecione a coluna com as respostas:", colunas_disponiveis)
                
                if coluna_respostas:
                    respostas = np.array(df[coluna_respostas].values)
                    
                    if len(respostas) != num_questoes:
                        st.warning(f"⚠️ O arquivo tem {len(respostas)} respostas, mas você selecionou {num_questoes} questões.")
                    else:
                        st.success(f"✅ {len(respostas)} respostas carregadas!")
            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
    
    else:  # Usar Exemplo
        st.info("Usando dados simulados para demonstração.")
        
        # Gerar exemplo coerente
        np.random.seed(42)
        respostas = np.array([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0,
                              1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0,
                              1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0])
        
        if len(respostas) > num_questoes:
            respostas = respostas[:num_questoes]
        
        st.write(f"Exemplo: {' '.join(map(str, respostas[:20]))}... ({len(respostas)} questões)")
        st.success(f"✅ Exemplo carregado com {len(respostas)} respostas!")

with tab2:
    st.header("Análise de Desempenho")
    
    if respostas is None:
        st.warning("⚠️ Por favor, insira as respostas na aba 'Entrada de Dados' primeiro.")
    else:
        # Gerar ou usar parâmetros fornecidos
        if parametros_fornecidos:
            # Usar parâmetros fornecidos
            if len(params_a) != len(respostas):
                st.error(f"❌ Erro: Você tem {len(params_a)} parâmetros mas {len(respostas)} respostas. Devem ser iguais!")
            else:
                st.success(f"✅ Usando {len(params_a)} parâmetros fornecidos como referência!")
                num_itens = len(params_a)
        else:
            # Gerar parâmetros simulados
            np.random.seed(42)
            num_itens = len(respostas)
            
            # Parâmetros realistas para ENEM
            params_a = np.random.uniform(0.8, 2.5, num_itens)  # Discriminação
            params_b = np.linspace(-3, 3, num_itens)  # Dificuldade (distribuída)
            params_c = np.random.uniform(0.15, 0.25, num_itens)  # Acerto casual
            
            st.info("ℹ️ Usando parâmetros realistas simulados (não fornecidos como referência).")
        
        # Calcular TRI
        engine = TRIEngine()
        theta_estimado = engine.estimate_theta(respostas, params_a, params_b, params_c)
        nota_enem = engine.to_enem_score(theta_estimado)
        analise = engine.analyze_consistency(theta_estimado, respostas, params_b)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📌 Proficiência (θ)",
                f"{theta_estimado:.2f}",
                delta="Escala TRI"
            )
        
        with col2:
            st.metric(
                "🎯 Nota ENEM",
                f"{nota_enem:.0f}",
                delta="Escala 0-1000"
            )
        
        with col3:
            total_acertos = int(np.sum(respostas))
            st.metric(
                "✅ Total de Acertos",
                f"{total_acertos}/{num_itens}",
                delta=f"{100*total_acertos/num_itens:.1f}%"
            )
        
        with col4:
            coerencia_color = "🟢" if analise['coerencia'] == "Alta" else "🔴"
            st.metric(
                "🔗 Coerência Pedagógica",
                analise['coerencia'],
                delta=coerencia_color
            )
        
        st.divider()
        
        # Análise Detalhada
        col_analise1, col_analise2 = st.columns(2)
        
        with col_analise1:
            st.subheader("📊 Distribuição de Acertos por Dificuldade")
            
            # Criar bins de dificuldade
            bins = np.linspace(params_b.min(), params_b.max(), 6)
            bin_labels = ['Muito Fácil', 'Fácil', 'Médio', 'Difícil', 'Muito Difícil']
            
            df_analise = pd.DataFrame({
                'Dificuldade': params_b,
                'Resposta': respostas,
                'Bin': pd.cut(params_b, bins=bins, labels=bin_labels, include_lowest=True)
            })
            
            acertos_por_dif = df_analise.groupby('Bin')['Resposta'].agg(['sum', 'count'])
            acertos_por_dif['Taxa'] = (acertos_por_dif['sum'] / acertos_por_dif['count'] * 100).round(1)
            
            fig_dif = go.Figure(data=[
                go.Bar(
                    x=acertos_por_dif.index.astype(str),
                    y=acertos_por_dif['Taxa'],
                    marker_color=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#c0392b'],
                    text=acertos_por_dif['Taxa'].apply(lambda x: f'{x:.0f}%'),
                    textposition='auto',
                )
            ])
            fig_dif.update_layout(
                title="Taxa de Acerto por Nível de Dificuldade",
                xaxis_title="Dificuldade do Item",
                yaxis_title="Taxa de Acerto (%)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_dif, use_container_width=True)
        
        with col_analise2:
            st.subheader("📈 Curva Característica do Item (CCI)")
            
            # Plotar CCI para alguns itens representativos
            theta_range = np.linspace(-4, 4, 100)
            
            # Selecionar 3 itens: fácil, médio, difícil
            idx_facil = np.argmin(params_b)
            idx_medio = np.argmin(np.abs(params_b))
            idx_dificil = np.argmax(params_b)
            
            indices = [idx_facil, idx_medio, idx_dificil]
            labels = ['Fácil', 'Médio', 'Difícil']
            cores = ['#2ecc71', '#f39c12', '#e74c3c']
            
            fig_cci = go.Figure()
            
            for idx, label, cor in zip(indices, labels, cores):
                p_theta = engine.logistic_3pl(
                    theta_range,
                    params_a[idx],
                    params_b[idx],
                    params_c[idx]
                )
                fig_cci.add_trace(go.Scatter(
                    x=theta_range,
                    y=p_theta,
                    mode='lines',
                    name=f'{label} (b={params_b[idx]:.2f})',
                    line=dict(color=cor, width=2)
                ))
            
            # Marcar a posição do aluno
            fig_cci.add_vline(
                x=theta_estimado,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Seu θ = {theta_estimado:.2f}",
                annotation_position="top right"
            )
            
            fig_cci.update_layout(
                title="Curva Característica do Item (CCI)",
                xaxis_title="Proficiência (θ)",
                yaxis_title="Probabilidade de Acerto",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_cci, use_container_width=True)
        
        st.divider()
        
        # Recomendações
        st.subheader("💡 Recomendações de Mentoria")
        
        if nota_enem >= 900:
            st.success(f"""
            ✅ **Parabéns!** Sua nota estimada de **{nota_enem:.0f}** está acima de 900!
            
            **Próximos passos:**
            - Mantenha a consistência em suas respostas
            - Foque em aprimorar os itens de alta dificuldade
            - Revise estratégias de tempo e gestão de ansiedade
            """)
        elif nota_enem >= 800:
            st.info(f"""
            ℹ️ Sua nota estimada é **{nota_enem:.0f}**. Você está no caminho certo!
            
            **Para alcançar 900+:**
            - Aumente a taxa de acerto em itens de dificuldade média
            - Revise conceitos que causam erros em questões fáceis
            - Pratique mais questões de alta dificuldade
            """)
        else:
            st.warning(f"""
            ⚠️ Sua nota estimada é **{nota_enem:.0f}**. Há espaço para melhoria!
            
            **Plano de ação:**
            - Revise a base de conteúdo (itens fáceis)
            - Aumente o tempo de estudo em tópicos frágeis
            - Pratique mais questões para ganhar confiança
            """)
        
        if analise['coerencia'] == "Baixa":
            st.error("""
            🔴 **Coerência Pedagógica Baixa**
            
            Você está errando muitas questões fáceis. Isso sugere:
            - Falta de atenção ou leitura apressada
            - Gaps de conhecimento em conceitos básicos
            - Possível chute em questões difíceis
            
            **Ação imediata:** Revise os conceitos fundamentais antes de tentar questões mais complexas.
            """)

with tab3:
    st.header("📚 O que é TRI?")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.subheader("Teoria de Resposta ao Item (TRI)")
        st.markdown("""
        A TRI é um modelo matemático que avalia a proficiência do estudante 
        de forma mais sofisticada que a simples contagem de acertos.
        
        **Diferenças da TRI vs. Contagem de Acertos:**
        - **Contagem:** 45 acertos = 45 acertos (independente de quais)
        - **TRI:** 45 acertos em questões fáceis ≠ 45 acertos em questões difíceis
        
        A TRI considera a **dificuldade** e **discriminação** de cada item.
        """)
    
    with col_info2:
        st.subheader("Os 3 Parâmetros (Modelo 3PL)")
        st.markdown("""
        | Parâmetro | Significado |
        |-----------|------------|
        | **a** | Discriminação: capacidade de diferenciar alunos |
        | **b** | Dificuldade: nível de proficiência necessário |
        | **c** | Acerto casual: probabilidade de acerto por chute |
        """)
    
    st.divider()
    
    st.subheader("🎯 Por que a Coerência Pedagógica Importa?")
    st.markdown("""
    A TRI premia **coerência**. Se você acerta questões difíceis mas erra as fáceis,
    o sistema interpreta que você "chutou" as difíceis. Sua nota será penalizada!
    
    **Exemplo:**
    - **Aluno A:** Acerta 45 questões fáceis e médias, erra as difíceis → Nota alta
    - **Aluno B:** Acerta 45 questões (misturado: fáceis, médias e difíceis) → Nota menor
    
    Ambos acertaram 45, mas o Aluno A tem nota maior porque foi **coerente**.
    """)
    
    st.divider()
    
    st.subheader("📊 Escala ENEM")
    st.markdown("""
    - **Média:** 500 pontos
    - **Desvio Padrão:** 100 pontos
    - **Mínimo:** 0 pontos
    - **Máximo:** 1000 pontos
    
    A nota é calculada a partir do **theta (θ)** estimado pela TRI,
    usando a fórmula: **Nota = 500 + 100 × θ**
    """)

with tab4:
    st.header("❓ Como Usar o Simulador")
    
    st.subheader("Passo 1: Preparar o Arquivo de Parâmetros (Opcional)")
    st.markdown("""
    Se você quer máxima precisão, crie um arquivo CSV com os parâmetros das questões que você escolheu.
    
    **Formato do arquivo:**
    ```
    a,b,c
    1.5,-2.0,0.20
    1.2,0.0,0.20
    1.8,2.0,0.20
    ```
    
    - **a:** Discriminação (recomendado: 0.8 a 2.5)
    - **b:** Dificuldade (recomendado: -3 a 3)
    - **c:** Acerto casual (padrão: 0.20 para 5 alternativas)
    
    **Onde obter os parâmetros:**
    - Se usar questões do ENEM anterior: Baixe os Microdados do INEP
    - Se criar suas próprias questões: Etiquet as como Fácil/Médio/Difícil
    """)
    
    st.subheader("Passo 2: Carregar o Arquivo")
    st.markdown("""
    Na aba "Entrada de Dados", clique em "Upload do arquivo CSV com parâmetros".
    O sistema validará e carregará os dados.
    """)
    
    st.subheader("Passo 3: Inserir as Respostas")
    st.markdown("""
    Escolha uma das três formas:
    - **Manualmente:** Digite 1 para acerto, 0 para erro
    - **Upload CSV:** Carregue um arquivo com as respostas
    - **Usar Exemplo:** Teste com dados de demonstração
    """)
    
    st.subheader("Passo 4: Visualizar os Resultados")
    st.markdown("""
    Na aba "Análise", você verá:
    - **Nota ENEM:** Estimativa na escala 0-1000
    - **Proficiência (θ):** Valor bruto da TRI
    - **Coerência Pedagógica:** Se o padrão de respostas é consistente
    - **Gráficos:** Taxa de acerto por dificuldade e Curva Característica do Item
    """)
    
    st.divider()
    
    st.subheader("📥 Download do Arquivo de Exemplo")
    
    # Criar arquivo de exemplo
    exemplo_params = pd.DataFrame({
        'a': [1.5, 1.2, 1.8, 1.0, 2.0, 1.4, 1.6, 1.1, 1.9, 1.3],
        'b': [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
        'c': [0.20] * 10
    })
    
    csv_exemplo = exemplo_params.to_csv(index=False)
    
    st.download_button(
        label="📥 Baixar Arquivo de Exemplo (parametros_exemplo.csv)",
        data=csv_exemplo,
        file_name="parametros_exemplo.csv",
        mime="text/csv"
    )
    
    st.write("Use este arquivo como template para criar o seu próprio!")

# Footer
st.divider()
st.markdown("""
---
**Corretor TRI ENEM v2.0** | Desenvolvido com ❤️ usando Streamlit e Python
*Ferramenta educacional para análise de desempenho baseada em TRI*
""")
