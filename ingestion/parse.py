import os
import sys
import json
from bs4 import BeautifulSoup

DATA_RAW_DIR = os.path.join("data", "raw")
DATA_PROCESSED_DIR = os.path.join("data", "processed")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def clean_html_to_sections(html_content, url, fetched_at):
    soup = BeautifulSoup(html_content, 'html.parser')
    tag = soup.find('script', id='__NEXT_DATA__')
    if not tag:
        raise ValueError("Could not find __NEXT_DATA__ script tag in HTML.")
        
    data = json.loads(tag.string)
    
    # Safely traverse properties
    props = data.get('props', {})
    page_props = props.get('pageProps', {})
    mf_data = page_props.get('mfServerSideData', {})
    
    if not mf_data:
        raise ValueError("mfServerSideData is empty or not found in JSON state.")
        
    # Extract name and general info
    scheme_name = mf_data.get('scheme_name', 'N/A')
    category = mf_data.get('category', 'N/A')
    sub_category = mf_data.get('sub_category', 'N/A')
    description = mf_data.get('description', 'N/A')
    launch_date_raw = mf_data.get('launch_date', 'N/A')
    launch_date = launch_date_raw.split('T')[0] if (launch_date_raw and launch_date_raw != 'N/A') else 'N/A'
    
    aum = mf_data.get('aum', 'N/A')
    aum_formatted = f"₹{aum:,.2f} Cr" if isinstance(aum, (int, float)) else f"₹{aum} Cr"
    
    nav = mf_data.get('nav', 'N/A')
    nav_date_raw = mf_data.get('nav_date', 'N/A')
    nav_date = nav_date_raw.split('T')[0] if (nav_date_raw and nav_date_raw != 'N/A') else 'N/A'
    
    # Try finding risk
    risk = mf_data.get('nfo_risk')
    if not risk:
        peer_comparison = mf_data.get('peerComparison', [])
        for peer in peer_comparison:
            if peer.get('scheme_name') == scheme_name or peer.get('fund_name') in scheme_name:
                risk = peer.get('risk')
                break
    if not risk:
        risk = "Very High" # standard fallback for equity/mid/small cap
        
    logo_url = mf_data.get('logo_url', 'N/A')
    
    # 1. Overview
    overview_text = f"""### Overview: {scheme_name}
- **Scheme Name**: {scheme_name}
- **Category**: {category}
- **Sub-Category**: {sub_category}
- **Launch Date**: {launch_date}
- **Asset Under Management (AUM)**: {aum_formatted}
- **Current NAV**: ₹{nav} (as of {nav_date})
- **Riskometer Classification**: {risk}
- **Logo URL**: {logo_url}
- **Description**: {description}"""

    # 2. Expense Ratio
    expense_ratio = mf_data.get('expense_ratio', 'N/A')
    historic_expense = mf_data.get('historic_fund_expense', [])
    expense_text = f"### Expense Ratio\n- **Current Expense Ratio**: {expense_ratio}%\n"
    if historic_expense:
        expense_text += "\n**Historical Expense Ratios**:\n"
        for item in historic_expense[:5]:
            date_val = item.get('as_on_date', '')
            date = date_val.split('T')[0] if date_val else 'N/A'
            val = item.get('expense_ratio', 'N/A')
            expense_text += f"- As of {date}: {val}%\n"
            
    # 3. Exit Load
    exit_load = mf_data.get('exit_load', 'N/A')
    historic_exit_loads = mf_data.get('historic_exit_loads', [])
    exit_text = f"### Exit Load\n- **Exit Load Details**: {exit_load}\n"
    if historic_exit_loads:
        exit_text += "\n**Historical Exit Loads**:\n"
        for item in historic_exit_loads[:5]:
            date_val = item.get('as_on_date', '')
            date = date_val.split('T')[0] if date_val else 'N/A'
            val = item.get('exit_load', 'N/A')
            exit_text += f"- As of {date}: {val}\n"

    # 4. Minimum Investment
    min_lump = mf_data.get('min_investment_amount', 'N/A')
    min_sip = mf_data.get('min_sip_investment', 'N/A')
    sip_mult = mf_data.get('sip_multiplier', 'N/A')
    add_inv = mf_data.get('mini_additional_investment', 'N/A')
    min_inv_text = f"""### Minimum Investment Requirements
- **Minimum Lumpsum Investment**: ₹{min_lump}
- **Minimum SIP Investment**: ₹{min_sip}
- **SIP Multiplier**: ₹{sip_mult}
- **Minimum Additional Investment**: ₹{add_inv}"""

    # 5. Benchmark
    bench_name = mf_data.get('benchmark_name', 'N/A')
    bench_code = mf_data.get('benchmark', 'N/A')
    benchmark_text = f"### Benchmark Index\n- **Benchmark Index Name**: {bench_name}\n- **Benchmark Code**: {bench_code}"

    # 6. Tax
    sub_cat_lower = sub_category.lower()
    cat_lower = category.lower()
    is_equity = (cat_lower == 'equity') or any(k in sub_cat_lower for k in ['small', 'mid', 'large', 'defence'])
    
    if is_equity:
        tax_text = """### Taxation Rules (Equity Mutual Fund)
- **Short-term Capital Gains (STCG)**: Gains on units held for 1 year or less are taxed at 15% (20% under updated rules).
- **Long-term Capital Gains (LTCG)**: Gains on units held for more than 1 year are tax-free up to ₹1 Lakh per financial year. Gains exceeding ₹1 Lakh are taxed at 10% (12.5% under updated rules) without indexation benefit."""
    else:
        tax_text = """### Taxation Rules (Debt / Other Mutual Fund)
- **Income Tax Slab Rate**: For Gold/Silver, commodity ETFs, or non-equity fund of funds, returns are classified as capital gains and are taxed at the investor's marginal income tax slab rate (applicable for investments made on or after April 1, 2023)."""

    # 7. Fund Management
    fund_mgrs = mf_data.get('fund_manager_details', [])
    mgmt_text = "### Fund Management\n"
    if fund_mgrs:
        for mgr in fund_mgrs:
            name = mgr.get('person_name', 'N/A')
            edu = mgr.get('education', 'N/A')
            exp = mgr.get('experience', 'N/A')
            f_managed = mgr.get('funds_managed', [])
            f_names = [f.get('scheme_name') for f in f_managed if f.get('scheme_name')]
            
            mgmt_text += f"\n#### Fund Manager: {name}\n"
            mgmt_text += f"- **Education**: {edu}\n"
            mgmt_text += f"- **Experience**: {exp}\n"
            if f_names:
                mgmt_text += f"- **Other Funds Managed**: {', '.join(f_names[:10])}\n"
    else:
        # Fallback to general fund manager names if details list is empty
        fm_names = mf_data.get('fund_manager', 'N/A')
        mgmt_text += f"\n- **Fund Manager Name(s)**: {fm_names}\n- (Detailed biography and experience profile not available for this scheme)"

    # 8. Investment Objective
    inv_obj_text = f"### Investment Objective\n- **Objective**: {description}"

    # 9. Fund House
    amc_info = mf_data.get('amc_info') or {}
    amc_name = amc_info.get('name', 'N/A')
    amc_addr = amc_info.get('address', 'N/A')
    amc_phone = amc_info.get('phone', 'N/A')
    amc_email = amc_info.get('email', 'N/A')
    amc_website = amc_info.get('vro_website', 'N/A')
    amc_desc = amc_info.get('description', 'N/A')
    amc_more = amc_info.get('more_description', '')
    
    if amc_more:
        amc_more_soup = BeautifulSoup(amc_more, 'html.parser')
        amc_more_clean = amc_more_soup.get_text('\n').strip()
    else:
        amc_more_clean = ""
        
    fund_house_text = f"""### Fund House Profile: {amc_name}
- **AMC Name**: {amc_name}
- **Address**: {amc_addr}
- **Phone**: {amc_phone}
- **Email**: {amc_email}
- **Website**: {amc_website}
- **About the AMC**: {amc_desc}
{amc_more_clean}"""

    # Pack into sections dict
    sections = {
        "overview": overview_text.strip(),
        "expense_ratio": expense_text.strip(),
        "exit_load": exit_text.strip(),
        "minimum_investment": min_inv_text.strip(),
        "benchmark": benchmark_text.strip(),
        "tax": tax_text.strip(),
        "fund_management": mgmt_text.strip(),
        "investment_objective": inv_obj_text.strip(),
        "fund_house": fund_house_text.strip(),
        "metadata": {
            "source_url": url,
            "fetched_at": fetched_at
        }
    }
    return sections

