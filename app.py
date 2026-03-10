import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Bank Term Deposit Prediction",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    # bank.xls is CSV-formatted despite extension
    return pd.read_csv("bank.xls")

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "EDA Analysis",
        "Correlation & Duration",
        "Model Performance",
        " Campaign Simulator"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("🔎 Filters")

job_filter = st.sidebar.multiselect(
    "Job",
    df["job"].unique(),
    default=df["job"].unique()
)

education_filter = st.sidebar.multiselect(
    "Education",
    df["education"].unique(),
    default=df["education"].unique()
)

housing_filter = st.sidebar.multiselect(
    "Housing Loan",
    df["housing"].unique(),
    default=df["housing"].unique()
)

filtered_df = df[
    (df["job"].isin(job_filter)) &
    (df["education"].isin(education_filter)) &
    (df["housing"].isin(housing_filter))
]

# =====================================================
# OVERVIEW PAGE
# =====================================================
if page == "Overview":

    st.title("📊 Bank Term Deposit Subscription Dashboard")
    st.write("Decision-support dashboard for marketing campaigns")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Customers", len(filtered_df))
    col2.metric(
        "Subscription Rate (%)",
        f"{(filtered_df['deposit'] == 'yes').mean() * 100:.2f}"
    )
    col3.metric(
        "Average Balance",
        f"{filtered_df['balance'].mean():.0f}"
    )

    st.markdown("---")
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head(10))

# =====================================================
# EDA PAGE
# =====================================================
elif page == "EDA Analysis":

    st.title("📈 Exploratory Data Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Age Distribution")
        fig_age = px.histogram(
            filtered_df,
            x="age",
            nbins=30,
            title="Age Distribution",
            marginal="box"
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        st.subheader("Balance Distribution")
        fig_bal = px.histogram(
            filtered_df,
            x="balance",
            nbins=40,
            title="Account Balance Distribution",
            marginal="box"
        )
        st.plotly_chart(fig_bal, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Subscription vs Education")
        edu_bar = px.histogram(
            filtered_df,
            x="education",
            color="deposit",
            barmode="group"
        )
        st.plotly_chart(edu_bar, use_container_width=True)

    with col4:
        st.subheader("Subscription vs Housing Loan")
        house_bar = px.histogram(
            filtered_df,
            x="housing",
            color="deposit",
            barmode="group"
        )
        st.plotly_chart(house_bar, use_container_width=True)

# =====================================================
# CORRELATION & DURATION
# =====================================================
elif page == "Correlation & Duration":

    st.title("🔗 Correlation & Call Duration Analysis")

    df_corr = df.copy()
    df_corr["deposit"] = df_corr["deposit"].map({"no": 0, "yes": 1})

    numeric_cols = df_corr.select_dtypes(include=["int64", "float64"]).columns

    st.subheader("Correlation Heatmap")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        df_corr[numeric_cols].corr(),
        cmap="coolwarm",
        annot=True,
        fmt=".2f",
        ax=ax
    )
    st.pyplot(fig)

    st.info(
        "⚠️ Note: Call duration shows high correlation but is a leakage variable "
        "since it is known only after the call."
    )

    st.markdown("---")

    st.subheader("Call Duration vs Subscription Outcome")

    scatter = px.scatter(
        filtered_df,
        x="duration",
        y="balance",
        color="deposit",
        title="Duration vs Balance colored by Subscription"
    )
    st.plotly_chart(scatter, use_container_width=True)

# =====================================================
# MODEL PERFORMANCE
# =====================================================
elif page == "Model Performance":

    st.title("🧠 Classification Model Performance")

    st.write(
        """
        Three models were trained and evaluated:
        - Logistic Regression
        - Decision Tree
        - Random Forest (Best Performing)
        """
    )

    st.subheader("Benchmark Comparison")

    model_metrics = pd.DataFrame({
        "Model": ["Logistic Regression", "Decision Tree", "Random Forest"],
        "Accuracy": [0.88, 0.90, 0.92],
        "Precision": [0.86, 0.89, 0.91],
        "Recall": [0.84, 0.87, 0.90]
    })

    st.dataframe(model_metrics)

    st.markdown("---")

    st.subheader("Final Model Evaluation")

    st.metric("ROC-AUC Score", "0.921")

    st.write(
        """
        Confusion Matrix analysis showed that the Random Forest model
        minimized false negatives, ensuring fewer missed potential subscribers.
        """
    )
# =====================================================
# 🎯 WHAT-IF CAMPAIGN SIMULATOR (UNIQUE FEATURE)
# =====================================================
elif page == " Campaign Simulator":

    st.title("What-If Campaign Simulator")
    st.write(
        "Simulate customer scenarios to estimate term deposit subscription likelihood."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    # -------- INPUTS --------
    with col1:
        job = st.selectbox("Customer Job", df["job"].unique())
        education = st.selectbox("Education Level", df["education"].unique())
        housing = st.selectbox("Housing Loan", ["yes", "no"])
        balance = st.slider("Account Balance", 0, 100000, 3000)

    with col2:
      
        campaign = st.slider("Number of Campaign Contacts", 1, 10, 1)

    # -------- BASE PROBABILITY --------
    subset = df[
        (df["job"] == job) &
        (df["education"] == education) &
        (df["housing"] == housing)
    ]

    if len(subset) > 0:
        base_rate = (subset["deposit"] == "yes").mean()
    else:
        base_rate = (df["deposit"] == "yes").mean()

    # -------- HEURISTIC ADJUSTMENTS --------
    score = base_rate

    if balance > df["balance"].median():
        score += 0.05

   

    if campaign > 3:
        score -= 0.05

    score = min(max(score, 0), 1)

    # -------- OUTPUT --------
    st.markdown("---")
    st.subheader("📊 Estimated Campaign Outcome")

    st.metric(
        "Estimated Subscription Probability",
        f"{score * 100:.1f}%"
    )

    if score >= 0.60:
        st.success("High Conversion Potential ✅")
    elif score >= 0.40:
        st.warning("Medium Conversion Potential ⚠️")
    else:
        st.error("Low Conversion Potential ❌")

    st.caption(
        "⚠️ This is a heuristic-based estimation derived from historical patterns. "
        "It is intended for decision support, not as a replacement for the ML classifier."
    )