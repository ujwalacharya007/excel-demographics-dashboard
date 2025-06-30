import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set up the page
st.set_page_config(page_title="Excel Data Visualization Dashboard", page_icon="📊")
st.title("📊 Excel-Based Demographic Visualization")

st.markdown("""
Upload an Excel file extracted from OCR data. This app will help visualize key demographics like:
- 🧑‍🤝‍🧑 Age Group Distribution
- 🚻 Gender Breakdown (choose chart type)
- 🏷️ Caste Composition (select number of top castes)
""")

# Upload Excel file
uploaded_file = st.file_uploader("📤 Upload Excel File (e.g., from 'rupandehi-3.xlsx')", type=["xlsx"])

def convert_to_nepali_number(num):
    eng = '0123456789'
    nep = '०१२३४५६७८९'
    return ''.join(nep[eng.index(ch)] if ch in eng else ch for ch in str(num))

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean caste column
    df['जाति'] = df['जाति'].astype(str).str.strip().replace({
        'गुरुङ्ग': 'गुरुङ', 'गुरूङ्ग': 'गुरुङ', 'गुरूङ': 'गुरुङ'
    })

    # ---- AGE GROUP PIE CHART ----
    def categorize_age(age):
        if age < 20:
            return '<20'
        elif age <= 35:
            return '21–35'
        elif age <= 50:
            return '36–50'
        else:
            return '51+'

    df['Age Group'] = df['उमेर'].apply(categorize_age)
    age_labels_nepali = {
        '<20': '२० वर्ष मुनि', '21–35': '२१ देखि ३५ वर्ष',
        '36–50': '३६ देखि ५० वर्ष', '51+': '५१ वर्ष माथि'
    }
    order = ['<20', '21–35', '36–50', '51+']
    age_counts = df['Age Group'].value_counts().reindex(order, fill_value=0)

    if st.checkbox("📈 Show Age Group Pie Chart"):
        labels = [age_labels_nepali[label] for label in order]
        hover_labels = [
            f"{age_labels_nepali[label]}<br>({convert_to_nepali_number(count)} जनसंख्या)"
            for label, count in zip(order, age_counts.values)
        ]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=age_counts.values,
            hovertext=hover_labels,
            hoverinfo="text",
            textinfo='percent+label',
            textfont=dict(family="Nirmala UI, Mangal, Arial", size=14)
        )])
        fig.update_layout(title="उमेर समूह वितरण")
        st.plotly_chart(fig, use_container_width=True)

    # ---- GENDER CHART (Dynamic) ----
    if st.checkbox("🧭 Show Gender Distribution"):
        gender_chart_type = st.radio("Select Gender Chart Type", ["Pie Chart", "Bar Chart"], horizontal=True)
        gender_counts = df['लिङ्ग'].value_counts()
        labels = gender_counts.index.tolist()
        values = gender_counts.values.tolist()
        percentages = [round(v / sum(values) * 100, 1) for v in values]

        display_labels = [
            f"{label}<br>{convert_to_nepali_number(val)} ({p}%)"
            for label, val, p in zip(labels, values, percentages)
        ]

        if gender_chart_type == "Pie Chart":
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                text=display_labels,
                hoverinfo='text',
                textinfo='text',
                marker=dict(colors=['#66B3FF', '#FF9999']),
                textfont=dict(family="Nirmala UI, Mangal, Arial", size=14)
            )])
            fig.update_layout(title="लिङ्ग वितरण")
            st.plotly_chart(fig, use_container_width=True)

        elif gender_chart_type == "Bar Chart":
            fig = go.Figure(data=[go.Bar(
                x=labels,
                y=values,
                text=display_labels,
                textposition='auto',
                marker_color=['#FF9999', '#66B3FF']
            )])
            fig.update_layout(
                title="लिङ्ग वितरण",
                xaxis_title="लिङ्ग",
                yaxis_title="जनसंख्या",
                font=dict(family="Nirmala UI, Mangal, Arial", size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---- CASTE BAR CHART ----
    if st.checkbox("🏷️ Show Castes by Gender"):
        top_n = st.slider("Select number of top castes to display:", min_value=5, max_value=50, value=10)
        top_castes = df['जाति'].value_counts().head(top_n).index.tolist()
        filtered = df[df['जाति'].isin(top_castes)]
        grouped = filtered.groupby(['जाति', 'लिङ्ग']).size().unstack(fill_value=0)

        fig = go.Figure()
        for gender in grouped.columns:
            fig.add_bar(
                name=gender,
                x=grouped.index,
                y=grouped[gender],
                text=grouped[gender],
                hovertemplate='जाति: %{x}<br>लिङ्ग: ' + gender + '<br>जनसंख्या: %{y}<extra></extra>'
            )

        fig.update_layout(
            barmode='stack',
            title=f'शीर्ष {top_n} जातिहरुमा लिङ्ग अनुसार स्तरीकृत बार चार्ट',
            xaxis_title='जाति',
            yaxis_title='जनसंख्या',
            font=dict(family='Nirmala UI, Mangal, Arial', size=14),
            legend_title='लिङ्ग'
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("📄 कृपया Excel फाइल अपलोड गर्नुहोस् जसमा 'उमेर', 'लिङ्ग', 'जाति' को स्तम्भहरू छन्।")