import requests
import xml.etree.ElementTree as ET

def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            xml_content = response.text
            root = ET.fromstring(xml_content)
            urls = []
            for child in root:
                if 'url' in child.tag:
                    for url_child in child:
                        if 'loc' in url_child.tag:
                            urls.append(url_child.text)
            return urls
        else:
            print(f"Failed to fetch sitemap from {sitemap_url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
