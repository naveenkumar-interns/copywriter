import streamlit as st
from backend import WebsiteCopySystem, CopyInput
import json
from pathlib import Path
import time

def init_session_state():
    if 'generated_copy' not in st.session_state:
        st.session_state.generated_copy = {}
    if 'generation_complete' not in st.session_state:
        st.session_state.generation_complete = False

def save_results(results: dict, filename: str):
    output_dir = Path("generated_copy")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

def main():
    st.set_page_config(
        page_title="AI Website Copywriter",
        page_icon="✍️",
        layout="wide"
    )
    
    init_session_state()
    
    # Header
    st.title("🚀 AI Website Copywriter")
    st.markdown("Generate professional website copy powered by AI")
    
    # Sidebar - Input Parameters
    with st.sidebar:
        st.header("Project Settings")
        
        # Basic Information
        product = st.text_input(
            "Product/Website Name*",
            help="Enter the name of your product or website"
        )
        
        industry = st.text_input(
            "Industry",
            help="e.g., Technology, E-commerce, Healthcare"
        )
        
        # Content Parameters
        st.subheader("Content Settings")
        
        tone = st.select_slider(
            "Tone of Voice",
            options=["Casual", "Friendly", "Professional", "Technical", "Luxury"],
            value="Professional"
        )
        
        length = st.select_slider(
            "Content Length",
            options=["Short", "Medium", "Long"],
            value="Medium"
        )
        
        brand_voice = st.text_area(
            "Brand Voice Description",
            help="Describe your brand's personality"
        )
        
        # Target Audience
        st.subheader("Target Audience")
        target_audience = st.text_area(
            "Describe your target audience*",
            help="Include demographics, interests, pain points"
        )
        
        # USPs
        st.subheader("Unique Selling Points")
        usp_count = st.number_input("Number of USPs", min_value=1, max_value=5, value=3)
        usps = []
        for i in range(usp_count):
            usp = st.text_input(f"USP {i+1}", key=f"usp_{i}")
            if usp:
                usps.append(usp)
    
    # Main Content Area
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.subheader("Website Sections")
        sections = []
        
        # Standard sections
        standard_sections = {
            "Homepage": True,
            "About": True,
            "Services": True,
            "Contact": True
        }
        
        cols = st.columns(2)
        for i, (section, default) in enumerate(standard_sections.items()):
            col_idx = i % 2
            with cols[col_idx]:
                if st.checkbox(section, default):
                    sections.append(section.lower())
        
        # Custom section
        custom_section = st.text_input("Add Custom Section")
        if custom_section:
            sections.append(custom_section.lower())
    
    # Generate Button
    if st.button("Generate Copy", type="primary", disabled=not (product and target_audience)):
        if not product or not target_audience:
            st.error("Please fill in all required fields marked with *")
            return
            
        try:
            with st.spinner("Generating your website copy..."):
                system = WebsiteCopySystem()
                
                input_data = CopyInput(
                    product=product,
                    tone=tone.lower(),
                    length=length.lower(),
                    industry=industry,
                    target_audience=target_audience,
                    brand_voice=brand_voice,
                    unique_selling_points=usps
                )
                
                results = system.generate_website_copy(input_data, sections)
                st.session_state.generated_copy = results
                st.session_state.generation_complete = True
                
                # Save results
                save_results(results, f"{product.lower().replace(' ', '_')}_copy.json")
                
            st.success("✅ Copy generated successfully!")
            
        except Exception as e:
            st.error(f"Error generating copy: {str(e)}")
            return
    
    # Display Results
    if st.session_state.generation_complete:
        st.header("Generated Website Copy")
        
        tabs = st.tabs([s.title() for s in sections])
        for tab, section in zip(tabs, sections):
            with tab:
                if section in st.session_state.generated_copy:
                    st.markdown(st.session_state.generated_copy[section])
                    
                    # Download buttons
                    col1, col2 = st.columns([1,4])
                    with col1:
                        if st.download_button(
                            f"Download {section.title()}",
                            st.session_state.generated_copy[section],
                            file_name=f"{section}_copy.txt"
                        ):
                            st.toast(f"Downloaded {section} copy!")
        
        # Export all sections
        if st.download_button(
            "Export All Sections",
            json.dumps(st.session_state.generated_copy, indent=2),
            file_name=f"{product.lower().replace(' ', '_')}_complete.json",
            mime="application/json"
        ):
            st.toast("📥 Exported all sections!")

if __name__ == "__main__":
    main()