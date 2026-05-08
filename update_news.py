import requests
from bs4 import BeautifulSoup
import re
import os

def update_news():
    # Usamos la URL correcta del dominio global en español
    url = "https://es.technologyreview.com/ia"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al acceder a la web: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    # Escaneamos más artículos para tener de dónde elegir tras filtrar
    all_articles = soup.find_all('article')[:15]

    # Palabras a evitar para mantener la neutralidad
    forbidden_keywords = ['musk', 'altman', 'democracia', 'política', 'juicio', 'voto', 'elecciones', 'trump', 'biden']

    news_data = []
    for art in all_articles:
        if len(news_data) >= 3:
            break
            
        title_tag = art.select_one('h2') or art.select_one('h3')
        link_tag = art.select_one('a')
        
        if title_tag and link_tag:
            title = title_tag.get_text().strip()
            # Filtro de neutralidad: si contiene alguna palabra prohibida, saltamos la noticia
            if any(word in title.lower() for word in forbidden_keywords):
                continue

            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://es.technologyreview.com" + link
            
            # Palabra clave para la imagen (limpiamos un poco el título)
            keyword = re.sub(r'[^\w\s]', '', title).split()[0].lower() if len(title.split()) > 0 else "technology"
            img_url = f"https://images.unsplash.com/featured/?technology,{keyword}"
            
            news_data.append({
                "title": title,
                "link": link,
                "img": img_url
            })

    if len(news_data) < 3:
        print("No se encontraron suficientes noticias")
        return

    # Leer el archivo index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Actualizar el News Grid en el HTML
    # Buscamos el bloque <div class="news-grid">...</div>
    new_grid_html = '    <div class="news-grid">\n'
    for i, item in enumerate(news_data):
        new_grid_html += f'''      <a class="news-card reveal" href="{item['link']}" target="_blank" rel="noopener noreferrer">
        <img class="news-img" src="{item['img']}"
          alt="{item['title']}" />
        <div class="news-body">
          <div class="news-tag" data-i18n="n{i+1}.tag">IA · Actualidad</div>
          <div class="news-title" data-i18n="n{i+1}.title">{item['title']}</div>
        </div>
      </a>\n'''
    new_grid_html += '    </div>'

    content = re.sub(r'<div class="news-grid">.*?<\/div>', new_grid_html, content, flags=re.DOTALL)

    # 2. Actualizar el objeto de traducciones (Español)
    for i, item in enumerate(news_data):
        # Actualizar nX.title en español
        pattern = rf"'n{i+1}\.title': '.*?'"
        replacement = f"'n{i+1}.title': '{item['title']}'"
        content = re.sub(pattern, replacement, content)
        
        # También actualizamos el tag a algo genérico
        pattern_tag = rf"'n{i+1}\.tag': '.*?'"
        replacement_tag = f"'n{i+1}.tag': 'IA · Actualidad'"
        content = re.sub(pattern_tag, replacement_tag, content)

    # Guardar los cambios
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("¡Web actualizada con éxito!")

if __name__ == "__main__":
    update_news()
