import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# === Load dataset ===
df = pd.read_csv("heart_disease.csv")

# === Replace Age with Age Group Labels ===
age_map = {
    1: "18–24", 2: "25–29", 3: "30–34", 4: "35–39", 5: "40–44",
    6: "45–49", 7: "50–54", 8: "55–59", 9: "60–64", 10: "65–69",
    11: "70–74", 12: "75–79", 13: "80+"
}
df["Age"] = df["Age"].map(age_map)

# === Map binary columns to meaningful labels for plotting ===
df['Smoker_Label'] = df['Smoker'].map({0: 'No', 1: 'Yes'})
df['HighBP_Label'] = df['HighBP'].map({0: 'No', 1: 'Yes'})
df['CholCheck_Label'] = df['CholCheck'].map({0: 'No', 1: 'Yes'})
df['PhysActivity_Label'] = df['PhysActivity'].map({0: 'No', 1: 'Yes'})
df['Fruits_Label'] = df['Fruits'].map({0: 'No', 1: 'Yes'})

# === Map HeartDiseaseorAttack to meaningful labels for legend ===
df['HeartDiseaseorAttack_Label'] = df['HeartDiseaseorAttack'].map({0: 'No Heart Disease', 1: 'Heart Disease'})

# === Page config ===
st.set_page_config(page_title="Heart Disease Dashboard", layout="wide")