def parse_all():
    ensure_dir(DATA_PROCESSED_DIR)
    
    html_files = [f for f in os.listdir(DATA_RAW_DIR) if f.endswith(".html")]
    if not html_files:
        print("No raw HTML files found in data/raw/. Please run fetch.py first.", file=sys.stderr)
        return
        
    for file_name in html_files:
        slug = file_name.replace(".html", "")
        html_path = os.path.join(DATA_RAW_DIR, file_name)
        meta_path = os.path.join(DATA_RAW_DIR, f"{slug}_metadata.json")
        
        # Load metadata
        url = "N/A"
        fetched_at = "N/A"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                url = meta.get("url", "N/A")
                fetched_at = meta.get("fetched_at", "N/A")
                
        print(f"Parsing: {file_name} ...")
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
                
            sections = clean_html_to_sections(html_content, url, fetched_at)
            
            # Save as JSON
            json_output_path = os.path.join(DATA_PROCESSED_DIR, f"{slug}_processed.json")
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(sections, f, indent=4)
                
            # Save as human-readable markdown for reference and debugging
            md_output_path = os.path.join(DATA_PROCESSED_DIR, f"{slug}_processed.md")
            with open(md_output_path, "w", encoding="utf-8") as f:
                f.write(f"# Scheme Sections: {slug}\n\n")
                f.write(f"Source URL: {url}\n")
                f.write(f"Last Fetched: {fetched_at}\n\n")
                for key, val in sections.items():
                    if key == "metadata":
                        continue
                    f.write(f"--- \n\n## Section: {key}\n\n{val}\n\n")
                    
            print(f"Successfully parsed and wrote processed files for {slug}.")
            
        except Exception as e:
            print(f"Error parsing {file_name}: {e}", file=sys.stderr)

if __name__ == "__main__":
    parse_all()
