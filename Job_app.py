import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# Set page config
st.set_page_config(page_title="CareerVue: Job Market Insights", layout="wide")

# Load cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_job_data_with_skills.csv')
    # Normalize role names to match skill_to_roles (e.g., "Data-Analyst" -> "Data Analyst")
    df['role'] = df['role'].str.replace('-', ' ').str.title()
    return df

df = load_data()

# Define a color palette for the charts (distinct colors that work in both light and dark themes)
color_palette = [
    "#3440E8",  # Blue
    "#3466D3",  # Red
    "#648DE4",  # Green
    "#AC74E7",  # Purple
    "#CF5AEF",  # Orange
    "#E861DA",  # Cyan
    "#EE7093",  # Pink
    "#E45A8B",  # Light Green
    "#CB6481",  # Magenta
    "#A94162"   # Yellow
]

# Define roadmaps (for career roadmap feature only, skills are now in the CSV)
roadmaps = {
    "Data Analyst": {
        "skills": ["Excel", "SQL", "Python", "Tableau", "Power BI", "Statistics"],
        "roadmap": [
            {"step": "Master Excel", "description": "Learn data manipulation, pivot tables, and VLOOKUP.", "resources": "Excel Easy, Coursera Excel Basics, YouTube: ExcelIsFun"},
            {"step": "Learn SQL", "description": "Write queries, joins, and aggregations.", "resources": "Mode Analytics SQL Tutorial, Khan Academy SQL, W3Schools SQL"},
            {"step": "Learn Python", "description": "Use pandas, numpy, and matplotlib.", "resources": "Automate the Boring Stuff, DataCamp Python, Kaggle Python Course"},
            {"step": "Learn Tableau", "description": "Create interactive dashboards.", "resources": "Tableau Public, Udemy Tableau Course, YouTube: Tableau Tutorials"},
            {"step": "Learn Power BI", "description": "Build reports with DAX.", "resources": "Microsoft Learn Power BI, Coursera Power BI, YouTube: Guy in a Cube"},
            {"step": "Learn Statistics", "description": "Understand regression and hypothesis testing.", "resources": "StatQuest YouTube, Khan Academy Statistics, Coursera Statistics"}
        ]
    },
    "Data Scientist": {
        "skills": ["Python", "SQL", "Machine Learning", "Statistics", "R", "Data Visualization"],
        "roadmap": [
            {"step": "Learn Python", "description": "Master pandas, sklearn, and matplotlib.", "resources": "DataCamp Python, Kaggle Python Course, YouTube: Corey Schafer"},
            {"step": "Learn SQL", "description": "Query datasets with joins.", "resources": "SQLZoo, Mode Analytics, W3Schools SQL"},
            {"step": "Learn Data Analytics", "description": "Perform EDA and data cleaning.", "resources": "Coursera Data Analysis, Kaggle Tutorials, YouTube: StatQuest"},
            {"step": "Learn Machine Learning", "description": "Study regression, classification.", "resources": "Andrew Ng Coursera ML, Fast.ai, Kaggle ML Courses"},
            {"step": "Learn R", "description": "Use R for statistical modeling.", "resources": "R for Data Science, DataCamp R, YouTube: MarinStatsLectures"},
            {"step": "Explore Deep Learning", "description": "Learn neural networks with TensorFlow.", "resources": "DeepLearning.AI Coursera, YouTube: Sentdex, Fast.ai"}
        ]
    },
    "Machine Learning Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Cloud Platforms"],
        "roadmap": [
            {"step": "Learn Python", "description": "Master ML libraries like sklearn.", "resources": "Automate the Boring Stuff, DataCamp Python, Kaggle Python Course"},
            {"step": "Learn Machine Learning", "description": "Understand SVM, random forests.", "resources": "Andrew Ng Coursera ML, Fast.ai, Kaggle ML Courses"},
            {"step": "Learn Deep Learning", "description": "Build neural networks.", "resources": "DeepLearning.AI Coursera, YouTube: Sentdex, Fast.ai Deep Learning"},
            {"step": "Master TensorFlow", "description": "Develop production-ready models.", "resources": "TensorFlow Tutorials, Coursera TensorFlow, YouTube: TensorFlow"},
            {"step": "Master PyTorch", "description": "Use PyTorch for research.", "resources": "PyTorch Tutorials, Udemy PyTorch, YouTube: Python Engineer"},
            {"step": "Learn Cloud Platforms", "description": "Deploy models on AWS.", "resources": "AWS Machine Learning, Google Cloud ML, Microsoft Learn Azure"}
        ]
    },
    "Web Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB"],
        "roadmap": [
            {"step": "Learn HTML", "description": "Build webpage structures.", "resources": "W3Schools HTML, FreeCodeCamp, YouTube: Traversy Media"},
            {"step": "Learn CSS", "description": "Style with flexbox, animations.", "resources": "CSS-Tricks, FreeCodeCamp CSS, YouTube: Kevin Powell"},
            {"step": "Learn JavaScript", "description": "Add interactivity with ES6.", "resources": "JavaScript.info, Eloquent JavaScript, YouTube: The Net Ninja"},
            {"step": "Learn React", "description": "Build dynamic UI components.", "resources": "React Docs, Scrimba React, YouTube: Traversy Media"},
            {"step": "Learn Node.js", "description": "Create backend APIs.", "resources": "Node.js Docs, Udemy Node.js, YouTube: Academind"},
            {"step": "Learn MongoDB", "description": "Use NoSQL databases.", "resources": "MongoDB University, YouTube: Tech With Tim, Coursera MongoDB"}
        ]
    },
    "Mobile App Developer": {
        "skills": ["Flutter", "React Native", "Java", "Kotlin", "Swift", "REST APIs"],
        "roadmap": [
            {"step": "Learn Flutter", "description": "Build cross-platform apps.", "resources": "Flutter Docs, Udemy Flutter, YouTube: The Net Ninja"},
            {"step": "Learn React Native", "description": "Develop with JavaScript.", "resources": "React Native Docs, Coursera React Native, YouTube: Programming with Mosh"},
            {"step": "Learn Java", "description": "Understand Android fundamentals.", "resources": "Head First Java, Udemy Java, YouTube: ProgrammingKnowledge"},
            {"step": "Learn Kotlin", "description": "Use Kotlin for Android.", "resources": "Kotlin Docs, Udemy Kotlin, YouTube: Philipp Lackner"},
            {"step": "Learn Swift", "description": "Develop iOS apps.", "resources": "Apple Swift Docs, Hacking with Swift, YouTube: Sean Allen"},
            {"step": "Learn REST APIs", "description": "Connect apps to backends.", "resources": "Postman Tutorial, YouTube: Traversy Media, Coursera API Design"}
        ]
    },
    "Software Engineer": {
        "skills": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git"],
        "roadmap": [
            {"step": "Learn Python", "description": "Master general-purpose coding.", "resources": "Automate the Boring Stuff, DataCamp Python, YouTube: Corey Schafer"},
            {"step": "Learn Java", "description": "Understand OOP and enterprise apps.", "resources": "Head First Java, Udemy Java, YouTube: ProgrammingKnowledge"},
            {"step": "Learn C++", "description": "Use for performance-critical apps.", "resources": "LearnCpp.com, Udemy C++, YouTube: The Cherno"},
            {"step": "Learn Data Structures", "description": "Master arrays, trees.", "resources": "GeeksforGeeks DSA, Coursera DSA, YouTube: Abdul Bari"},
            {"step": "Learn Algorithms", "description": "Study sorting, dynamic programming.", "resources": "CLRS Book, LeetCode, YouTube: NeetCode"},
            {"step": "Learn Git", "description": "Use version control.", "resources": "Git Docs, YouTube: Traversy Media, Coursera Git"}
        ]
    },
    "DevOps Engineer": {
        "skills": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"],
        "roadmap": [
            {"step": "Learn Linux", "description": "Master system administration.", "resources": "Linux Journey, Udemy Linux, YouTube: LinuxHint"},
            {"step": "Learn Docker", "description": "Containerize applications.", "resources": "Docker Docs, YouTube: TechWorld with Nana, Coursera Docker"},
            {"step": "Learn Kubernetes", "description": "Orchestrate containers.", "resources": "Kubernetes Docs, Udemy Kubernetes, YouTube: KubeSimplified"},
            {"step": "Learn AWS", "description": "Use cloud infrastructure.", "resources": "AWS Free Tier, ACloudGuru, YouTube: AWS Training"},
            {"step": "Learn CI/CD", "description": "Automate with Jenkins.", "resources": "Jenkins Docs, YouTube: TechWorld with Nana, Coursera CI/CD"},
            {"step": "Learn Terraform", "description": "Manage infrastructure.", "resources": "Terraform Docs, Udemy Terraform, YouTube: HashiCorp"}
        ]
    },
    "Full Stack Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"],
        "roadmap": [
            {"step": "Learn HTML", "description": "Build webpage structures.", "resources": "W3Schools HTML, FreeCodeCamp, YouTube: Traversy Media"},
            {"step": "Learn CSS", "description": "Style with responsive design.", "resources": "CSS-Tricks, FreeCodeCamp CSS, YouTube: Kevin Powell"},
            {"step": "Learn JavaScript", "description": "Add client-side logic.", "resources": "JavaScript.info, Eloquent JavaScript, YouTube: The Net Ninja"},
            {"step": "Learn React", "description": "Develop dynamic frontends.", "resources": "React Docs, Scrimba React, YouTube: Traversy Media"},
            {"step": "Learn Node.js", "description": "Build scalable APIs.", "resources": "Node.js Docs, Udemy Node.js, YouTube: Academind"},
            {"step": "Learn SQL", "description": "Manage databases.", "resources": "SQLZoo, Mode Analytics, YouTube: Tech With Tim"}
        ]
    },
    "Cloud Engineer": {
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform"],
        "roadmap": [
            {"step": "Learn AWS", "description": "Master EC2, S3, Lambda.", "resources": "AWS Free Tier, ACloudGuru, YouTube: AWS Training"},
            {"step": "Learn Azure", "description": "Use Azure services.", "resources": "Microsoft Learn Azure, Udemy Azure, YouTube: Adam Marczak"},
            {"step": "Learn GCP", "description": "Explore Google Cloud.", "resources": "Google Cloud Skills Boost, Coursera GCP, YouTube: Google Cloud Tech"},
            {"step": "Learn Docker", "description": "Containerize apps.", "resources": "Docker Docs, YouTube: TechWorld with Nana, Coursera Docker"},
            {"step": "Learn Kubernetes", "description": "Orchestrate containers.", "resources": "Kubernetes Docs, Udemy Kubernetes, YouTube: KubeSimplified"},
            {"step": "Learn Terraform", "description": "Automate infrastructure.", "resources": "Terraform Docs, Udemy Terraform, YouTube: HashiCorp"}
        ]
    },
    "Python Developer": {
        "skills": ["Python", "Git", "Django", "Flask", "SQL"],
        "roadmap": [
            {"step": "Learn Python", "description": "Master Python programming.", "resources": "Automate the Boring Stuff, DataCamp Python, YouTube: Corey Schafer"},
            {"step": "Learn Git", "description": "Use version control.", "resources": "Git Docs, YouTube: Traversy Media, Coursera Git"},
            {"step": "Learn Django", "description": "Build web apps with Django.", "resources": "Django Docs, Udemy Django, YouTube: The Net Ninja"},
            {"step": "Learn Flask", "description": "Create lightweight web apps.", "resources": "Flask Docs, Udemy Flask, YouTube: Tech With Tim"},
            {"step": "Learn SQL", "description": "Manage databases.", "resources": "SQLZoo, Mode Analytics, YouTube: Tech With Tim"}
        ]
    }
}

