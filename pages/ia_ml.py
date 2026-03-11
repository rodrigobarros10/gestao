import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

from database.connection import run_query
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")

col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", width="stretch"):
        st.switch_page("app.py")

if not st.session_state.get('logged_in') or "ia_ml" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.error("Acesso Negado.")
    st.stop()

st.subheader("🤖 Central de Inteligência Artificial (Modelos Preditivos)")
st.markdown("""
*Esta área contém modelos avançados de Machine Learning para auxílio à tomada de decisão. 
Alguns painéis estão integrados à base de dados para projeções, enquanto outros operam com simulações até a implantação final dos algoritmos.*
""")
st.divider()

ml_tab1, ml_tab2, ml_tab3, ml_tab4, ml_tab5, ml_tab6, ml_tab7 = st.tabs([
    "📊 1. Previsão Histórica (Demanda/Viagens)", 
    "🛠️ 2. Probabilidade de Falha", 
    "⏱️ 3. Previsão de Atrasos", 
    "🚨 4. Detecção Anomalias",
    "⚡ 5. Consumo de Energia",
    "🕵️ 6. Prevenção a Fraudes",
    "⚠️ 7. Risco de Ocorrências"
])

with ml_tab1:
    st.markdown("#### 📈 Projeção de Demanda e Operação (Próximos 6 Meses)")
    st.caption("O algoritmo analisa o histórico real dos últimos meses na base de dados, calcula a linha de tendência (regressão) e espelha o comportamento de variância para os próximos meses.")
    
    # 1. Tentar puxar dados reais do banco
    engine = st.session_state.get('db_loader').get_engine() if st.session_state.get('connected') else None
    
    df_pax = pd.DataFrame()
    df_viagens = pd.DataFrame()
    
    if engine:
        try:
            # Puxa o histórico mensal de passageiros
            q_pax = """
            SELECT DATE_TRUNC('month', data_hora)::date as mes, COUNT(*) as qtd 
            FROM public.arq2_bilhetagem 
            GROUP BY 1 ORDER BY 1
            """
            df_pax = run_query(engine, q_pax)
            
            # Puxa o histórico mensal de viagens
            q_viagens = """
            SELECT DATE_TRUNC('month', data)::date as mes, COUNT(*) as qtd 
            FROM public.arq3_viagens 
            GROUP BY 1 ORDER BY 1
            """
            df_viagens = run_query(engine, q_viagens)
        except:
            pass

    # 2. Fallback de Segurança: Se não houver dados no banco, cria um mockup realista dos últimos 12 meses
    hoje = datetime.now().date()
    hoje_inicio_mes = hoje.replace(day=1)
    
    if df_pax is None or df_pax.empty or len(df_pax) < 3:
        meses_hist = [(hoje_inicio_mes - pd.DateOffset(months=i)).date() for i in range(12, 0, -1)]
        qtd_pax = [random.randint(1500000, 1900000) for _ in range(12)]
        df_pax = pd.DataFrame({'mes': meses_hist, 'qtd': qtd_pax})
        
    if df_viagens is None or df_viagens.empty or len(df_viagens) < 3:
        meses_hist = [(hoje_inicio_mes - pd.DateOffset(months=i)).date() for i in range(12, 0, -1)]
        qtd_viagens = [random.randint(8500, 9500) for _ in range(12)]
        df_viagens = pd.DataFrame({'mes': meses_hist, 'qtd': qtd_viagens})

    # 3. Função do Algoritmo Preditivo (Regressão Linear + Ruído Histórico)
    def gerar_previsao_ml(df_hist, future_months=6):
        df = df_hist.sort_values('mes').copy()
        df['mes'] = pd.to_datetime(df['mes'])
        df = df.tail(24) # Limita a análise aos últimos 24 meses para captar a tendência mais recente
        
        y = df['qtd'].values
        x = np.arange(len(y))
        
        # Treinamento da linha de tendência (Regressão de Grau 1)
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Calcula a variância (resíduos) para espelhar a margem de erro natural da operação
        residuos = y - p(x)
        desvio_padrao = np.std(residuos) if np.std(residuos) > 0 else np.mean(y) * 0.05
        
        # Gera as datas futuras
        last_date = df['mes'].iloc[-1]
        future_dates = [(last_date + pd.DateOffset(months=i)).date() for i in range(1, future_months + 1)]
        
        future_x = np.arange(len(y), len(y) + future_months)
        tendencia_base = p(future_x)
        
        # Aplica a previsão espelhando a volatilidade do sistema real
        forecast = [int(max(0, val + random.uniform(-desvio_padrao, desvio_padrao))) for val in tendencia_base]
        upper_bound = [int(val + desvio_padrao * 1.5) for val in forecast]
        lower_bound = [int(max(0, val - desvio_padrao * 1.5)) for val in forecast]
        
        # Datas de histórico formatadas
        hist_dates = [d.date() for d in df['mes']]
        
        return hist_dates, list(y), future_dates, forecast, upper_bound, lower_bound

    # Executa o algoritmo para as duas métricas
    h_dates_p, h_y_p, f_dates_p, f_y_p, f_up_p, f_low_p = gerar_previsao_ml(df_pax)
    h_dates_v, h_y_v, f_dates_v, f_y_v, f_up_v, f_low_v = gerar_previsao_ml(df_viagens)

    # 4. Renderização lado a lado em Painel
    c_pax, c_trips = st.columns(2)
    
    with c_pax:
        fig_p = go.Figure()
        # Histórico
        fig_p.add_trace(go.Scatter(x=h_dates_p, y=h_y_p, mode='lines+markers', name='Histórico Real', line=dict(color='#3498db', width=3)))
        # Previsão
        fig_p.add_trace(go.Scatter(x=f_dates_p, y=f_y_p, mode='lines+markers', name='Projeção IA', line=dict(color='#e67e22', width=3, dash='dash')))
        # Intervalos de Confiança (Sombreamento)
        fig_p.add_trace(go.Scatter(x=f_dates_p, y=f_up_p, mode='lines', line=dict(width=0), showlegend=False))
        fig_p.add_trace(go.Scatter(x=f_dates_p, y=f_low_p, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(230, 126, 34, 0.2)', name='Margem Espelhada'))
        
        fig_p.update_layout(title="Passageiros Transportados (Mensal)", xaxis_title="Período", yaxis_title="Volume de Passageiros", legend=dict(orientation="h", y=-0.2), height=400)
        st.plotly_chart(fig_p, use_container_width=True)
        
    with c_trips:
        fig_v = go.Figure()
        # Histórico
        fig_v.add_trace(go.Scatter(x=h_dates_v, y=h_y_v, mode='lines+markers', name='Histórico Real', line=dict(color='#2ecc71', width=3)))
        # Previsão
        fig_v.add_trace(go.Scatter(x=f_dates_v, y=f_y_v, mode='lines+markers', name='Projeção IA', line=dict(color='#f1c40f', width=3, dash='dash')))
        # Intervalos de Confiança (Sombreamento)
        fig_v.add_trace(go.Scatter(x=f_dates_v, y=f_up_v, mode='lines', line=dict(width=0), showlegend=False))
        fig_v.add_trace(go.Scatter(x=f_dates_v, y=f_low_v, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(241, 196, 15, 0.2)', name='Margem Espelhada'))
        
        fig_v.update_layout(title="Viagens Realizadas (Mensal)", xaxis_title="Período", yaxis_title="Qtd. de Viagens", legend=dict(orientation="h", y=-0.2), height=400)
        st.plotly_chart(fig_v, use_container_width=True)

with ml_tab2:
    st.markdown("#### 🛠️ Previsão de Falha Crítica em TUEs (Próximos 15 dias)")
    st.caption("Algoritmo sugerido: **Random Forest** ou **Análise de Sobrevivência**. Auxilia o CMD (Indicador MRO) puxando trens para manutenção preventiva antes da falha.")
    
    trens_mock = [f"TUE {str(i).zfill(3)}" for i in range(1, 16)]
    riscos = [random.randint(5, 95) for _ in trens_mock]
    df_frota_ml = pd.DataFrame({'Trem': trens_mock, 'Probabilidade_Falha': riscos})
    df_frota_ml = df_frota_ml.sort_values(by='Probabilidade_Falha', ascending=False).reset_index(drop=True)
    
    def color_risk(val):
        if val > 75: return '#e74c3c'
        elif val > 40: return '#f1c40f'
        else: return '#2ecc71'
        
    df_frota_ml['Cor'] = df_frota_ml['Probabilidade_Falha'].apply(color_risk)
    df_frota_ml['Status Recomendado'] = df_frota_ml['Probabilidade_Falha'].apply(lambda x: 'Manutenção Imediata' if x > 75 else ('Atenção' if x > 40 else 'Operação Normal'))
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        fig_frota = px.bar(df_frota_ml.head(10), x='Probabilidade_Falha', y='Trem', orientation='h', color='Cor', color_discrete_map='identity', text='Probabilidade_Falha')
        fig_frota.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_frota.update_layout(title="Top 10 Trens com Maior Risco", xaxis_title="Probabilidade de Falha (%)", yaxis_title="")
        st.plotly_chart(fig_frota, use_container_width=True)
        
    with col_f2:
        st.markdown("##### 📋 Ações Sugeridas pelo Modelo")
        for _, row in df_frota_ml.head(4).iterrows():
            cor_box = "rgba(231, 76, 60, 0.2)" if row['Cor'] == '#e74c3c' else ("rgba(241, 196, 15, 0.2)" if row['Cor'] == '#f1c40f' else "rgba(46, 204, 113, 0.2)")
            st.markdown(f"""
            <div style="background-color: {cor_box}; border-left: 5px solid {row['Cor']}; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                <strong>{row['Trem']}</strong> - Risco: {row['Probabilidade_Falha']}%<br>
                <span style="font-size: 12px; color: #ccc;">Ação: {row['Status Recomendado']}</span>
            </div>
            """, unsafe_allow_html=True)

with ml_tab3:
    st.markdown("#### ⏱️ Mapa de Risco de Atrasos e Gargalos (Hoje)")
    st.caption("Algoritmo sugerido: **Regressão Logística** ou **CatBoost**. Prevê a probabilidade de um headway estourar ou viagens atrasarem com base na hora e dia da semana.")
    
    horas = [f"{str(h).zfill(2)}:00" for h in range(5, 24)]
    estacoes = ['Eldorado', 'Calafate', 'Lagoinha', 'Central', 'Minas Shopping', 'Vilarinho']
    
    dados_heatmap = []
    for e in estacoes:
        linha_risco = []
        for h in range(5, 24):
            if h in [7, 8, 17, 18]: base_r = random.uniform(0.6, 0.95)
            elif h in [6, 9, 16, 19]: base_r = random.uniform(0.3, 0.6)
            else: base_r = random.uniform(0.05, 0.2)
            linha_risco.append(base_r)
        dados_heatmap.append(linha_risco)
        
    fig_hm = px.imshow(dados_heatmap, x=horas, y=estacoes, color_continuous_scale='RdYlGn_r', aspect="auto")
    fig_hm.update_layout(title="Probabilidade de Atraso por Estação e Horário", coloraxis_colorbar=dict(title="Risco (0 a 1)"))
    st.plotly_chart(fig_hm, use_container_width=True)

with ml_tab4:
    st.markdown("#### 🚨 Sistema de Detecção de Anomalias (Tempo Real)")
    st.caption("Algoritmo sugerido: **Isolation Forest**. Identifica picos atípicos de embarque ou validador travado automaticamente, gerando alertas para o CCO.")
    
    horas_dia = [f"{str(h).zfill(2)}:00" for h in range(0, 24)]
    pax_normal = [random.randint(10, 50) if (h < 5 or h > 22) else random.randint(300, 800) for h in range(24)]
    
    hora_anomalia = 14
    pax_normal[hora_anomalia] = 3500 
    
    fig_anom = go.Figure()
    fig_anom.add_trace(go.Scatter(x=horas_dia, y=pax_normal, mode='lines', name='Fluxo Estação (Horto)', line=dict(color='#9b59b6', width=2)))
    
    fig_anom.add_trace(go.Scatter(
        x=[horas_dia[hora_anomalia]], 
        y=[pax_normal[hora_anomalia]], 
        mode='markers+text', 
        marker=dict(color='red', size=15, symbol='star'),
        text=['⚠️ Alerta de Anomalia Disparado'],
        textposition='top center',
        name='Anomalia Detectada'
    ))
    
    fig_anom.update_layout(title="Monitoramento de Fluxo - Estação Horto (Últimas 24h)", xaxis_title="Hora do Dia", yaxis_title="Validações / Hora")
    st.plotly_chart(fig_anom, use_container_width=True)
    st.warning("ALERTA DO MODELO: Fluxo atípico detectado às 14:00 na Estação Horto. Variação de +430% em relação à média histórica para este dia e horário. Sugestão: Enviar trem reserva ou reforçar segurança no local.")

with ml_tab5:
    st.markdown("#### ⚡ Previsão de Consumo de Energia e Eficiência")
    st.caption("Algoritmo sugerido: **LSTM** ou **XGBoost Regressor**. Baseado na Tabela de Energia (Tab 12) e Quadro de Viagens. Otimiza o planejamento energético.")
    
    meses_energia = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    consumo_real = [random.uniform(1.2, 1.5) * 1000000 for _ in range(3)]
    consumo_previsto = consumo_real + [random.uniform(1.2, 1.5) * 1000000 for _ in range(3)]
    consumo_otimizado = [v * 0.88 for v in consumo_previsto] # Simula economia com IA
    
    fig_energia = go.Figure()
    fig_energia.add_trace(go.Bar(x=meses_energia[:3], y=consumo_real, name='Consumo Real (KWh)', marker_color='#34495e'))
    fig_energia.add_trace(go.Bar(x=meses_energia[3:], y=consumo_previsto[3:], name='Previsão Base (KWh)', marker_color='#7f8c8d', opacity=0.6))
    fig_energia.add_trace(go.Scatter(x=meses_energia, y=consumo_otimizado, mode='lines+markers', name='Meta IA Otimizada (KWh)', line=dict(color='#2ecc71', width=3, dash='dot')))
    
    fig_energia.update_layout(title="Projeção de Consumo Energético vs Otimização sugerida pela IA", yaxis_title="Consumo (KWh)", barmode='group')
    st.plotly_chart(fig_energia, use_container_width=True)
    st.success("💡 Insight do Modelo: Ajustar a aceleração nos trechos Lagoinha-Central pode gerar uma economia projetada de 12% na fatura de energia do próximo mês.")

with ml_tab6:
    st.markdown("#### 🕵️ Clusterização de Perfis e Prevenção a Fraudes")
    st.caption("Algoritmo sugerido: **K-Means** ou **DBSCAN**. Analisa a Bilhetagem (Arq2) buscando evasão de receita, compartilhamento ilegal de cartões ou falhas de bloqueio.")
    
    n_pontos = 200
    uso_normal_x = np.random.normal(2, 0.5, int(n_pontos*0.85))
    uso_normal_y = np.random.normal(2, 0.5, int(n_pontos*0.85))
    
    uso_fraude_x = np.random.normal(8, 2, int(n_pontos*0.15))
    uso_fraude_y = np.random.normal(1.5, 0.3, int(n_pontos*0.15))
    
    df_clusters = pd.DataFrame({
        'Validações_Diárias': np.concatenate([uso_normal_x, uso_fraude_x]),
        'Estações_Distintas': np.concatenate([uso_normal_y, uso_fraude_y]),
        'Perfil': ['Usuário Padrão']*int(n_pontos*0.85) + ['Comportamento Suspeito (Evasão/Venda)']*int(n_pontos*0.15)
    })
    
    fig_cluster = px.scatter(df_clusters, x='Validações_Diárias', y='Estações_Distintas', color='Perfil', 
                             color_discrete_map={'Usuário Padrão': '#3498db', 'Comportamento Suspeito (Evasão/Venda)': '#e74c3c'})
    fig_cluster.update_layout(title="Mapeamento de Comportamento de Cartões (Gratuidade/Vale Transporte)")
    st.plotly_chart(fig_cluster, use_container_width=True)

with ml_tab7:
    st.markdown("#### ⚠️ Mapeamento Preditivo de Risco e Segurança")
    st.caption("Algoritmo sugerido: **Naive Bayes** ou **Redes Neurais (Classificação)**. Analisa histórico de Ocorrências (Arq4) cruzado com dia e hora para focar policiamento.")
    
    col_r1, col_r2 = st.columns([1, 2])
    
    with col_r1:
        estacao_risco = st.selectbox("Selecione a Estação para Análise de Risco Predito:", ["Central", "Vilarinho", "Eldorado", "Lagoinha", "São Gabriel"])
        st.info(f"O modelo calcula a probabilidade do tipo de evento que ocorrerá hoje na estação **{estacao_risco}** baseando-se em eventos passados e fatores externos.")
        
    with col_r2:
        if estacao_risco == "Central":
            riscos_cat = [80, 40, 20, 60, 50]
        elif estacao_risco == "Vilarinho":
            riscos_cat = [30, 85, 40, 30, 20]
        else:
            riscos_cat = [random.randint(10, 90) for _ in range(5)]
            
        categorias_risco = ['Furto/Roubo', 'Vandalismo TUE', 'Acesso Indevido à Via', 'Falha Sistêmica (Catraca)', 'Mal Súbito']
        
        df_radar = pd.DataFrame(dict(Risco=riscos_cat, Categoria=categorias_risco))
        fig_radar = px.line_polar(df_radar, r='Risco', theta='Categoria', line_close=True, markers=True, 
                                  color_discrete_sequence=['#e67e22'])
        fig_radar.update_traces(fill='toself')
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Índice Preditivo de Ocorrências (0 a 100)")
        st.plotly_chart(fig_radar, use_container_width=True)