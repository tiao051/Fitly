import requests
import csv
import time
import os
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "gymer_foods.csv")

if not API_KEY:
    print("❌ API_KEY not found in .env file")
    exit(1)

food_keywords = [
    # Protein sources chưa có
    "bison", "elk", "quail", "pheasant", "goose", "ostrich",
    "sea urchin", "octopus", "squid", "eel", "catfish", "flounder",
    "protein bar", "casein protein", "hemp protein", "pea protein",
    "tempeh", "seitan", "nutritional yeast", "spirulina",
    
    # Dairy & alternatives chưa có
    "kefir", "buttermilk", "heavy cream", "half and half",
    "blue cheese", "brie cheese", "camembert cheese", "swiss cheese",
    "provolone cheese", "monterey jack cheese", "pepper jack cheese",
    "cashew milk", "macadamia milk", "pea milk", "hemp milk",
    
    # Grains & starches chưa có
    "amaranth", "teff", "spelt", "kamut", "farro", "freekeh",
    "plantain", "yuca", "cassava", "taro", "parsnip", "rutabaga",
    "polenta", "grits", "bulgur", "wheat berries", "steel cut oats",
    
    # Fruits chưa có
    "papaya", "guava", "passion fruit", "dragon fruit", "lychee",
    "pomegranate", "persimmon", "star fruit", "jackfruit", "durian",
    "elderberry", "goji berries", "acai", "cranberries", "mulberries",
    "apricot", "nectarine", "cherry", "pear", "coconut",
    
    # Vegetables chưa có
    "artichoke", "fennel", "leeks", "shallots", "scallions",
    "bok choy", "cabbage", "collard greens", "turnip greens",
    "watercress", "endive", "radicchio", "butternut squash",
    "acorn squash", "spaghetti squash", "delicata squash",
    "eggplant", "okra", "jicama", "kohlrabi", "radish",
    
    # Nuts & seeds chưa có
    "macadamia nuts", "pine nuts", "chestnuts", "coconut flakes",
    "poppy seeds", "fennel seeds", "cumin seeds", "coriander seeds",
    "mustard seeds", "caraway seeds", "nigella seeds",
    
    # Oils & fats chưa có
    "sesame oil", "walnut oil", "flaxseed oil", "hemp oil",
    "grapeseed oil", "sunflower oil", "safflower oil", "canola oil",
    "coconut cream", "tahini", "almond butter", "sunflower butter",
    "macadamia butter", "hazelnut butter",
    
    # Beverages chưa có
    "kombucha", "coconut water", "bone broth", "vegetable broth",
    "green tea", "black tea", "matcha", "herbal tea",
    "espresso", "cold brew", "energy drink", "electrolyte drink",
    
    # Condiments & seasonings chưa có
    "balsamic vinegar", "apple cider vinegar", "rice vinegar",
    "soy sauce", "tamari", "miso", "fish sauce", "oyster sauce",
    "harissa", "sriracha", "hot sauce", "salsa", "pesto",
    "hummus", "guacamole", "tzatziki", "ranch dressing",
    
    # Sweeteners chưa có
    "coconut sugar", "date sugar", "brown sugar", "raw sugar",
    "molasses", "corn syrup", "rice syrup", "yacon syrup",
    "erythritol", "xylitol", "sucralose", "aspartame"
]

wanted_nutrients = [
    "Energy (Atwater General Factors)",
    "Protein",
    "Carbohydrate, by difference",
    "Total lipid (fat)"
]

headers = ["name", "fdc_id", "calories_kcal", "protein_g", "carb_g", "fat_g"]

# Kiểm tra file CSV có tồn tại không, nếu chưa thì tạo và ghi header
if not os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
    print(f"📄 Created new CSV file: {OUTPUT_CSV}")
else:
    print(f"📄 Found existing CSV file: {OUTPUT_CSV} - appending data...")

# Thread-safe queue để lưu kết quả
result_queue = queue.Queue()
write_lock = threading.Lock()

# Session để tái sử dụng connection
session = requests.Session()
session.headers.update({"User-Agent": "Food-Crawler/1.0"})

def process_food_detail(food_data):
    """Xử lý chi tiết 1 food item"""
    fdc_id, name = food_data
    
    try:
        detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={API_KEY}"
        detail_res = session.get(detail_url, timeout=8)
        detail_res.raise_for_status()
        detail_data = detail_res.json()
    except requests.RequestException as e:
        print(f"❌ Detail error for '{name}': {e}")
        return None

    nutrients = {}
    for nutrient in detail_data.get("foodNutrients", []):
        n = nutrient.get("nutrient", {})
        name_n = n.get("name")
        if name_n in wanted_nutrients:
            nutrients[name_n] = nutrient.get("amount", None)

    row = {
        "name": name,
        "fdc_id": fdc_id,
        "calories_kcal": nutrients.get("Energy (Atwater General Factors)"),
        "protein_g": nutrients.get("Protein"),
        "carb_g": nutrients.get("Carbohydrate, by difference"),
        "fat_g": nutrients.get("Total lipid (fat)")
    }

    # Chỉ trả về nếu có ít nhất 1 dữ liệu dinh dưỡng
    if any(value is not None for value in row.values() if isinstance(value, (int, float))):
        return row
    return None

def process_keyword(keyword):
    """Xử lý 1 keyword tìm kiếm"""
    print(f"🔍 Crawling: {keyword}")
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={keyword}&api_key={API_KEY}&pageSize=3"

    try:
        res = session.get(search_url, timeout=8)
        res.raise_for_status()
        foods = res.json().get("foods", [])
    except requests.RequestException as e:
        print(f"❌ Search error for '{keyword}': {e}")
        return []

    # Tạo list các food items để xử lý
    food_items = [(food["fdcId"], food["description"]) for food in foods]
    
    # Xử lý parallel các food details
    results = []
    with ThreadPoolExecutor(max_workers=3) as detail_executor:
        detail_futures = [detail_executor.submit(process_food_detail, item) for item in food_items]
        
        for future in as_completed(detail_futures):
            result = future.result()
            if result:
                results.append(result)
                print(f"✅ Saved: {result['name']}")
    
    return results

# Mở file CSV để append data
csv_file = open(OUTPUT_CSV, "a", newline="", encoding="utf-8")
csv_writer = csv.DictWriter(csv_file, fieldnames=headers)

print(f"🚀 Starting crawl with {len(food_keywords)} keywords...")
start_time = time.time()

# Xử lý parallel các keywords
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_keyword, keyword) for keyword in food_keywords]
    
    for future in as_completed(futures):
        results = future.result()
        
        # Thread-safe write to CSV
        with write_lock:
            for row in results:
                csv_writer.writerow(row)
                csv_file.flush()
        
        time.sleep(0.1)  # Giảm delay xuống 0.1s

csv_file.close()
session.close()

end_time = time.time()
print(f"✅ Done in {end_time - start_time:.2f} seconds. File saved to: {OUTPUT_CSV}")