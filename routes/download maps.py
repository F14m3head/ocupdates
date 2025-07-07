import os
import requests
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Ignore SSL warnings

BASE_URL = "https://www.octranspo.com/images/files/routes_pdf/" # Base URL for the route PDFs
DOWNLOAD_FOLDER = 'downloaded_routes/'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

routes = [
    '705', 'R1', '001', '002', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015',
    '017', '018', '019', '020', '021', '023', '024', '025', '026', '030', '031', '032', '033', '034', '035',
    '036', '038', '039', '040', '041', '042', '043', '044', '045', '047', '048', '049', '051', '053', '056',
    '057', '058', '060', '061', '062', '063', '066', '067', '068', '070', '073', '074', '075', '080', '081',
    '082', '084', '085', '086', '087', '088', '090', '092', '093', '094', '098', '099', '110', '111', '112',
    '116', '117', '125', '138', '139', '153', '158', '161', '162', '163', '165', '168', '173',
    '187', '189', '197', '198', '221', '222', '226', '228', '234', '237', '256', '261', '262',
    '263', '265', '266', '275', '277', '279', '283', '294', '299', '301', '302', '303', '304',
    '305', '450', '451', '452', '454', '455', '456'
    ]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
    }

def download_file(route_code):
    """
    Download a PDF file based on the route code.
    """
    # Construct the URL for the PDF file
    file_url = urljoin(BASE_URL, f'map_carte_{route_code}.pdf')
    local_filename = os.path.join(DOWNLOAD_FOLDER, f'{route_code}.pdf')

    try:
        # Request the file
        print(f"Downloading {file_url}...")
        response = requests.get(file_url, stream=True, verify=False, headers=headers)
        response.raise_for_status()  # Ensure we get a valid response (200 OK)

        # Save the file locally
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded {local_filename}")
        return local_filename  # Return the path to the saved file
    
    except requests.exceptions.RequestException as e: # If error, send error message
        print(f"Failed to download {file_url}: {e}")
        return None

downloaded_files = []

for route in routes:
      downloaded_file = download_file(route)
    if downloaded_file:
           downloaded_files.append(downloaded_file)
print(f"Successfully downloaded {len(downloaded_files)} files")