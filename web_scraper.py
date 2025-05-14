import trafilatura
import logging
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.

    Args:
        url: The URL of the website to scrape.

    Returns:
        str: The extracted text content from the website.
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            logger.error(f"Failed to download content from URL: {url}")
            return f"Unable to fetch content from {url}. Please check the URL and try again."
        
        # Extract the main content
        text = trafilatura.extract(downloaded)
        
        if not text:
            logger.warning(f"No content extracted from URL: {url}")
            return f"No content could be extracted from {url}. The page might have no main text content or might be protected."
            
        return text
    
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        return f"Error processing {url}: {str(e)}"


def get_job_listings(url: str) -> list:
    """
    Scrape job listings from a given URL.
    
    Args:
        url: The URL of the job board or listings page.
        
    Returns:
        list: A list of dictionaries containing job listings with their details.
    """
    import re
    from bs4 import BeautifulSoup
    import trafilatura
    import requests
    
    logger.info(f"Fetching job listings from: {url}")
    jobs = []
    
    try:
        # Attempt to download the page content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.error(f"Failed to download content from: {url}")
            return jobs
            
        # Use trafilatura to extract main content
        extracted_text = trafilatura.extract(downloaded)
        if not extracted_text:
            logger.error(f"Failed to extract text content from: {url}")
            
            # Fallback to direct requests + BeautifulSoup if trafilatura fails
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find job listings based on common patterns - this is site-specific
                # and would need customization for each job board
                
                # For Indeed-like sites
                if "indeed.com" in url:
                    job_cards = soup.find_all("div", class_=lambda c: c and ("job_" in c or "jobCard" in c or "job-card" in c))
                    for card in job_cards[:10]:  # Limit to first 10 results
                        title_elem = card.find("h2", class_=lambda c: c and ("title" in c or "jobTitle" in c))
                        company_elem = card.find(["span", "div"], class_=lambda c: c and ("company" in c))
                        location_elem = card.find(["div", "span"], class_=lambda c: c and ("location" in c))
                        link_elem = card.find("a", href=True)
                        
                        if title_elem:
                            job_info = {
                                "title": title_elem.text.strip(),
                                "company": company_elem.text.strip() if company_elem else "Unknown Company",
                                "location": location_elem.text.strip() if location_elem else "Unknown Location",
                                "source_url": "https://indeed.com" + link_elem['href'] if link_elem and link_elem['href'].startswith('/') else link_elem['href'] if link_elem else url,
                                "description_snippet": "Click to view full job description on the source website.",
                                "source": "Indeed"
                            }
                            jobs.append(job_info)
                
                # For LinkedIn-like sites
                elif "linkedin.com" in url:
                    job_cards = soup.find_all("div", class_=lambda c: c and ("job-search-card" in c or "job-card" in c))
                    for card in job_cards[:10]:
                        title_elem = card.find(["h3", "h2"], class_=lambda c: c and ("title" in c))
                        company_elem = card.find(["h4", "span"], class_=lambda c: c and ("company" in c))
                        location_elem = card.find(["span", "div"], class_=lambda c: c and ("location" in c))
                        link_elem = card.find("a", href=True)
                        
                        if title_elem:
                            job_info = {
                                "title": title_elem.text.strip(),
                                "company": company_elem.text.strip() if company_elem else "Unknown Company",
                                "location": location_elem.text.strip() if location_elem else "Unknown Location",
                                "source_url": link_elem['href'] if link_elem else url,
                                "description_snippet": "Click to view full job description on the source website.",
                                "source": "LinkedIn"
                            }
                            jobs.append(job_info)
                            
                # Generic fallback for other sites
                if not jobs:
                    # Look for any link that might contain job info
                    job_links = soup.find_all("a", href=True, text=lambda t: t and ("job" in t.lower() or "career" in t.lower() or "position" in t.lower()))
                    for link in job_links[:10]:
                        jobs.append({
                            "title": link.text.strip(),
                            "company": "See job details",
                            "location": "See job details",
                            "source_url": link['href'] if link['href'].startswith('http') else (url.split('/')[0] + '//' + url.split('/')[2] + link['href'] if link['href'].startswith('/') else url),
                            "description_snippet": "Click to view full job details on the source website.",
                            "source": url.split('/')[2]
                        })
            except Exception as e:
                logger.error(f"BeautifulSoup fallback failed: {str(e)}")
                
            return jobs  # Return whatever we may have found, even if empty
            
        # If trafilatura extraction was successful, try to parse job listings from the text
        # This is a simple pattern-based approach that might work for plain text
        job_blocks = re.split(r'\n\s*\n', extracted_text)
        
        # For each potential job block, try to extract job information
        for block in job_blocks[:15]:  # Limit to first 15 blocks to avoid processing too much
            lines = block.split('\n')
            if len(lines) >= 3:  # A reasonable job listing should have at least 3 lines of information
                # Simple assumption that first line is title, second is company, etc.
                # This is a very basic heuristic and would need refinement for real-world usage
                job_info = {
                    "title": lines[0].strip(),
                    "company": lines[1].strip() if len(lines) > 1 else "Unknown",
                    "location": next((line.strip() for line in lines[2:] if re.search(r'location|address|city|remote', line, re.I)), "Unknown Location"),
                    "source_url": url,
                    "description_snippet": "\n".join(lines[2:6]) + "...",  # First few lines as a description snippet
                    "source": url.split('/')[2]
                }
                
                # Only include if it looks like a job title (contains common job title words)
                if re.search(r'engineer|developer|manager|analyst|specialist|coordinator|assistant|director|designer|writer|editor|consultant|expert', job_info["title"], re.I):
                    jobs.append(job_info)
        
        logger.info(f"Extracted {len(jobs)} job listings from {url}")
        
    except Exception as e:
        logger.error(f"Error scraping jobs from {url}: {str(e)}")
    
    return jobs


