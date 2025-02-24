from bs4 import BeautifulSoup

def extract_all_links(html, date):
    """Extract all the news from the response."""
    soup = BeautifulSoup(html, 'html.parser')
    news = []
    for tr in soup.find_all("tr", class_="athing"):
        news.append(extract_one_link(str(tr) + str(tr.find_next_sibling("tr")), date))
    return news

def extract_one_link(html, date):
    """Extract the news from the response."""
    soup = BeautifulSoup(html, 'html.parser')

    result = {}
    # Extract rank (removing the trailing dot and converting to int)
    rank_text = soup.find("span", class_="rank").get_text(strip=True).replace(".", "")
    result['rank'] = int(rank_text)

    # Extract title and url
    titleline = soup.find("span", class_="titleline")
    link = titleline.find("a")
    result['title'] = link.get_text(strip=True)
    result['url'] = link.get("href")

    # Extract author, points, created_at and comments from the subtext row
    subtext = soup.find("td", class_="subtext")

    # Points
    score_tag = subtext.find("span", class_="score")
    if score_tag:
        points_text = score_tag.get_text(strip=True).split()[0]
        result['points'] = int(points_text)
    else:
        result['points'] = 0

    # Author
    author_tag = subtext.find("a", class_="hnuser")
    result['author'] = author_tag.get_text(strip=True) if author_tag else None

    # Created_at (from the title attribute of the age span)
    age_tag = subtext.find("span", class_="age")
    result['created_at'] = age_tag.get("title") if age_tag and age_tag.has_attr("title") else None

    # Comments: find the link that contains the word "comment"
    comment_link = subtext.find("a", string=lambda text: text and "comment" in text.lower())
    if comment_link:
        comments_text = comment_link.get_text(strip=True).split()[0]
        result['comments'] = int(comments_text)
    else:
        result['comments'] = 0

    result["partition_date"] = date
    return result