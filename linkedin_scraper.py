import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import io
from urllib.parse import urlparse
import json

# Page configuration
st.set_page_config(
    page_title="LinkedIn Profile Scraper",
    page_icon="🔍",
    layout="wide"
)

class LinkedInScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # HR-related certifications mapping
        self.hr_certifications = {
            'SHRM-CP': {'provider': 'SHRM', 'type': 'HR Management'},
            'SHRM-SCP': {'provider': 'SHRM', 'type': 'HR Management'},
            'PHR': {'provider': 'HRCI', 'type': 'HR Professional'},
            'SPHR': {'provider': 'HRCI', 'type': 'Senior HR Professional'},
            'GPHR': {'provider': 'HRCI', 'type': 'Global HR Professional'},
            'SHRM-AP': {'provider': 'SHRM', 'type': 'Asia Pacific HR'},
            'CHRP': {'provider': 'HRPA', 'type': 'Chartered HR Professional'},
            'CHRL': {'provider': 'HRPA', 'type': 'Chartered HR Leader'},
            'CHRE': {'provider': 'HRPA', 'type': 'Chartered HR Executive'},
            'CCP': {'provider': 'WorldatWork', 'type': 'Compensation Professional'},
            'CBP': {'provider': 'WorldatWork', 'type': 'Benefits Professional'},
            'GRP': {'provider': 'WorldatWork', 'type': 'Global Remuneration Professional'}
        }
        
        # HR-related job title keywords
        self.hr_keywords = [
            'human resources', 'hr', 'talent', 'recruiting', 'recruitment', 
            'people', 'employee', 'workforce', 'compensation', 'benefits',
            'training', 'development', 'learning', 'organizational'
        ]

    def is_valid_linkedin_url(self, url):
        """Validate LinkedIn profile URL"""
        parsed = urlparse(url)
        return 'linkedin.com' in parsed.netloc and '/in/' in parsed.path

    def extract_profile_data(self, url):
        """Extract profile data from LinkedIn URL"""
        if not self.is_valid_linkedin_url(url):
            return None
            
        try:
            # Simulate API call or scraping (in real implementation, you'd use LinkedIn API or proper scraping)
            # For demo purposes, we'll simulate data extraction
            time.sleep(1)  # Rate limiting
            
            # This is a placeholder - in real implementation you'd parse the HTML
            profile_data = {
                'profile_name': f'Sample User {hash(url) % 1000}',
                'company_name': f'Company {hash(url) % 100}',
                'job_title': self._generate_sample_job_title(),
                'department': 'HR',
                'location': 'USA',
                'certifications': self._generate_sample_certifications()
            }
            
            return profile_data
            
        except Exception as e:
            st.error(f"Error processing {url}: {str(e)}")
            return None

    def _generate_sample_job_title(self):
        """Generate sample HR-related job titles"""
        titles = [
            'HR Manager', 'Senior HR Business Partner', 'Talent Acquisition Specialist',
            'Compensation Analyst', 'HR Director', 'People Operations Manager',
            'Recruiting Manager', 'Employee Relations Specialist', 'Learning and Development Manager'
        ]
        import random
        return random.choice(titles)

    def _generate_sample_certifications(self):
        """Generate sample certifications for demo"""
        import random
        cert_list = list(self.hr_certifications.keys())
        num_certs = random.randint(0, 3)
        
        certifications = []
        for _ in range(num_certs):
            cert = random.choice(cert_list)
            certifications.append({
                'name': cert,
                'provider': self.hr_certifications[cert]['provider'],
                'type': self.hr_certifications[cert]['type'],
                'issued_date': f"{random.randint(1, 12):02d}/{random.randint(2020, 2024)}",
                'renewal_date': f"{random.randint(1, 12):02d}/{random.randint(2025, 2027)}"
            })
        
        return certifications

    def is_hr_related(self, job_title, department=None):
        """Check if job title/department is HR-related"""
        text_to_check = f"{job_title} {department or ''}".lower()
        return any(keyword in text_to_check for keyword in self.hr_keywords)

    def process_profiles(self, urls, progress_callback=None):
        """Process multiple LinkedIn profile URLs"""
        results = []
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            if progress_callback:
                progress_callback(i + 1, total_urls)
                
            profile_data = self.extract_profile_data(url.strip())
            
            if profile_data:
                base_data = {
                    'profile_url': url,
                    'profile_name': profile_data['profile_name'],
                    'company_name': profile_data['company_name'],
                    'job_title': profile_data['job_title'],
                    'department': profile_data['department'],
                    'location': profile_data['location'],
                    'is_hr_related': self.is_hr_related(profile_data['job_title'], profile_data['department'])
                }
                
                # If no certifications, add single row
                if not profile_data['certifications']:
                    results.append({
                        **base_data,
                        'certification': '',
                        'certification_provider': '',
                        'certification_type': '',
                        'certification_issued': '',
                        'certification_renewal': ''
                    })
                else:
                    # Add row for each certification
                    for cert in profile_data['certifications']:
                        results.append({
                            **base_data,
                            'certification': cert['name'],
                            'certification_provider': cert['provider'],
                            'certification_type': cert['type'],
                            'certification_issued': cert['issued_date'],
                            'certification_renewal': cert['renewal_date']
                        })
        
        return results