# Define skill-to-role mapping (using normalized role names: "Data Analyst", "Python Developer", etc.)
skill_to_roles = {
    "Python": ["Data Analyst", "Data Scientist", "Machine Learning Engineer", "Software Engineer", "Python Developer"],
    "Java": ["Mobile App Developer", "Software Engineer"],
    "SQL": ["Data Analyst", "Data Scientist", "Full Stack Developer", "Python Developer"],
    "Excel": ["Data Analyst"],
    "Tableau": ["Data Analyst"],
    "Power BI": ["Data Analyst"],
    "Machine Learning": ["Data Scientist", "Machine Learning Engineer"],
    "Deep Learning": ["Data Scientist", "Machine Learning Engineer"],
    "HTML": ["Web Developer", "Full Stack Developer"],
    "CSS": ["Web Developer", "Full Stack Developer"],
    "JavaScript": ["Web Developer", "Full Stack Developer"],
    "React": ["Web Developer", "Full Stack Developer"],
    "Node.js": ["Web Developer", "Full Stack Developer"],
    "MongoDB": ["Web Developer"],
    "Flutter": ["Mobile App Developer"],
    "React Native": ["Mobile App Developer"],
    "Kotlin": ["Mobile App Developer"],
    "Swift": ["Mobile App Developer"],
    "C++": ["Software Engineer"],
    "Data Structures": ["Software Engineer"],
    "Git": ["Software Engineer", "Python Developer"],
    "Linux": ["DevOps Engineer"],
    "Docker": ["DevOps Engineer", "Cloud Engineer"],
    "Kubernetes": ["DevOps Engineer", "Cloud Engineer"],
    "AWS": ["DevOps Engineer", "Cloud Engineer"],
    "Azure": ["Cloud Engineer"],
    "Statistics": ["Data Analyst", "Data Scientist"],
    "R": ["Data Scientist" "Data Analyst"],
    "Cloud Platforms": ["Machine Learning Engineer"],

}

