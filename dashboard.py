import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

st.set_page_config(page_title="Dashboard Bancaire", layout="wide")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Si vous avez un fichier CSS, décommentez la ligne ci-dessous
# local_css("style/main.css")


@st.cache_data
def load_data():
    """
    Charge les données depuis la base de données PostgreSQL.
    """
    engine = create_engine("postgresql://asja:asjauniversity@localhost:5432/asjadb")

    # Charger les données principales
    data = pd.read_sql("SELECT * FROM data", engine)

    # Charger les données agrégées
    number_accounts_by_branch = pd.read_sql('SELECT * FROM "numberAccountsByBranch"', engine)
    total_balance_by_branch = pd.read_sql('SELECT * FROM "totalBalanceByBranch"', engine)
    average_balance_by_product = pd.read_sql('SELECT * FROM "averageBalanceByProduct"', engine)
    average_account_by_product = pd.read_sql('SELECT * FROM "averageAccountByProduct"', engine)
    top_gestionnaires = pd.read_sql('SELECT * FROM "topGestionnaires"', engine)
    average_age_by_branch = pd.read_sql('SELECT * FROM "averageAgeByBranch"', engine)
    average_age_by_manager = pd.read_sql('SELECT * FROM "averageAgeByManager"', engine)

    return (
        data,
        number_accounts_by_branch,
        total_balance_by_branch,
        average_balance_by_product,
        average_account_by_product,
        top_gestionnaires,
        average_age_by_branch,
        average_age_by_manager,
    )


# Charger les données
(
    data,
    nb_accounts_branch,
    total_balance_branch,
    avg_balance_product,
    avg_account_product,
    top_managers,
    avg_age_branch,
    avg_age_manager,
) = load_data()

# Calculer les KPI globaux
total_encours = data["AvailableBalance"].sum()
total_accounts = len(data)
active_accounts = (data["AccountStatus"] == "Active").sum()
avg_account_balance = total_encours / total_accounts if total_accounts > 0 else 0
avg_account_age = data["AccountAgeYears"].mean()

st.title("Dashboard d'Analyse Bancaire")
st.markdown("### Surveillance des comptes clients, performances et répartitions")

# Section KPI
st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Encours Total",
        value=f"{total_encours:,.0f} €",
        delta=f"{avg_account_balance:,.0f} €/compte",
    )

with col2:
    st.metric(
        label="Nombre Total de Comptes",
        value=f"{total_accounts:,}",
        delta=f"{active_accounts:,} actifs",
    )

with col3:
    st.metric(label="Âge Moyen des Comptes", value=f"{avg_account_age:.1f} ans")

with col4:
    concentration = (
        (top_managers["TotalBalance"].head(10).sum() / total_encours * 100)
        if total_encours > 0
        else 0
    )
    st.metric(label="Concentration Top 10 Gestionnaires", value=f"{concentration:.1f}%")

st.markdown("</div>", unsafe_allow_html=True)

# Graphiques principaux
col_left, col_right = st.columns([2, 1])

