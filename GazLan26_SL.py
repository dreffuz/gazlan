import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GazLan26", page_icon="🎲", layout="centered")

# --- LOGICA DATI (Uguale alla tua) ---
punt = {1:6, 2:4, 3:3, 4:2}
SHEET_ID = '1lax0ZUNUFCp5uwxxAlVo98-lw0Eelpv48H7N2MHBd4w'
SHEET_NAME = 'dat'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

@st.cache_data(ttl=600) # Carica i dati e li tiene in memoria per 10 minuti
def fetch_data():
    data = pd.read_csv(url)
    data['Punteggio'] = data['posiz'].map(punt)
    data['vittorie'] = data['posiz'].eq(1).astype(int)
    
    somma = data.groupby('Giocatore').agg({
        'Punteggio': 'sum',
        'vittorie': 'sum'
    }).reset_index()
    
    somma = somma.sort_values('Punteggio', ascending=False)
    return data, somma

try:
    df_originale, df_somma = fetch_data()
    data_max = df_originale['Data'].max()

    # --- INTERFACCIA ---
    st.title("🏆 Campionato Ludico GazLan26")
    st.subheader(f"Classifica aggiornata al {data_max}")

    # --- TABELLA (Sostituisce Treeview) ---
    # Streamlit formatta automaticamente la tabella in modo professionale
    st.dataframe(df_somma, use_container_width=True, hide_index=True)

    # --- GRAFICI (Sostituisce FigureCanvasTkAgg) ---
    st.write("### Statistiche")
    
    # Creiamo due colonne per i grafici (come avevi fatto con i frame)
    col1, col2 = st.columns(2)

    colors = ['#4CAF50', '#FF9800', '#2196F3', '#E91E63']

    with col1:
        # Grafico a barre (Orizzontale come il tuo)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.barh(df_somma['Giocatore'], df_somma['Punteggio'], color=colors)
        for i, v in enumerate(df_somma['Punteggio']):
            ax.text(v * 0.95, i, str(v), color='white', fontweight='bold', 
                    ha='right', va='center', fontsize=12)
        ax.invert_yaxis()
        ax.set_title('Punteggio Totale', fontsize=14)
        ax.set_xticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        st.pyplot(fig)

    with col2:
        # Grafico a torta
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        ax2.pie(df_somma['vittorie'], labels=df_somma['Giocatore'], 
                autopct='%1.0f%%', colors=colors, textprops={'fontsize': 10})
        ax2.set_title('Vittorie', fontsize=14)
        st.pyplot(fig2)

    # Bottone extra per aggiornare
    if st.button("🔄 Aggiorna Dati"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"Errore nel caricamento: {e}")
    st.info("Assicurati che il foglio Google sia condiviso con 'Chiunque abbia il link'.") 