# Extract all unique skills from the skills column
all_skills = set()
for skills in df['skills'].dropna():
    if isinstance(skills, str):
        for skill in skills.split(", "):
            all_skills.add(skill.strip())

# Homepage
st.title("CareerVue:  A platform that gives you a clear view into career trends")
st.markdown("Explore India's tech job trends from Naukri and Indeed. Select a role to download a career roadmap for job preparation.")

# Sidebar for filters and roadmap selection
st.sidebar.header("Filter Options")
location_filter = st.sidebar.multiselect("Select Location", options=df['location'].unique(), default=[])
role_filter = st.sidebar.multiselect("Select Role", options=df['role'].unique(), default=[])
source_option = st.sidebar.selectbox("Select Data Source", options=["Both", "Naukri", "Indeed"], index=0)
title_search = st.sidebar.text_input("Search Job Title")

# Additional sidebar filters
st.sidebar.subheader("Advanced Filters")
salary_filter = st.sidebar.slider("Salary Range (₹ Lakhs)", min_value=0, max_value=50, value=(0, 50))

# Skills filter using the skills from the CSV
skills_filter = st.sidebar.multiselect("Select Skills", options=sorted(list(all_skills)), default=[])

# Filter data based on source
if source_option == "Naukri":
    filtered_df = df[df['source'] == 'Naukri']
