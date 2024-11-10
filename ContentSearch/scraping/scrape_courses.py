import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://courses.analyticsvidhya.com"
FREE_COURSES_URL = f"{BASE_URL}/pages/all-free-courses"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Retry limit to stop the scraping if no data is returned after multiple attempts
MAX_EMPTY_RESPONSES = 3
RETRY_LIMIT = 2  # Number of retries per page before moving on


async def fetch_course_list(session, page=1):
    url = f"{FREE_COURSES_URL}?page={page}"
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                print(f"Error fetching page {page}. Status code: {response.status}")
                return None

            soup = BeautifulSoup(await response.text(), 'html.parser')
            courses = []

            course_cards = soup.find_all('li', class_='course-cards__list-item')
            if not course_cards:
                print(f"No course data found on page {page}.")
                return None

            for card in course_cards:
                title_tag = card.find('h3')
                link_tag = card.find('a', class_='course-card')
                image_tag = card.find('img', class_='course-card__img')

                if title_tag and link_tag and image_tag:
                    course = {
                        'title': title_tag.text.strip(),
                        'link': BASE_URL + link_tag['href'],
                        'image': image_tag['src']
                    }
                    courses.append(course)
            return courses
    except Exception as e:
        print(f"Error fetching data from page {page}: {e}")
        return None


async def fetch_course_details(session, course):
    try:
        async with session.get(course['link'], headers=HEADERS) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')

            description_tag = soup.find('div', class_='course-description')
            course['description'] = description_tag.text.strip() if description_tag else 'No description available'
            return course
    except Exception as e:
        print(f"Error fetching details for course {course['title']}: {e}")
        return course


async def scrape_all_courses():
    all_courses = []
    page = 1
    empty_response_count = 0
    retry_count = 0

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    async with aiohttp.ClientSession() as session:
        while True:
            courses = await fetch_course_list(session, page)

            if not courses:
                empty_response_count += 1
                retry_count += 1
                if retry_count >= RETRY_LIMIT:
                    print(f"Skipping page {page} after {RETRY_LIMIT} retries.")
                    retry_count = 0  # Reset retry count
                    page += 1
                    await asyncio.sleep(2)  # Wait before moving to the next page
                    continue

                if empty_response_count >= MAX_EMPTY_RESPONSES:
                    print(f"Stopping scraping after {MAX_EMPTY_RESPONSES} empty responses.")
                    break

                print(f"Waiting for more data. {MAX_EMPTY_RESPONSES - empty_response_count} attempts left.")
                await asyncio.sleep(2)
                continue

            empty_response_count = 0
            print(f"Fetched {len(courses)} courses from page {page}.")

            tasks = [asyncio.ensure_future(fetch_course_details(session, course)) for course in courses]
            completed_courses = await asyncio.gather(*tasks)
            all_courses.extend(completed_courses)

            page += 1
            await asyncio.sleep(1)

    if all_courses:
        with open('courses_data.json', 'w') as f:
            json.dump(all_courses, f, indent=4)
        print(f"Scraping completed successfully. Total {len(all_courses)} courses scraped.")
    else:
        print("No courses were scraped.")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(scrape_all_courses())
    print(f"Scraping completed in {time.time() - start_time} seconds.")
