import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import csv
import json

# Конфигурация
KEYWORDS = ['дизайн', 'фото', 'web', 'python',
            'веб', 'frontend', 'backend', 'фотограф',
            'питон', 'пайтон', 'design', 'photography']

# RSS-ленты Хабра (можно выбрать одну или несколько)
RSS_FEEDS = {
    'ru_articles': 'https://habr.com/ru/rss/articles/?fl=ru',
    'en_articles': 'https://habr.com/en/rss/articles/?fl=en',
    'ru_top': 'https://habr.com/ru/rss/top/',
}


def contains_keyword(text, keywords):
    """Поиск ключевых слов в тексте с использованием регулярных выражений"""
    if not text:
        return False

    text_lower = text.lower()
    # Ищем ключевые слова как отдельные слова или части слов
    for keyword in keywords:
        if re.search(rf'\b{re.escape(keyword.lower())}\w*', text_lower):
            return True
    return False


def parse_date(date_string):
    """Парсинг даты из разных форматов"""
    if not date_string:
        return ""

    # Пытаемся распарсить разные форматы дат
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%d %b %Y'
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            return dt.strftime('%d.%m.%Y')
        except ValueError:
            continue

    return date_string[:10] if len(date_string) >= 10 else date_string


def parse_rss_feed(rss_url, max_articles=None):
    """Парсинг RSS-ленты"""
    print(f"Загружаем RSS-ленту: {rss_url}")

    try:
        response = requests.get(rss_url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # Парсим XML
        root = ET.fromstring(response.content)

        # Namespace для RSS
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'media': 'http://search.yahoo.com/mrss/'
        }

        # Находим все записи (статьи)
        articles = root.findall('.//item')
        if max_articles:
            articles = articles[:max_articles]

        print(f"Найдено статей: {len(articles)}")
        return articles, ns

    except Exception as e:
        print(f"Ошибка при загрузке RSS: {e}")
        return None, None


def analyze_article(article, ns):
    """Анализ одной статьи из RSS"""
    try:
        # Извлекаем базовую информацию
        title_elem = article.find('title')
        link_elem = article.find('link')

        if title_elem is None or link_elem is None:
            return None

        title = title_elem.text.strip() if title_elem.text else ""
        link = link_elem.text.strip() if link_elem.text else ""

        # Извлекаем дату
        date_elem = article.find('pubDate')
        if date_elem is None:
            date_elem = article.find('dc:date', ns)

        date_str = date_elem.text.strip() if date_elem is not None and date_elem.text else ""
        formatted_date = parse_date(date_str)

        # Извлекаем описание
        desc_elem = article.find('description')
        description = ""
        if desc_elem is not None and desc_elem.text:
            soup_desc = BeautifulSoup(desc_elem.text, 'html.parser')
            description = soup_desc.get_text().strip()

        # Извлекаем категории/теги
        categories = []
        for cat in article.findall('category'):
            if cat.text:
                categories.append(cat.text.strip())

        # Формируем текст для поиска ключевых слов
        search_text = f"{title} {description} {' '.join(categories)}".lower()

        return {
            'title': title,
            'link': link,
            'date': formatted_date,
            'date_raw': date_str,
            'description': description,
            'categories': categories,
            'search_text': search_text,
            'found_in_preview': contains_keyword(search_text, KEYWORDS)
        }

    except Exception as e:
        print(f"Ошибка при анализе статьи: {e}")
        return None


def get_full_article_text(url):
    """Получение полного текста статьи"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем основной текст статьи
        article_body = soup.find('div', {'class': 'tm-article-body'})

        if article_body:
            full_text = article_body.get_text().strip()
            return full_text

        # Альтернативный поиск для английской версии
        article_body_en = soup.find('article')
        if article_body_en:
            full_text = article_body_en.get_text().strip()
            return full_text

        return ""

    except Exception as e:
        print(f"Ошибка при загрузке полного текста: {e}")
        return ""


def save_results(results, format='console'):
    """Сохранение результатов в разных форматах"""
    if format == 'console':
        print("\n" + "=" * 100)
        print(f"{'РЕЗУЛЬТАТЫ ПОИСКА':^100}")
        print("=" * 100)

        if not results:
            print("Статьи по заданным ключевым словам не найдены.")
            return

        for idx, article in enumerate(results, 1):
            print(f"\n{idx}. {article['date']} – {article['title']}")
            print(f"   Ссылка: {article['link']}")
            if article['found_in_preview']:
                print("   ✓ Найдено в превью")
            else:
                print("   ✓ Найдено в полном тексте")
            if article.get('matched_keywords'):
                print(f"   Ключевые слова: {', '.join(article['matched_keywords'])}")
            print("-" * 100)

    elif format == 'csv':
        filename = f"habr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'title', 'link', 'found_in', 'keywords'])
            writer.writeheader()
            for article in results:
                writer.writerow({
                    'date': article['date'],
                    'title': article['title'],
                    'link': article['link'],
                    'found_in': 'preview' if article['found_in_preview'] else 'full_text',
                    'keywords': ', '.join(article.get('matched_keywords', []))
                })
        print(f"Результаты сохранены в {filename}")

    elif format == 'json':
        filename = f"habr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Результаты сохранены в {filename}")


def main():
    """Основная функция"""
    print("=" * 80)
    print("ПАРСЕР СТАТЕЙ С ХАБРА")
    print(f"Ключевые слова: {', '.join(KEYWORDS)}")
    print("=" * 80)

    all_results = []

    # Парсим RSS-ленту
    articles, ns = parse_rss_feed(RSS_FEEDS['ru_articles'], max_articles=20)

    if not articles:
        print("Не удалось загрузить статьи.")
        return

    print(f"\nАнализируем статьи...")

    for idx, article in enumerate(articles, 1):
        print(f"\rОбрабатываем статью {idx}/{len(articles)}...", end="")

        article_data = analyze_article(article, ns)
        if not article_data:
            continue

        # Проверяем ключевые слова в превью
        if article_data['found_in_preview']:
            article_data['matched_keywords'] = [
                kw for kw in KEYWORDS
                if contains_keyword(article_data['search_text'], [kw])
            ]
            all_results.append(article_data)
            continue

        # Если не найдено в превью, загружаем полный текст
        full_text = get_full_article_text(article_data['link'])
        if full_text:
            article_data['full_text'] = full_text
            if contains_keyword(full_text, KEYWORDS):
                article_data['matched_keywords'] = [
                    kw for kw in KEYWORDS
                    if contains_keyword(full_text, [kw])
                ]
                all_results.append(article_data)

        # Пауза между запросами
        time.sleep(0.5)

    print("\n" + "=" * 80)
    print(f"Анализ завершен. Найдено статей: {len(all_results)}")

    # Сохраняем результаты
    if all_results:
        save_results(all_results, format='console')
        save_results(all_results, format='csv')
        # save_results(all_results, format='json')  # раскомментировать для JSON
    else:
        print("\nСтатьи по заданным ключевым словам не найдены.")

        # Показываем примеры статей для проверки
        print("\nПримеры статей в RSS (первые 5):")
        for i, article in enumerate(articles[:5]):
            article_data = analyze_article(article, ns)
            if article_data:
                print(f"\n{i + 1}. {article_data['title']}")
                print(f"   Превью: {article_data['description'][:150]}...")

    print("\n" + "=" * 80)
    print("Работа программы завершена.")


if __name__ == "__main__":
    # Добавляем обработку Ctrl+C
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")