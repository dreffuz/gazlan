import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# in Tools -> Open system shell:
# streamlit run GazLan26_SL.py

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GazLan26", page_icon="🎲", layout="centered")

# --- LOGICA DATI ---
punt = {1:6, 2:4, 3:2, 4:1}
SHEET_ID = '1lax0ZUNUFCp5uwxxAlVo98-lw0Eelpv48H7N2MHBd4w'
SHEET_NAME = 'dat'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

@st.cache_data(ttl=600) # Carica i dati grezzi e li tiene in memoria per 10 minuti
def fetch_raw_data():
    data = pd.read_csv(url)
    data['Punteggio'] = data['posiz'].map(punt)
    data['vittorie'] = data['posiz'].eq(1).astype(int)
    data['Data'] = pd.to_datetime(data['Data'], format='%d/%m/%y')
    return data

try:
    # 1. Carichiamo i dati grezzi completi
    df_org = fetch_raw_data()
    data_max = df_org['Data'].max()

    # --- INTERFACCIA ---
    # Usiamo HTML a riga singola (senza indentazione) per ridurre la dimensione del titolo e del sottotitolo in modo sicuro
    st.markdown('<h1 style="font-size: 30px; font-weight: 700; margin-bottom: 5px; padding-bottom: 0px;">🏆 Campionato Ludico GazLan26</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size: 18px; color: #555; margin-top: 0px; margin-bottom: 25px;">Classifica aggiornata al {data_max.strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

    # --- DATI RIEPILOGO GENERALE (Sempre riferiti a TUTTI i giochi) ---
    giornate_gioco = df_org['Data'].nunique()
    totale_partite = df_org['Progr Partita'].nunique()
    giochi_diversi = df_org['Gioco'].nunique()

    # Mostriamo i contatori generali affiancati usando i widget metric di Streamlit
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Giornate di gioco", value=giornate_gioco)
    m2.metric(label="Totale partite", value=totale_partite)
    m3.metric(label="Giochi diversi", value=giochi_diversi)
    
    st.write("---") # Una linea di separazione prima del filtro e dei grafici

    # --- FILTRO GIOCO (LISTA A DISCESA CON CONTEGGIO PARTITE) ---
    totale_partite_generale = df_org['Progr Partita'].nunique()
    conteggio_giochi = df_org.groupby('Gioco')['Progr Partita'].nunique().to_dict()
    giochi_unici = sorted(df_org['Gioco'].dropna().unique())
    
    mappa_opzioni = {f"Tutti ({totale_partite_generale} partite)": "Tutti"}
    
    for gioco in giochi_unici:
        num_partite = conteggio_giochi.get(gioco, 0)
        testo_partita = "partita" if num_partite == 1 else "partite"
        etichetta_estesa = f"{gioco} ({num_partite} {testo_partita})"
        mappa_opzioni[etichetta_estesa] = gioco

    opzione_scelta_estesa = st.selectbox("Seleziona il gioco", options=list(mappa_opzioni.keys()))
    gioco_selezionato = mappa_opzioni[opzione_scelta_estesa]

    # --- FILTRAGGIO DATI ---
    if gioco_selezionato == 'Tutti':
        df_filtrato = df_org
    else:
        df_filtrato = df_org[df_org['Gioco'] == gioco_selezionato]

    # 3. Calcoliamo la somma e le vittorie SOLO sui dati filtrati
    df_somma = df_filtrato.groupby('Giocatore').agg({
        'Punteggio': 'sum',
        'vittorie': 'sum'
    }).reset_index()
    
    df_somma = df_somma.sort_values('Punteggio', ascending=False)
    
    # Rinominiamo la colonna "vittorie" con la V maiuscola per l'estetica della tabella
    df_tabella = df_somma.rename(columns={'vittorie': 'Vittorie'})

    # --- TABELLA (Ripristinata con st.dataframe nativo di Streamlit) ---
    st.dataframe(
        df_tabella,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Giocatore": st.column_config.TextColumn("Giocatore"),
            "Punteggio": st.column_config.NumberColumn("Punteggio", alignment="center"),
            "Vittorie": st.column_config.NumberColumn("Vittorie", alignment="center")
        }
    )

    # --- GRAFICI ---
    st.write("### Statistiche")
    
    col1, col2 = st.columns(2)
    colors = ['#4CAF50', '#FF9800', '#2196F3', '#E91E63']

    with col1:
        # Grafico a barre (Orizzontale)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.barh(df_somma['Giocatore'], df_somma['Punteggio'], color=colors)
        
        # Etichette del punteggio dentro le barre con font più grande (da 12 a 14)
        for i, v in enumerate(df_somma['Punteggio']):
            ax.text(v * 0.95, i, str(v), color='white', fontweight='bold', 
                    ha='right', va='center', fontsize=14)
                    
        ax.invert_yaxis()
        
        # Titolo del grafico più grande (da 14 a 18) e in grassetto
        ax.set_title('Punteggio Totale', fontsize=18, fontweight='bold', pad=15)
        
        # Etichette dei giocatori sulla sinistra più grandi (labelsize=14)
        ax.tick_params(axis='y', labelsize=14)
        ax.set_xticks([])
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        st.pyplot(fig)

    with col2:
        # Grafico a torta
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        
        # Filtriamo df_somma per tenere solo chi ha effettivamente vinto almeno una volta (> 0)
        df_torta = df_somma[df_somma['vittorie'] > 0]
        
        if not df_torta.empty:
            colori_filtrati = [colors[i % len(colors)] for i in df_torta.index]
            
            # Disegna la torta con etichette dei giocatori e valori reali più grandi (fontsize: 14)
            ax2.pie(
                df_torta['vittorie'], 
                labels=df_torta['Giocatore'], 
                autopct=lambda pct: f"{int(round(pct * df_torta['vittorie'].sum() / 100.0))}", 
                colors=colori_filtrati, 
                textprops={'fontsize': 14}
            )
        else:
            ax2.text(0.5, 0.5, "Nessuna vittoria\nregistrata", 
                     ha='center', va='center', fontsize=16, color='gray')
            ax2.axis('off')
            
        # Titolo della torta più grande (da 14 a 18) e in grassetto
        ax2.set_title('Vittorie', fontsize=18, fontweight='bold', pad=15)
        st.pyplot(fig2)

    # Bottone extra per aggiornare
    if st.button("🔄 Aggiorna Dati"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"Errore nel caricamento: {e}")
    st.info("Assicurati che il foglio Google sia condiviso con 'Chiunque abbia il link'.")