def get_scholarship_listings(url: str) -> list:
    """
    Scrape scholarship listings from a given URL.
    
    Args:
        url: The URL of the scholarship listings page.
        
    Returns:
        list: A list of dictionaries containing scholarship details.
    """
    import re
    from bs4 import BeautifulSoup
    import trafilatura
    import requests
    from datetime import datetime, timedelta
    
    logger.info(f"Fetching scholarship listings from: {url}")
    scholarships = []
    
    try:
        # Attempt to download the page content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.error(f"Failed to download content from: {url}")
            return scholarships
            
        # Use trafilatura to extract main content
        extracted_text = trafilatura.extract(downloaded)
        if not extracted_text:
            logger.error(f"Failed to extract text content from: {url}")
            
            # Fallback to direct requests + BeautifulSoup if trafilatura fails
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # For scholarship4dev-like sites
                if "scholars4dev.com" in url or "scholarship" in url:
                    scholarship_items = soup.find_all(["div", "article"], class_=lambda c: c and ("scholarship" in c.lower() if c else False))
                    
                    if not scholarship_items:
                        # Try to find links containing scholarship info
                        scholarship_links = soup.find_all("a", href=True, text=lambda t: t and (
                            "scholarship" in t.lower() or 
                            "fellowship" in t.lower() or 
                            "grant" in t.lower() or
                            "funding" in t.lower()))
                        
                        for link in scholarship_links[:10]:
                            scholarship_url = link['href'] if link['href'].startswith('http') else (
                                url.split('/')[0] + '//' + url.split('/')[2] + link['href'] 
                                if link['href'].startswith('/') else url)
                                
                            scholarships.append({
                                "title": link.text.strip(),
                                "organization": "See details on source website",
                                "country": "Various",
                                "field_of_study": "Various",
                                "amount": "See details on source website",
                                "deadline": (datetime.utcnow() + timedelta(days=90)).strftime("%B %d, %Y"),
                                "source_url": scholarship_url,
                                "description_snippet": "Click to view full scholarship details on the source website.",
                                "source": url.split('/')[2]
                            })
                    else:
                        # Process found scholarship items
                        for item in scholarship_items[:10]:
                            title_elem = item.find(["h2", "h3", "h4", "a"], text=lambda t: t and len(t) > 10)
                            link_elem = item.find("a", href=True) if not title_elem or not title_elem.name == "a" else title_elem
                            
                            # Try to extract details from the item
                            description = item.find(["div", "p"], class_=lambda c: c and ("desc" in c.lower() or "excerpt" in c.lower() if c else False))
                            description_text = description.text.strip() if description else None
                            
                            if not description_text:
                                # Try to get any paragraph text
                                paragraphs = item.find_all("p")
                                if paragraphs:
                                    description_text = paragraphs[0].text.strip()
                                    
                            # Extract metadata like deadline, country, etc.
                            country_match = re.search(r'Country:\s*([A-Za-z\s,]+)', item.text) if item.text else None
                            deadline_match = re.search(r'Deadline:\s*([A-Za-z0-9\s,]+)', item.text) if item.text else None
                            
                            if title_elem:
                                scholarship_url = link_elem['href'] if link_elem and link_elem.has_attr('href') else url
                                if not scholarship_url.startswith('http'):
                                    scholarship_url = url.split('/')[0] + '//' + url.split('/')[2] + (
                                        scholarship_url if scholarship_url.startswith('/') else '/' + scholarship_url)
                                    
                                scholarships.append({
                                    "title": title_elem.text.strip(),
                                    "organization": "See details on source website",
                                    "country": country_match.group(1) if country_match else "Various",
                                    "field_of_study": "Various",
                                    "amount": "See details",
                                    "deadline": deadline_match.group(1) if deadline_match else "See website for deadline",
                                    "source_url": scholarship_url,
                                    "description_snippet": description_text[:200] + "..." if description_text and len(description_text) > 200 else description_text if description_text else "Click for details",
                                    "source": url.split('/')[2]
                                })
                                
                # Generic fallback for other websites
                if not scholarships:
                    # Look for any content that mentions scholarships
                    content_blocks = soup.find_all(["div", "article", "section"], text=lambda t: t and (
                        "scholarship" in t.lower() or 
                        "fellowship" in t.lower() or 
                        "grant" in t.lower()))
                        
                    for block in content_blocks[:5]:
                        title_elem = block.find(["h1", "h2", "h3", "h4", "strong"])
                        link_elem = block.find("a", href=True)
                        
                        if title_elem:
                            scholarships.append({
                                "title": title_elem.text.strip(),
                                "organization": "See details on source website",
                                "country": "Various",
                                "field_of_study": "Various",
                                "amount": "See details",
                                "deadline": "See website for deadline",
                                "source_url": link_elem['href'] if link_elem and link_elem.has_attr('href') else url,
                                "description_snippet": block.text[:200].strip() + "..." if len(block.text) > 200 else block.text.strip(),
                                "source": url.split('/')[2]
                            })
                
            except Exception as e:
                logger.error(f"BeautifulSoup fallback failed: {str(e)}")
                
            return scholarships
        
        # If trafilatura extraction was successful, try to parse from the extracted text
        # This is more challenging for plain text but we'll try a pattern-based approach
        scholarship_sections = re.split(r'\n\s*\n', extracted_text)
        
        for section in scholarship_sections[:10]:  # Limit to first 10 sections
            lines = section.split('\n')
            if len(lines) >= 3:  # Need at least a few lines to be a meaningful entry
                # Check if it looks like a scholarship
                if re.search(r'scholarship|fellowship|grant|funding|stipend', section, re.I):
                    # Try to identify the title (usually the first line with significant text)
                    title = lines[0].strip()
                    
                    # Look for descriptions of deadlines, amounts, fields, etc.
                    deadline_match = re.search(r'deadline[:\s]+([A-Za-z0-9\s,\.]+)', section, re.I)
                    amount_match = re.search(r'(amount|award|funding)[:\s]+([\$€£A-Za-z0-9\s,\.]+)', section, re.I)
                    field_match = re.search(r'(field|study|subject)[:\s]+([A-Za-z0-9\s,\.]+)', section, re.I)
                    country_match = re.search(r'(country|location|place)[:\s]+([A-Za-z0-9\s,\.]+)', section, re.I)
                    
                    description = "\n".join(lines[1:5]) if len(lines) > 1 else "See source for details"
                    
                    scholarships.append({
                        "title": title,
                        "organization": next((line.strip() for line in lines[1:3] if not re.search(r'deadline|amount|field|country', line, re.I)), "See details"),
                        "country": country_match.group(2).strip() if country_match else "Various",
                        "field_of_study": field_match.group(2).strip() if field_match else "Various",
                        "amount": amount_match.group(2).strip() if amount_match else "See details",
                        "deadline": deadline_match.group(1).strip() if deadline_match else "See website for deadline",
                        "source_url": url,
                        "description_snippet": description,
                        "source": url.split('/')[2]
                    })
        
        logger.info(f"Extracted {len(scholarships)} scholarship listings from {url}")
        
    except Exception as e:
        logger.error(f"Error scraping scholarships from {url}: {str(e)}")
    
    return scholarships


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.
    
    Args:
        url: The URL to validate.
        
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_date_from_content(content: str) -> datetime:
    """
    Attempt to extract a publication date from content.
    
    Args:
        content: The text content to analyze.
        
    Returns:
        datetime: The extracted date, or current date if none found.
    """
    # Default to current date/time
    result_date = datetime.utcnow()
    
    try:
        metadata = trafilatura.extract_metadata(content)
        if not metadata:
            return result_date
            
        metadata_dict = metadata.as_dict()
        if not metadata_dict or 'date' not in metadata_dict or not metadata_dict['date']:
            return result_date
            
        # Try to parse the date string into a datetime object
        date_value = metadata_dict['date']
        
        # Check if it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value
            
        # It must be a string, try to convert it
        if isinstance(date_value, str):
            # Try different date formats
            for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%B %d, %Y'):
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    if parsed_date:
                        return parsed_date
                except ValueError:
                    continue
    except Exception as e:
        logger.error(f"Error extracting date from content: {str(e)}")
    
    # If all else fails, return the current date/time
    return result_date