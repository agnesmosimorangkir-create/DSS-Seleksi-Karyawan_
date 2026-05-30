 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
 
def show_final_recommendation():
 
    st.title("🏆 Final Recommendation")
 
    st.markdown("""
    Halaman ini menggabungkan hasil dari **semua metode DSS** — EV, EOL,
    Uncertainty Analysis, Expected Utility, dan Monte Carlo — untuk menghasilkan
    **rekomendasi final** kandidat terbaik secara komprehensif.
    """)
 
    st.markdown("---")
 
    if "utility" not in st.session_state:
        st.warning("⚠️ Selesaikan seluruh proses DSS terlebih dahulu.")
        return
 
    if "mc_result" not in st.session_state:
        st.warning("⚠️ Jalankan Monte Carlo Simulation terlebih dahulu.")
        return
 
    df        = st.session_state["utility"]
    mc_result = st.session_state["mc_result"]
 
    # Gabungkan semua metrik
    df_final = df[[
        "ID_Kandidat","Nama","Pendidikan","Pengalaman_Tahun",
        "Tes_Teknis","Wawancara","Soft_Skills","Kedisiplinan",
        "EV","EOL","Hurwicz","Expected_Utility"
    ]].copy()
 
    df_final = df_final.merge(
        mc_result[["ID_Kandidat","Persentase"]],
        on="ID_Kandidat", how="left"
    ).fillna(0)
 
    df_final.rename(columns={"Persentase": "WinRate_MC"}, inplace=True)
 
    # Ranking gabungan dari 5 metode
    df_final["Rank_EV"]      = df_final["EV"].rank(ascending=False)
    df_final["Rank_EOL"]     = df_final["EOL"].rank(ascending=True)
    df_final["Rank_Hurwicz"] = df_final["Hurwicz"].rank(ascending=False)
    df_final["Rank_Utility"] = df_final["Expected_Utility"].rank(ascending=False)
    df_final["Rank_MC"]      = df_final["WinRate_MC"].rank(ascending=False)
 
    df_final["Rank_Gabungan"] = (
        df_final["Rank_EV"]      +
        df_final["Rank_EOL"]     +
        df_final["Rank_Hurwicz"] +
        df_final["Rank_Utility"] +
        df_final["Rank_MC"]
    ) / 5
 
    df_final = df_final.sort_values("Rank_Gabungan").reset_index(drop=True)
    df_final.index += 1
 
    def confidence(p):
        if p >= 10:  return "⭐⭐⭐ Sangat Tinggi"
        elif p >= 5: return "⭐⭐ Tinggi"
        elif p >= 2: return "⭐ Sedang"
        else:        return "Rendah"
 
    df_final["Confidence"] = df_final["WinRate_MC"].apply(confidence)
 
    # --- Banner Kandidat #1 ---
    terbaik = df_final.iloc[0]
 
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e3a5f 0%, #2e86ab 100%);
                    padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;'>
            <h2 style='color:white; margin:0;'>🥇 Rekomendasi Utama</h2>
            <h1 style='color:#FFD700; margin:0.3rem 0;'>{terbaik['Nama']}</h1>
            <p style='color:#a8d8ea; margin:0;'>
                {terbaik['ID_Kandidat']} &nbsp;|&nbsp;
                {terbaik['Pendidikan']} &nbsp;|&nbsp;
                Pengalaman: {terbaik['Pengalaman_Tahun']} tahun
            </p>
        </div>
    """, unsafe_allow_html=True)
 
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("EV",        f"{terbaik['EV']:.4f}")
    col2.metric("EOL",       f"{terbaik['EOL']:.4f}")
    col3.metric("Hurwicz",   f"{terbaik['Hurwicz']:.4f}")
    col4.metric("Utility",   f"{terbaik['Expected_Utility']:.4f}")
    col5.metric("Win Rate",  f"{terbaik['WinRate_MC']:.1f}%")
 
    st.markdown(f"**Confidence Level: {terbaik['Confidence']}**")
 
    st.markdown("---")
 
    # --- Top 5 Expander ---
    st.subheader("🏅 Top 5 Rekomendasi")
 
    for i, row in df_final.head(5).iterrows():
        with st.expander(
            f"#{i} — {row['Nama']} ({row['ID_Kandidat']}) "
            f"| Confidence: {row['Confidence']}"
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Pendidikan",  row["Pendidikan"])
            c2.metric("Pengalaman",  f"{row['Pengalaman_Tahun']} tahun")
            c3.metric("Tes Teknis",  row["Tes_Teknis"])
            c4.metric("Wawancara",   row["Wawancara"])
 
            c5, c6, c7, c8, c9 = st.columns(5)
            c5.metric("EV",       f"{row['EV']:.4f}")
            c6.metric("EOL",      f"{row['EOL']:.4f}")
            c7.metric("Hurwicz",  f"{row['Hurwicz']:.4f}")
            c8.metric("Utility",  f"{row['Expected_Utility']:.4f}")
            c9.metric("Win Rate", f"{row['WinRate_MC']:.1f}%")
 
    st.markdown("---")
 
    # --- Rumus Ranking Gabungan ---
    st.subheader("📊 Tabel Ranking Gabungan Semua Metode")
 
    st.code("""
