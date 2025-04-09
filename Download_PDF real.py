import requests
import time
import os

# Replace with your own email as required by Unpaywall API usage policies.
EMAIL = "65011212003@msu.ac.th"

def fetch_dois(query, rows=100):
    """
    Fetch DOIs from CrossRef API for a given query.
    """
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": rows,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    dois = [item['DOI'] for item in data['message']['items']]
    return dois

def get_open_access_pdf_url(doi):
    """
    Get the open access PDF URL from Unpaywall API for a given DOI.
    """
    url = f"https://api.unpaywall.org/v2/{doi}"
    params = {"email": EMAIL}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if data.get("is_oa"):
        oa_locations = data.get("oa_locations", [])
        for location in oa_locations:
            pdf_url = location.get("url_for_pdf")
            if pdf_url:
                return pdf_url
    return None

def download_pdf(url, filename):
    """
    Download a PDF from a URL and save it locally.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

def main():
    query = "agriculture diseases"
    dois = fetch_dois(query, rows=100)
    print(f"Found {len(dois)} DOIs for query: {query}")
    
    # Create folder to store downloaded papers.
    folder = "papers"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    downloaded = 0
    for doi in dois:
        pdf_url = get_open_access_pdf_url(doi)
        if pdf_url:
            # Replace '/' in DOI with '_' for a safe filename.
            safe_doi = doi.replace("/", "_")
            filename = os.path.join(folder, f"{safe_doi}.pdf")
            download_pdf(pdf_url, filename)
            downloaded += 1
            # Pause to avoid hammering the API endpoints.
            time.sleep(1)
        else:
            print(f"No open access PDF found for DOI: {doi}")
        
        # Stop once we reach 100 downloaded papers.
        if downloaded >= 100:
            break

    print(f"Downloaded {downloaded} open access papers.")

if __name__ == "__main__":
    main()