# === Password Protection ===
def check_password():
    def password_entered():
        if st.session_state["password"] == "Heart123":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.text_input("🔒 Enter Password", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# === CSS Styles ===
st.markdown("""
    <style>
    body { background-color: #1e1e1e; color: white; }
     .metric-card {
        background-color: #cccccc;
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-title {color: #1a1a1a; font-weight: bold; font-size: 24px; }
    .metric-value { font-size: 32px; font-weight: 700; color: #e63946; }
    .heart {
        animation: beat 1s infinite;
        transform-origin: center;
        display: inline-block;
        color: #e63946;
        font-size: 90px; /* Adjusted for sidebar */
    }
    @keyframes beat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.3); }
    }
    </style>
""", unsafe_allow_html=True)

# === Chart Helper ===
def make_plot(fig):
    fig.patch.set_facecolor('#1e1e1e')
    for ax in fig.axes:
        ax.set_facecolor('#1e1e1e')
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_color("white")
        
        # --- FIX FOR LEGEND TITLE COLOR ---
        if ax.get_legend():
            legend_title = ax.get_legend().get_title()
            if legend_title:
                legend_title.set_color("white") # Correct way to set title color
            # Set the color of legend labels (entries)
            for text in ax.get_legend().get_texts():
                text.set_color("white")
        # --- END FIX ---

        ax.title.set_color("white")
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
    st.pyplot(fig)
    plt.close(fig) # Close the figure to free up memory

# === Sidebar with Filters and Navigation ===
with st.sidebar:
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
            <div class="heart">❤️</div>
        </div>
    """, unsafe_allow_html=True)

    st.header("🔍 Filters")

    sex_map = {0: "Female", 1: "Male"}
    sex_options = ["All"] + list(sex_map.keys())
    selected_sex = st.selectbox("Gender", options=sex_options, format_func=lambda x: sex_map.get(x, "All"))

    smoker_options = ["All", "Yes", "No"]
    smoker_choice = st.sidebar.selectbox("Smoker", options=smoker_options) # Added st.sidebar

    diabetes_map = {0: "No", 1: "Yes", 2: "Borderline", 3: "Unknown"}
    diabetes_options = ["All"] + list(diabetes_map.keys())
    selected_diabetes = st.selectbox("Diabetic Status", options=diabetes_options, format_func=lambda x: diabetes_map.get(x, "All"))

    genhlth_map = {1: "Excellent", 2: "Very Good", 3: "Good", 4: "Fair", 5: "Poor"}
    genhlth_options = ["All"] + list(genhlth_map.keys())
    selected_genhlth = st.selectbox("General Health Rating", options=genhlth_options, format_func=lambda x: genhlth_map.get(x, "All"))

    # Navigation for pages
    st.markdown("---")
    page_selection = st.radio("Navigate", ["Dashboard", "Detailed Visuals"])

# === Filtering Logic ===
filtered_df = df.copy()
if selected_sex != "All":
    filtered_df = filtered_df[filtered_df["Sex"] == selected_sex]
if smoker_choice != "All":
    filtered_df = filtered_df[filtered_df["Smoker_Label"] == smoker_choice]
if selected_diabetes != "All":
    filtered_df = filtered_df[filtered_df["Diabetes"] == selected_diabetes]
if selected_genhlth != "All":
    filtered_df = filtered_df[filtered_df["GenHlth"] == selected_genhlth]

# === Page Content ===
if page_selection == "Dashboard":
    # === Title with ECG ===
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center;">
            <svg width="100%" height="80" viewBox="0 0 1200 80" xmlns="http://www.w3.org/2000/svg">
                <polyline fill="none" stroke="#e63946" stroke-width="4"
                    points="0,40 50,40 70,20 90,60 110,40 200,40 220,40 240,20 260,60 280,40 400,40 420,20 440,60 460,40 1200,40">
                    <animate attributeName="points" dur="2s" repeatCount="indefinite"
                        values="0,40 50,40 70,20 90,60 110,40 200,40 220,40 240,20 260,60 280,40 400,40 420,20 440,60 460,40 1200,40;
                                0,40 30,40 50,20 70,60 90,40 180,40 200,40 220,20 240,60 260,40 380,40 400,20 420,60 440,40 1200,40;
                                0,40 50,40 70,20 90,60 110,40 200,40 220,40 240,20 260,60 280,40 400,40 420,20 440,60 460,40 1200,40"/>
                </polyline>
            </svg>
            <h1 style='text-align: center; font-size: 48px; font-family: "Segoe UI", sans-serif; color: #e63946; margin-top: -10px;'>
                Heart Disease Dashboard
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # === Metric Cards ===
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Records</div><div class='metric-value'>{len(filtered_df):,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Heart Disease Cases</div><div class='metric-value'>{int(filtered_df['HeartDiseaseorAttack'].sum()):,}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Heart Disease Rate</div><div class='metric-value'>{filtered_df['HeartDiseaseorAttack'].mean() * 100:.2f}%</div></div>", unsafe_allow_html=True)

    # === Chart Rows (First 3 charts) ===
    charts_page1 = [
        ("📈 Heart Disease by Age",
            lambda ax: (
                # Use 'HeartDiseaseorAttack_Label' for hue
                sns.countplot(data=filtered_df, x="Age", hue="HeartDiseaseorAttack_Label", ax=ax, palette="Reds", order=age_map.values()),
                ax.set_xlabel("Age Group", color="white"),
                ax.set_ylabel("Count", color="white"),
                ax.tick_params(axis='x', labelrotation=90, labelcolor='white'),
                ax.tick_params(axis='y', labelcolor='white'),
                # Removed direct set_title with color here. make_plot handles it.
                ax.legend(title='Heart Disease Status') # Keep the title set here for the legend object
        )),
        ("🧑‍🤝‍🧑 Gender Distribution",
            lambda ax: (
                ax.pie(
                    filtered_df["Sex"].value_counts(),
                    labels=[sex_map[i] for i in filtered_df["Sex"].value_counts().index],
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=["#e63946", "#555"]
                )
        )),
        ("⚖️ BMI Distribution", lambda ax: sns.histplot(filtered_df["BMI"], bins=30, kde=True, color="#e63946", ax=ax)),
    ]

    for i in range(0, len(charts_page1), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(charts_page1):
                with cols[j]:
                    st.subheader(charts_page1[i+j][0])
                    fig, ax = plt.subplots(figsize=(8, 6)) # Adjust figure size for better display
                    charts_page1[i+j][1](ax)
                    make_plot(fig)

    # === Raw Data Table ===
    with st.expander("📄 Show Raw Data"):
        st.dataframe(filtered_df)

elif page_selection == "Detailed Visuals":
    st.markdown("""
        <h1 style='text-align: center; font-size: 48px; font-family: "Segoe UI", sans-serif; color: #e63946;'>
            Detailed Visuals
        </h1>
    """, unsafe_allow_html=True)

    # === Additional 6 Visuals on a new page ===
    charts_page2 = [
        ("📌 Correlation Matrix", lambda ax: sns.heatmap(filtered_df.corr(numeric_only=True), cmap="Reds", ax=ax)),
        ("🚬 Smoking vs Heart Disease", lambda ax: sns.countplot(data=filtered_df, x="Smoker_Label", hue="HeartDiseaseorAttack_Label", palette="dark:red", ax=ax)), # Use mapped column for hue
        ("💊 High Blood Pressure", lambda ax: sns.countplot(data=filtered_df, x="HighBP_Label", hue="HeartDiseaseorAttack_Label", ax=ax, palette="Reds")), # Use mapped column for hue
        ("⚠️ Cholesterol Level", lambda ax: sns.countplot(data=filtered_df, x="CholCheck_Label", hue="HeartDiseaseorAttack_Label", ax=ax, palette="Reds")), # Use mapped column for hue
        ("🏃 Physical Activity", lambda ax: sns.countplot(data=filtered_df, x="PhysActivity_Label", hue="HeartDiseaseorAttack_Label", ax=ax, palette="Reds")), # Use mapped column for hue
        ("🍔 Fruit Consumption", lambda ax: sns.countplot(data=filtered_df, x="Fruits_Label", hue="HeartDiseaseorAttack_Label", ax=ax, palette="Reds")), # Use mapped column for hue
    ]

    for i in range(0, len(charts_page2), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(charts_page2):
                with cols[j]:
                    st.subheader(charts_page2[i+j][0])
                    fig, ax = plt.subplots(figsize=(8, 6)) # Adjust figure size for better display
                    charts_page2[i+j][1](ax)
                    make_plot(fig)