elif source_option == "Indeed":
    filtered_df = df[df['source'] == 'Indeed']
else:
    filtered_df = df.copy()

# Apply location filter
if location_filter:
    filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]

# Apply role filter
if role_filter:
    filtered_df = filtered_df[filtered_df['role'].isin(role_filter)]

# Apply title search
if title_search:
    filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(title_search.lower(), na=False)]

# Apply salary filter
if 'salary' in filtered_df.columns:
    def convert_salary_to_numeric(salary):
        if isinstance(salary, str):
            if '-' in salary:
                try:
                    low, high = map(float, salary.split('-'))
                    return (low + high) / 2
                except:
                    return 0
            elif salary == 'Not Disclosed':
                return 0
            try:
                return float(salary)
            except:
                return 0
        return 0

    filtered_df['salary_numeric'] = filtered_df['salary'].apply(convert_salary_to_numeric)
    filtered_df = filtered_df[
        (filtered_df['salary_numeric'] >= salary_filter[0] * 100000) & 
        (filtered_df['salary_numeric'] <= salary_filter[1] * 100000)
    ]

# Apply skills filter and map to roles
if skills_filter:
    # First, filter jobs that have any of the selected skills
    filtered_df = filtered_df[filtered_df['skills'].apply(
        lambda skills: isinstance(skills, str) and any(skill in skills.split(", ") for skill in skills_filter)
    )]
    # Then, optionally filter by related roles (relaxed to avoid over-filtering)
    related_roles = set()
    for skill in skills_filter:
        if skill in skill_to_roles:
            related_roles.update(skill_to_roles[skill])
    if related_roles:
        filtered_df = filtered_df[filtered_df['role'].isin(related_roles)]
    # If no related roles match, don't filter further to avoid empty results

