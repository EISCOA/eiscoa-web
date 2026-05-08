import requests
from bs4 import BeautifulSoup
import re
import os

def update_news():
    # Usamos MIT Technology Review en español
    url = "https://technologyreview.es/temas/inteligencia-artificial"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al acceder a Technology Review: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    # MIT Technology Review usa h3 para los títulos de los artículos en la lista
    articles = soup.find_all('article')
    if not articles:
        # Intento alternativo si la estructura cambia
        articles = soup.select('div.views-row')

    forbidden_keywords = ['musk', 'altman', 'política', 'democracia', 'juicio', 'trump', 'biden', 'ley', 'regulación', 'tribunales', 'demanda']

    news_data = []
    # En la versión simplificada de la web, buscamos los H3 y sus enlaces
    for item in soup.find_all('h3'):
        if len(news_data) >= 3:
            break
            
        title = item.get_text().strip()
        link_tag = item.find_parent('a') or item.find('a')
        
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://technologyreview.es" + link
            
            # Filtro de neutralidad
            if any(word in title.lower() for word in forbidden_keywords):
                continue
            
            news_data.append({
                "title": title,
                "link": link
            })

    if not news_data:
        print("No se encontraron noticias válidas")
        return

    # Actualizar index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Nota: Como ahora usamos imágenes generadas manualmente por el usuario (Antigravity), 
    # el script debería mantener las imágenes o permitir actualizarlas. 
    # Para este ejercicio, actualizaremos solo textos y enlaces, manteniendo la estructura.
    
    # Re-escribir el grid completo es más seguro
    new_grid_html = '    <div class="news-grid">\n'
    # Map of images (para mantener las que generamos)
    imgs = ["news_llm_debug_v2.png", "news_deepseek_v4.png", "news_ai_data_value.png"]
    tags = ["IA · Desarrollo", "IA · Eficiencia", "IA · Empresa"]
    
    for i, item in enumerate(news_data):
        img = imgs[i] if i < len(imgs) else "news_ai_adoption.png"
        tag = tags[i] if i < len(tags) else "IA · Innovación"
        new_grid_html += f'''      <a class="news-card reveal" href="{item['link']}" target="_blank" rel="noopener noreferrer">
        <img class="news-img" src="{img}"
          alt="{item['title']}" />
        <div class="news-body">
          <div class="news-tag" data-i18n="n{i+1}.tag">{tag}</div>
          <div class="news-title" data-i18n="n{i+1}.title">{item['title']}</div>
        </div>
      </a>\n'''
    new_grid_html += '    </div>'

    content = re.sub(r'<div class="news-grid">.*?<\/div>', new_grid_html, content, flags=re.DOTALL)

    # Actualizar traducciones específicas en el archivo
    for i, item in enumerate(news_data):
        content = re.sub(rf"'n{i+1}\.title': '.*?'", f"'n{i+1}.title': '{item['title']}'", content)
        content = re.sub(rf"'n{i+1}\.tag': '.*?'", f"'n{i+1}.tag': '{tags[i] if i < len(tags) else 'IA · Innovación'}'", content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"¡Web actualizada con noticias de Technology Review! ({len(news_data)} noticias)")

if __name__ == "__main__":
    update_news()
