import requests
import streamlit as st

def hgvs_req(chrom, pos, ref, alt):
    for_search = f"{chrom}:g.{pos}{ref}>{alt}"
    return for_search

def search(str):
    url = (f"https://rest.ensembl.org/vep/human/hgvs/{str}")
    headers = {"Content-Type": "application/json"} 
    result = requests.get(url, headers=headers)
    return result.json()

def is_pathogenic(ls):
    if isinstance(ls, dict) and ls.get("error"):
        return None, f"Server error: {ls.get('error')}"
    if not ls:
        return None, "No data returned. Please check your input."
    
    look = ls[0]
    colocated = look.get("colocated_variants")
    
    if not colocated:
        return None, "No colocated variants found."
    
    for variant in colocated:
        clin = variant.get("clin_sig") or variant.get("clin_sig_allele")
        if clin and "pathogenic" in str(clin).lower():
            if variant.get("phenotype_or_disease"):
                transcripts = look.get("transcript_consequences", [])
                gene_name = transcripts[0].get("gene_symbol") if transcripts else "Unknown Gene"
                return gene_name, None
    
    return None, "Not pathogenic or no clinical significance data."



st.title("🧬 𝘐𝘴 𝘪𝘵 𝘱𝘢𝘵𝘩𝘰𝘨𝘦𝘯𝘪𝘤?")
st.write("Insert information below.")

with st.form("variant_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        chrom = st.text_input("Chromosome", placeholder="e.g. 17")
        pos   = st.text_input("Position",   placeholder="e.g. 7674220")
    
    with col2:
        ref = st.text_input("Reference Base", placeholder="e.g. C")
        alt = st.text_input("Alternative Base", placeholder="e.g. T")
    
    submitted = st.form_submit_button("🔍 Check Pathogenicity")

if submitted:
    if not all([chrom, pos, ref, alt]):
        st.warning("⚠️ Fill up every field.")
    else:
        hgvs_str = hgvs_req(chrom, pos, ref, alt)
        
        st.info(f"Querying: `{hgvs_str}`")
        
        with st.spinner("Ensembl API..."):
            try:
                raw_data = search(hgvs_str)
            except Exception as e:
                st.error(f"API access failed: {e}")
                st.stop()
        
        gene, error_msg = is_pathogenic(raw_data)
        
        if gene:
            st.success(f"✅ **{gene}** gene was found pathologenic variant.")
            st.markdown(
                f"**UniProt gene detail:** [🔗Search {gene}](https://www.uniprot.org/uniprotkb?query={gene})",
                unsafe_allow_html=True
            )
        else:
            st.error(f"❌ {error_msg}")
        
        with st.expander("📄 Raw API Response"):
            st.json(raw_data)