Rank_Gabungan = (Rank_EV + Rank_EOL + Rank_Hurwicz + Rank_Utility + Rank_MC) / 5
 
Semakin kecil Rank_Gabungan → semakin baik kandidat secara keseluruhan
    """, language="text")
 
    st.dataframe(
        df_final[[
            "ID_Kandidat","Nama","Pendidikan",
            "EV","EOL","Hurwicz","Expected_Utility","WinRate_MC",
            "Rank_Gabungan","Confidence"
        ]].head(20).round(4),
        use_container_width=True
    )
 
    st.markdown("---")
 
    # --- Radar Chart Top 3 ---
    st.subheader("🕸️ Profil Top 3 Kandidat (Radar Chart)")
 
    categories = ["Tes Teknis","Wawancara","Soft Skills","Kedisiplinan","Pengalaman","Pendidikan"]
    kolom_data = ["Tes_Teknis","Wawancara","Soft_Skills","Kedisiplinan","Pengalaman_Tahun","Skor_Pendidikan"]
    maks_data  = [100, 100, 100, 100, 10, 4]
    colors     = ["#2196F3","#4CAF50","#FF9800"]
 
    fig_radar = go.Figure()
 
    for i, (_, row) in enumerate(df_final.head(3).iterrows()):
        values = [row[k]/m for k, m in zip(kolom_data, maks_data)]
        values += values[:1]
        cats = categories + [categories[0]]
 
        fig_radar.add_trace(go.Scatterpolar(
            r=values, theta=cats,
            fill="toself", opacity=0.6,
            name=f"#{i+1} {row['Nama'].split()[0]}",
            line_color=colors[i]
        ))
 
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Radar Chart — Profil Top 3 Kandidat",
        showlegend=True
    )
    st.plotly_chart(fig_radar, use_container_width=True)
 
    st.markdown("---")
 
    # --- Grouped Bar Perbandingan Metode ---
    st.subheader("📊 Perbandingan Skor Antar Metode (Top 10)")
 
    top10      = df_final.head(10)
    fig_compare = go.Figure()
 
    for metrik, warna, label in zip(
        ["EV","Hurwicz","Expected_Utility"],
        ["#2196F3","#FF9800","#4CAF50"],
        ["Expected Value","Hurwicz","Expected Utility"]
    ):
        fig_compare.add_trace(go.Bar(
            name=label,
            x=[n.split()[0] for n in top10["Nama"]],
            y=top10[metrik],
            marker_color=warna,
            opacity=0.85
        ))
 
    fig_compare.update_layout(
        barmode="group",
        title="Perbandingan EV, Hurwicz, Utility — Top 10 Kandidat",
        xaxis_title="Kandidat",
        yaxis_title="Skor",
        legend_title="Metode"
    )
    st.plotly_chart(fig_compare, use_container_width=True)
 
    st.markdown("---")
 
    st.success(f"""
    ✅ **Kesimpulan:** Berdasarkan analisis komprehensif menggunakan 5 metode DSS
    (EV, EOL, Uncertainty, Utility, Monte Carlo), kandidat yang paling direkomendasikan
    adalah **{terbaik['Nama']}** dengan Rank Gabungan terbaik dan
    Confidence Level **{terbaik['Confidence']}**.
    """)
 
    st.caption(
        "Sistem Pendukung Keputusan Seleksi Karyawan  |  "
        "Agnes Monica Simorangkir  |  NIM: 4233260018"
    )