def main():
    st.title("🔍 LinkedIn Profile Scraper")
    st.markdown("Extract profile information and HR certifications from LinkedIn profiles")
    
    # Initialize scraper
    scraper = LinkedInScraper()
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Filter options
    st.sidebar.subheader("Filters")
    filter_hr_only = st.sidebar.checkbox("HR-related profiles only", value=False)
    filter_certified_only = st.sidebar.checkbox("Certified professionals only", value=False)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "🔍 Search Profiles", "📊 Results"])
    
    with tab1:
        st.header("Upload Profile URLs")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file containing LinkedIn profile URLs",
            type=['csv', 'xlsx', 'xls'],
            help="File should contain a column with LinkedIn profile URLs"
        )
        
        # Manual URL input
        st.subheader("Or enter URLs manually:")
        manual_urls = st.text_area(
            "LinkedIn Profile URLs (one per line):",
            height=100,
            placeholder="https://www.linkedin.com/in/profile1\nhttps://www.linkedin.com/in/profile2"
        )
        
        # Column selection for uploaded file
        url_column = None
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.subheader("File Preview")
                st.dataframe(df.head())
                
                url_column = st.selectbox(
                    "Select column containing LinkedIn URLs:",
                    options=df.columns.tolist()
                )
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Process button
        if st.button("🚀 Start Processing", type="primary"):
            urls = []
            
            # Get URLs from file or manual input
            if uploaded_file and url_column:
                urls = df[url_column].dropna().tolist()
            elif manual_urls:
                urls = [url.strip() for url in manual_urls.split('\n') if url.strip()]
            
            if not urls:
                st.warning("Please provide LinkedIn profile URLs")
                return
            
            # Validate URLs
            valid_urls = [url for url in urls if scraper.is_valid_linkedin_url(url)]
            invalid_count = len(urls) - len(valid_urls)
            
            if invalid_count > 0:
                st.warning(f"Found {invalid_count} invalid LinkedIn URLs (skipped)")
            
            if not valid_urls:
                st.error("No valid LinkedIn URLs found")
                return
            
            st.info(f"Processing {len(valid_urls)} LinkedIn profiles...")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total):
                progress = current / total
                progress_bar.progress(progress)
                status_text.text(f"Processing profile {current} of {total}")
            
            # Process profiles
            with st.spinner("Extracting profile data..."):
                results = scraper.process_profiles(valid_urls, update_progress)
            
            if results:
                # Convert to DataFrame
                df_results = pd.DataFrame(results)
                
                # Apply filters
                if filter_hr_only:
                    df_results = df_results[df_results['is_hr_related'] == True]
                
                if filter_certified_only:
                    df_results = df_results[df_results['certification'] != '']
                
                # Store in session state
                st.session_state['results'] = df_results
                st.session_state['processed'] = True
                
                st.success(f"✅ Successfully processed {len(results)} profiles!")
                st.info("Check the 'Results' tab to view and download the data")
            else:
                st.error("No data could be extracted from the provided URLs")
    
    with tab2:
        st.header("Search Processed Profiles")
        
        if 'results' in st.session_state:
            df_results = st.session_state['results']
            
            # Search filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_name = st.text_input("Search by name:")
            
            with col2:
                search_company = st.text_input("Search by company:")
            
            with col3:
                search_certification = st.selectbox(
                    "Filter by certification:",
                    options=['All'] + list(scraper.hr_certifications.keys())
                )
            
            # Apply search filters
            filtered_df = df_results.copy()
            
            if search_name:
                filtered_df = filtered_df[
                    filtered_df['profile_name'].str.contains(search_name, case=False, na=False)
                ]
            
            if search_company:
                filtered_df = filtered_df[
                    filtered_df['company_name'].str.contains(search_company, case=False, na=False)
                ]
            
            if search_certification != 'All':
                filtered_df = filtered_df[
                    filtered_df['certification'] == search_certification
                ]
            
            st.subheader(f"Search Results ({len(filtered_df)} profiles)")
            st.dataframe(filtered_df, use_container_width=True)
            
        else:
            st.info("No processed data available. Please process some profiles first.")
    
    with tab3:
        st.header("Processing Results")
        
        if 'results' in st.session_state:
            df_results = st.session_state['results']
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Profiles", len(df_results['profile_url'].unique()))
            
            with col2:
                hr_count = df_results['is_hr_related'].sum()
                st.metric("HR-Related", hr_count)
            
            with col3:
                cert_count = len(df_results[df_results['certification'] != ''])
                st.metric("With Certifications", cert_count)
            
            with col4:
                unique_companies = df_results['company_name'].nunique()
                st.metric("Unique Companies", unique_companies)
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(df_results, use_container_width=True)
            
            # Download options
            st.subheader("Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV download
                csv = df_results.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"linkedin_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excel download
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_results.to_excel(writer, sheet_name='LinkedIn_Profiles', index=False)
                    
                    # Add summary sheet
                    summary_data = {
                        'Metric': ['Total Profiles', 'HR-Related', 'With Certifications', 'Unique Companies'],
                        'Count': [
                            len(df_results['profile_url'].unique()),
                            df_results['is_hr_related'].sum(),
                            len(df_results[df_results['certification'] != '']),
                            df_results['company_name'].nunique()
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                st.download_button(
                    label="📥 Download as Excel",
                    data=output.getvalue(),
                    file_name=f"linkedin_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Certification analysis
            if cert_count > 0:
                st.subheader("Certification Analysis")
                
                cert_df = df_results[df_results['certification'] != '']
                cert_counts = cert_df['certification'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(cert_counts)
                
                with col2:
                    provider_counts = cert_df['certification_provider'].value_counts()
                    st.bar_chart(provider_counts)
        
        else:
            st.info("No results to display. Please process some profiles first.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Note**: This is a demo application. In production, ensure compliance with LinkedIn's Terms of Service and data privacy regulations."
    )

if __name__ == "__main__":
    main()