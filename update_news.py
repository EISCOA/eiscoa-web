import requests
from bs4 import BeautifulSoup
import re
import os

def update_news():
    # Usamos Xataka IA, que es mucho más estable y neutro
    url = "https://www.xataka.com/categoria/inteligencia-artificial"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al acceder a Xataka: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    # Xataka usa clases específicas para sus artículos
    articles = soup.find_all('article', class_='abstract-article')[:10]

    forbidden_keywords = ['musk', 'altman', 'política', 'democracia', 'juicio', 'trump', 'biden', 'ley', 'regulación']

    news_data = []
    for art in articles:
        if len(news_data) >= 3:
            break
            
        title_tag = art.select_one('.abstract-title a')
        if title_tag:
            title = title_tag.get_text().strip()
            link = title_tag['href']
            
            # Filtro de neutralidad
            if any(word in title.lower() for word in forbidden_keywords):
                continue
            
            # Intentar coger la imagen del artículo si existe, si no, Unsplash
            img_tag = art.select_one('img')
            img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else f"https://images.unsplash.com/featured/?technology,ai"
            
            news_data.append({
                "title": title,
                "link": link,
                "img": img_url
            })

    if not news_data:
        print("No se encontraron noticias válidas")
        return

    # Actualizar index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    new_grid_html = '    <div class="news-grid">\n'
    for i, item in enumerate(news_data):
        new_grid_html += f'''      <a class="news-card reveal" href="{item['link']}" target="_blank" rel="noopener noreferrer">
        <img class="news-img" src="{item['img']}"
          alt="{item['title']}" />
        <div class="news-body">
          <div class="news-tag" data-i18n="n{i+1}.tag">IA · Innovación</div>
          <div class="news-title" data-i18n="n{i+1}.title">{item['title']}</div>
        </div>
      </a>\n'''
    new_grid_html += '    </div>'

    content = re.sub(r'<div class="news-grid">.*?<\/div>', new_grid_html, content, flags=re.DOTALL)

    for i, item in enumerate(news_data):
        content = re.sub(rf"'n{i+1}\.title': '.*?'", f"'n{i+1}.title': '{item['title']}'", content)
        content = re.sub(rf"'n{i+1}\.tag': '.*?'", f"'n{i+1}.tag': 'IA · Innovación'", content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("¡Web actualizada con noticias de Xataka!")

if __name__ == "__main__":
    update_news()