with col_left:
    # 1. Répartition des encours par agence
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Répartition des Encours par Agence")

    # Fusionner les données d'agence
    branch_data = pd.merge(nb_accounts_branch, total_balance_branch, on="Branch", how="left")

    if not branch_data.empty:
        fig_branch = make_subplots(specs=[[{"secondary_y": True}]])

        fig_branch.add_trace(
            go.Bar(
                x=branch_data["Branch"],
                y=branch_data["TotalAvailableBalance"],
                name="Encours Total (€)",
                marker_color=px.colors.qualitative.Set2[0],
                hovertemplate="<b>%{x}</b><br>Encours: %{y:,.0f} €<extra></extra>",
            ),
            secondary_y=False,
        )

        fig_branch.add_trace(
            go.Scatter(
                x=branch_data["Branch"],
                y=branch_data["noCompte"],
                name="Nombre de Comptes",
                mode="lines+markers",
                line=dict(color=px.colors.qualitative.Set2[1], width=3),
                hovertemplate="<b>%{x}</b><br>Comptes: %{y}<extra></extra>",
            ),
            secondary_y=True,
        )

        fig_branch.update_layout(
            template="plotly_white",
            height=400,
            xaxis_title="Agence",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )

        fig_branch.update_yaxes(title_text="Encours (€)", secondary_y=False, tickformat=",.0f")
        fig_branch.update_yaxes(title_text="Nombre de Comptes", secondary_y=True)

        st.plotly_chart(fig_branch, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour les agences.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Top 10 des gestionnaires
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Top 10 des Gestionnaires par Encours")

    if not top_managers.empty:
        # Trier et limiter à top 10
        top_10 = top_managers.sort_values("TotalBalance", ascending=False).head(10)

        fig_top_managers = px.bar(
            top_10,
            x="gestionnaire de compte",
            y="TotalBalance",
            color="TotalBalance",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={"TotalBalance": "Encours Géré (€)", "gestionnaire de compte": "Gestionnaire"},
            text_auto=",.0f",  # type: ignore
        )

        fig_top_managers.update_layout(
            template="plotly_white",
            height=400,
            xaxis_tickangle=-45,
            coloraxis_showscale=False,
            yaxis_tickformat=",.0f",
        )

        fig_top_managers.update_traces(
            hovertemplate="<b>%{x}</b><br>Encours: %{y:,.0f} €<extra></extra>",
            textposition="outside",
        )

        st.plotly_chart(fig_top_managers, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour les gestionnaires.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # 3. Répartition par type de produit (CORRIGÉ - utilisation du nombre de comptes)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Répartition par Produit")

    if not avg_balance_product.empty and not avg_account_product.empty:
        # Fusionner les données de produit
        product_data = pd.merge(
            avg_balance_product, avg_account_product, on=["ProductCode", "Product"], how="left"
        )

        # Calculer le pourcentage pour chaque produit
        product_data["Pourcentage"] = (
            product_data["Compte"] / product_data["Compte"].sum() * 100
        ).round(1)

        # Trier par nombre de comptes (descendant)
        product_data = product_data.sort_values("Compte", ascending=False)

        # Créer un graphique en barres pour le nombre de comptes
        fig_product = px.bar(
            product_data,
            x="Product",
            y="Compte",
            color="Pourcentage",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={
                "Product": "Type de Produit",
                "Compte": "Nombre de Comptes",
                "Pourcentage": "Part (%)",
            },
            text=[
                f"{row['Compte']:,} ({row['Pourcentage']}%)" for _, row in product_data.iterrows()
            ],
            hover_data={
                "Product": True,
                "Compte": True,
                "Pourcentage": True,
                "AverageAvailableBalance": ":,.0f €",
            },
        )

        fig_product.update_layout(
            template="plotly_white",
            height=400,
            xaxis_title="Type de Produit",
            yaxis_title="Nombre de Comptes",
            xaxis_tickangle=-45,
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(title="Part (%)", thickness=20, len=0.75),
            hovermode="x unified",
        )

        fig_product.update_traces(
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Nombre de comptes: %{y:,}<br>Part: %{customdata[0]}%<br>Solde moyen: %{customdata[1]:,.0f} €<extra></extra>",
        )

        fig_product.update_yaxes(tickformat=",")

        st.plotly_chart(fig_product, use_container_width=True)

        # Afficher un tableau récapitulatif avec meilleure mise en forme
        with st.expander("Détails par produit"):
            product_summary = product_data.copy()
            product_summary = product_summary[
                ["Product", "Compte", "Pourcentage", "AverageAvailableBalance"]
            ]

            # Formater les valeurs
            product_summary["Compte"] = product_summary["Compte"].apply(lambda x: f"{x:,}")
            product_summary["Pourcentage"] = product_summary["Pourcentage"].apply(
                lambda x: f"{x:.1f}%"
            )
            product_summary["AverageAvailableBalance"] = product_summary[
                "AverageAvailableBalance"
            ].apply(lambda x: f"{x:,.0f} €" if pd.notnull(x) else "N/A")

            st.dataframe(
                product_summary,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Product": "Produit",
                    "Compte": "Nombre de Comptes",
                    "Pourcentage": "Part (%)",
                    "AverageAvailableBalance": "Solde Moyen",
                },
            )

            # Afficher quelques statistiques
            total_comptes = product_data["Compte"].sum()
            st.caption(f"Total des comptes: {total_comptes:,}")
    else:
        st.info("Aucune donnée disponible pour les produits.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Âge moyen des comptes par gestionnaire
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Âge Moyen des Comptes par Gestionnaire")

    if not avg_age_manager.empty:
        # Fusionner avec les données d'encours
        manager_age_data = (
            pd.merge(avg_age_manager, top_managers, on="gestionnaire de compte", how="inner")
            .sort_values("TotalBalance", ascending=False)
            .head(10)
        )

        fig_age_manager = go.Figure()

        fig_age_manager.add_trace(
            go.Scatter(
                x=manager_age_data["gestionnaire de compte"],
                y=manager_age_data["AverageAccountAgeYears"],
                mode="markers+text",
                marker=dict(
                    size=manager_age_data["TotalBalance"]
                    / manager_age_data["TotalBalance"].max()
                    * 50
                    + 10,
                    color=manager_age_data["TotalBalance"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Encours (€)"),
                ),
                text=[f"{age:.1f} ans" for age in manager_age_data["AverageAccountAgeYears"]],
                textposition="top center",
                hovertemplate="<b>%{x}</b><br>Âge moyen: %{y:.1f} ans<br>Encours: %{marker.color:,.0f} €<extra></extra>",
            )
        )

        fig_age_manager.update_layout(
            template="plotly_white",
            height=400,
            xaxis_title="Gestionnaire",
            yaxis_title="Âge Moyen (années)",
            xaxis_tickangle=-45,
        )

        st.plotly_chart(fig_age_manager, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour l'âge des comptes.")
    st.markdown("</div>", unsafe_allow_html=True)

# Tableau de données détaillées
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(" Données Détail des Comptes")

# Filtres
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    branches = ["Toutes"] + sorted(data["Branch"].dropna().unique().tolist())
    selected_branch = st.selectbox("Filtrer par agence:", branches)

with col_filter2:
    products = ["Tous"] + sorted(data["Product"].dropna().unique().tolist())
    selected_product = st.selectbox("Filtrer par produit:", products)

with col_filter3:
    min_balance, max_balance = (
        int(data["AvailableBalance"].min()),
        int(data["AvailableBalance"].max()),
    )
    balance_range = st.slider(
        "Filtrer par solde (€):",
        min_balance,
        max_balance,
        (min_balance, max_balance),
        format="%d €",
    )

# Appliquer les filtres
filtered_data = data.copy()

if selected_branch != "Toutes":
    filtered_data = filtered_data[filtered_data["Branch"] == selected_branch]

if selected_product != "Tous":
    filtered_data = filtered_data[filtered_data["Product"] == selected_product]

filtered_data = filtered_data[
    (filtered_data["AvailableBalance"] >= balance_range[0])
    & (filtered_data["AvailableBalance"] <= balance_range[1])
]

# Afficher les statistiques filtrées
st.caption(
    f"{len(filtered_data)} comptes trouvés | Encours total: {filtered_data['AvailableBalance'].sum():,.0f} €"
)

# Afficher le tableau
display_cols = [
    "noCompte",
    "Branch",
    "Product",
    "gestionnaire de compte",
    "AvailableBalance",
    "AccountAgeYears",
    "OpeningDate",
]

display_data = filtered_data[display_cols].copy()
display_data["AvailableBalance"] = display_data["AvailableBalance"].map("{:,.0f} €".format)
display_data["AccountAgeYears"] = display_data["AccountAgeYears"].map("{:.1f} ans".format)
display_data["OpeningDate"] = pd.to_datetime(display_data["OpeningDate"]).dt.strftime("%d/%m/%Y")

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "noCompte": "Numéro Compte",
        "Branch": "Agence",
        "Product": "Produit",
        "gestionnaire de compte": "Gestionnaire",
        "AvailableBalance": "Solde Disponible",
        "AccountAgeYears": "Âge du Compte",
        "OpeningDate": "Date d'Ouverture",
    },
)

# Bouton de téléchargement
csv_data = filtered_data[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    label=" Télécharger les données filtrées (CSV)",
    data=csv_data,
    file_name=f"donnees_bancaires_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
)

st.markdown("</div>", unsafe_allow_html=True)

# Pied de page
st.markdown("---")