# Check if filtered_df is empty after applying filters
if filtered_df.empty:
    st.warning("No jobs match the selected filters. Please adjust your filters to see results.")
else:
    # Roadmap feature
    st.header("Career Roadmap")
    roadmap_role = st.selectbox("Select Role for Roadmap", options=list(roadmaps.keys()))
    if roadmap_role:
        st.subheader(f"Career Roadmap for {roadmap_role}")
        roadmap = roadmaps[roadmap_role]
        st.write("**Skills Required:**", ", ".join(roadmap['skills']))
        st.write("**Roadmap to Prepare:**")
        for step in roadmap['roadmap']:
            st.write(f"- **{step['step']}**: {step['description']} (Resources: {step['resources']})")

        def create_roadmap_pdf(role, roadmap):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph(f"CodeMantra Career Roadmap for {role}", styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Skills Required: {', '.join(roadmap['skills'])}", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Roadmap to Prepare:", styles['Heading2']))
            story.append(Spacer(1, 6))
            for step in roadmap['roadmap']:
                story.append(Paragraph(f"{step['step']}: {step['description']} (Resources: {step['resources']})", styles['Normal']))
                story.append(Spacer(1, 6))

            doc.build(story)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_roadmap_pdf(roadmap_role, roadmap)
        st.download_button(
            label=f"Download {roadmap_role} Roadmap PDF",
            data=pdf_buffer,
            file_name=f"{roadmap_role}_Roadmap.pdf",
            mime="application/pdf"
        )

    # Trending jobs by role
    st.header("Trending Jobs by Role")
    role_counts = filtered_df['role'].value_counts()
    st.write("Roles based on job postings:")
    for role, count in role_counts.items():
        st.write(f"- {role}: {count} postings")

    # Graph: Job Demand by Role with Chart Type Selection
    st.header("Job Demand by Role")
    chart_type_roles = st.selectbox("Select Chart Type for Job Demand by Role", options=["Bar", "Pie", "Line"], index=0, key="chart_type_roles")

    if skills_filter:
        st.write(f"Showing roles for selected skills: {', '.join(skills_filter)}")
        role_counts = filtered_df['role'].value_counts()
        if role_counts.empty:
            st.warning("No roles match the selected skills after applying other filters.")
        else:
            role_counts_df = role_counts.reset_index()
            role_counts_df.columns = ['role', 'count']
            
            # Create the chart based on the selected type
            if chart_type_roles == "Bar":
                fig_role = px.bar(
                    role_counts_df,
                    x='role',
                    y='count',
                    labels={'role': 'Role', 'count': 'Number of Postings'},
                    title=f"Roles Demanding Skills: {', '.join(skills_filter)}"
                )
                fig_role.update_traces(
                    marker_color=[color_palette[i % len(color_palette)] for i in range(len(role_counts_df))],
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5,
                    opacity=0.8,
                    width=0.4
                )
                fig_role.update_layout(
                    height=600,
                    xaxis_tickangle=-45
                )
            elif chart_type_roles == "Pie":
                fig_role = px.pie(
                    role_counts_df,
                    names='role',
                    values='count',
                    title=f"Roles Demanding Skills: {', '.join(skills_filter)}"
                )
                fig_role.update_traces(
                    marker=dict(colors=[color_palette[i % len(color_palette)] for i in range(len(role_counts_df))]),
                    opacity=0.8
                )
                fig_role.update_layout(
                    height=600
                )
            else:  # Line chart
                fig_role = px.line(
                    role_counts_df,
                    x='role',
                    y='count',
                    labels={'role': 'Role', 'count': 'Number of Postings'},
                    title=f"Roles Demanding Skills: {', '.join(skills_filter)}"
                )
                fig_role.update_traces(
                    line_color=color_palette[0],
                    opacity=0.8
                )
                fig_role.update_layout(
                    height=600,
                    xaxis_tickangle=-45
                )
            
            st.plotly_chart(fig_role, use_container_width=True)
    else:
        role_counts = filtered_df['role'].value_counts()
        role_counts_df = role_counts.reset_index()
        role_counts_df.columns = ['role', 'count']
        
        if chart_type_roles == "Bar":
            fig_role = px.bar(
                role_counts_df,
                x='role',
                y='count',
                labels={'role': 'Role', 'count': 'Number of Postings'},
                title="Trending Roles in India's Market"
            )
            fig_role.update_traces(
                marker_color=[color_palette[i % len(color_palette)] for i in range(len(role_counts_df))],
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1.5,
                opacity=0.8,
                width=0.4
            )
            fig_role.update_layout(
                height=600,
                xaxis_tickangle=-45
            )
        elif chart_type_roles == "Pie":
            fig_role = px.pie(
                role_counts_df,
                names='role',
                values='count',
                title="Trending Roles in India's Market"
            )
            fig_role.update_traces(
                marker=dict(colors=[color_palette[i % len(color_palette)] for i in range(len(role_counts_df))]),
                opacity=0.8
            )
            fig_role.update_layout(
                height=600
            )
        else:  # Line chart
            fig_role = px.line(
                role_counts_df,
                x='role',
                y='count',
                labels={'role': 'Role', 'count': 'Number of Postings'},
                title="Trending Roles in India's Market"
            )
            fig_role.update_traces(
                line_color=color_palette[0],
                opacity=0.8
            )
            fig_role.update_layout(
                height=600,
                xaxis_tickangle=-45
            )
        
        st.plotly_chart(fig_role, use_container_width=True)

    # Graph: Job Postings by Salary Range with Chart Type Selection
    st.header("Job Postings by Salary Range")
    chart_type_salary = st.selectbox("Select Chart Type for Job Postings by Salary Range", options=["Bar", "Pie", "Line"], index=0, key="chart_type_salary")

    def bucket_salary(salary):
        if salary == 'Not Disclosed':
            return 'Not Disclosed'
        try:
            if '-' in salary:
                low, high = map(float, salary.split('-'))
                avg = (low + high) / 2
            else:
                avg = float(salary)
            if avg < 500000:
                return '<₹5L'
            elif avg <= 1000000:
                return '₹5L-₹10L'
            else:
                return '>₹10L'
        except:
            return 'Not Disclosed'

    filtered_df['salary_bucket'] = filtered_df['salary'].apply(bucket_salary)
    salary_counts = filtered_df['salary_bucket'].value_counts()
    salary_counts_df = salary_counts.reset_index()
    salary_counts_df.columns = ['salary_bucket', 'count']

    if chart_type_salary == "Bar":
        fig_salary = px.bar(
            salary_counts_df,
            x='salary_bucket',
            y='count',
            labels={'salary_bucket': 'Salary Range', 'count': 'Number of Postings'},
            title="Salary Trends in Job Postings"
        )
        fig_salary.update_traces(
            marker_color=[color_palette[i % len(color_palette)] for i in range(len(salary_counts_df))],
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5,
            opacity=0.8,
            width=0.4
        )
        fig_salary.update_layout(
            height=600,
            xaxis_tickangle=-45
        )
    elif chart_type_salary == "Pie":
        fig_salary = px.pie(
            salary_counts_df,
            names='salary_bucket',
            values='count',
            title="Salary Trends in Job Postings"
        )
        fig_salary.update_traces(
            marker=dict(colors=[color_palette[i % len(color_palette)] for i in range(len(salary_counts_df))]),
            opacity=0.8
        )
        fig_salary.update_layout(
            height=600
        )
    else:  # Line chart
        fig_salary = px.line(
            salary_counts_df,
            x='salary_bucket',
            y='count',
            labels={'salary_bucket': 'Salary Range', 'count': 'Number of Postings'},
            title="Salary Trends in Job Postings"
        )
        fig_salary.update_traces(
            line_color=color_palette[0],
            opacity=0.8
        )
        fig_salary.update_layout(
            height=600,
            xaxis_tickangle=-45
        )

    st.plotly_chart(fig_salary, use_container_width=True)

    # Graph: Job Postings by Location with Chart Type Selection
    st.header("Job Postings by Location")
    chart_type_location = st.selectbox("Select Chart Type for Job Postings by Location", options=["Bar", "Pie", "Line"], index=0, key="chart_type_location")

    location_counts = filtered_df['location'].value_counts().head(10)
    location_counts_df = location_counts.reset_index()
    location_counts_df.columns = ['location', 'count']

    if chart_type_location == "Bar":
        fig_location = px.bar(
            location_counts_df,
            x='location',
            y='count',
            labels={'location': 'Location', 'count': 'Number of Postings'},
            title="Top Job Locations in India"
        )
        fig_location.update_traces(
            marker_color=[color_palette[i % len(color_palette)] for i in range(len(location_counts_df))],
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5,
            opacity=0.8,
            width=0.4
        )
        fig_location.update_layout(
            height=600,
            xaxis_tickangle=-45
        )
    elif chart_type_location == "Pie":
        fig_location = px.pie(
            location_counts_df,
            names='location',
            values='count',
            title="Top Job Locations in India"
        )
        fig_location.update_traces(
            marker=dict(colors=[color_palette[i % len(color_palette)] for i in range(len(location_counts_df))]),
            opacity=0.8
        )
        fig_location.update_layout(
            height=600
        )
    else:  # Line chart
        fig_location = px.line(
            location_counts_df,
            x='location',
            y='count',
            labels={'location': 'Location', 'count': 'Number of Postings'},
            title="Top Job Locations in India"
        )
        fig_location.update_traces(
            line_color=color_palette[0],
            opacity=0.8
        )
        fig_location.update_layout(
            height=600,
            xaxis_tickangle=-45
        )

    st.plotly_chart(fig_location, use_container_width=True)

    # Graph: Trending Skills with Chart Type Selection
    st.header("Trending Skills")
    chart_type_skills = st.selectbox("Select Chart Type for Trending Skills", options=["Bar", "Pie", "Line"], index=0, key="chart_type_skills")

    if not filtered_df.empty and 'skills' in filtered_df.columns:
        skills_series = filtered_df['skills'].dropna().str.split(", ").explode().str.strip()
        skills_counts = skills_series.value_counts().head(10)
        if not skills_counts.empty:
            skills_counts_df = skills_counts.reset_index()
            skills_counts_df.columns = ['skills', 'count']

            if chart_type_skills == "Bar":
                fig_skills = px.bar(
                    skills_counts_df,
                    x='skills',
                    y='count',
                    labels={'skills': 'Skill', 'count': 'Number of Postings'},
                    title="Top Skills in Demand"
                )
                fig_skills.update_traces(
                    marker_color=[color_palette[i % len(color_palette)] for i in range(len(skills_counts_df))],
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5,
                    opacity=0.8,
                    width=0.4
                )
                fig_skills.update_layout(
                    height=600,
                    xaxis_tickangle=-45
                )
            elif chart_type_skills == "Pie":
                fig_skills = px.pie(
                    skills_counts_df,
                    names='skills',
                    values='count',
                    title="Top Skills in Demand"
                )
                fig_skills.update_traces(
                    marker=dict(colors=[color_palette[i % len(color_palette)] for i in range(len(skills_counts_df))]),
                    opacity=0.8
                )
                fig_skills.update_layout(
                    height=600
                )
            else:  # Line chart
                fig_skills = px.line(
                    skills_counts_df,
                    x='skills',
                    y='count',
                    labels={'skills': 'Skill', 'count': 'Number of Postings'},
                    title="Top Skills in Demand"
                )
                fig_skills.update_traces(
                    line_color=color_palette[0],
                    opacity=0.8
                )
                fig_skills.update_layout(
                    height=600,
                    xaxis_tickangle=-45
                )

            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.warning("No skills data available after filtering. Try adjusting your filters.")
    else:
        st.warning("No skills data available after filtering. Try adjusting your filters.")

    # Graph: Top Hiring Companies with Chart Type Selection
    st.header("Top Hiring Companies")
    chart_type_companies = st.selectbox("Select Chart Type for Top Hiring Companies", options=["Bar", "Pie", "Line"], index=0, key="chart_type_companies")

    company_counts = filtered_df['company'].value_counts().head(10)
    company_counts_df = company_counts.reset_index()
    company_counts_df.columns = ['company', 'count']

    if chart_type_companies == "Bar":
        fig_company = px.bar(
            company_counts_df,
            x='company',
            y='count',
            labels={'company': "Company", 'count': 'Number of Postings'},
            title="Top Companies by Job Postings"
        )
        fig_company.update_traces(
            marker_color=[color_palette[i % len(color_palette)] for i in range(len(company_counts_df))],
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5,
            opacity=0.8,
            width=0.4
        )
        fig_company.update_layout(
            height=600,
            xaxis_tickangle=-45
        )
    elif chart_type_companies == "Pie":
        fig_company = px.pie(
            company_counts_df,
            names='company',
            values='count',
            title="Top Companies by Job Postings"
        )
        fig_company.update_traces(
            marker=dict(colors=[color_palette[i % len(color_palette)] for i in range(len(company_counts_df))]),
            opacity=0.8
        )
        fig_company.update_layout(
            height=600
        )
    else:  # Line chart
        fig_company = px.line(
            company_counts_df,
            x='company',
            y='count',
            labels={'company': "Company", 'count': 'Number of Postings'},
            title="Top Companies by Job Postings"
        )
        fig_company.update_traces(
            line_color=color_palette[0],
            opacity=0.8
        )
        fig_company.update_layout(
            height=600,
            xaxis_tickangle=-45
        )

    st.plotly_chart(fig_company, use_container_width=True)

    # Display job listings
    st.header("Job Listings")
    st.write(f"Displaying {len(filtered_df)} job listings")
    st.dataframe(filtered_df[['title', 'company', 'location', 'salary', 'role', 'source', 'skills']])

    # Download filtered data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="filtered_job_data.csv",
        mime="text/csv"
    )