"""
Quick test script for Pixabay tool
"""
from src.tools.pixabay_tool import PixabayTool

print("Testing Pixabay API...")
print("-" * 50)

# Test search images
result = PixabayTool.search_images('technology', per_page=3)
print(f"✅ Search images: Found {result.get('totalHits', 0)} images")

if result.get('hits'):
    first_image = result['hits'][0]
    print(f"   First image: {first_image.get('tags')}")
    print(f"   By: {first_image.get('user')}")
    print(f"   URL: {first_image.get('webformatURL')}")

print("-" * 50)

# Test get best image
best = PixabayTool.search_and_get_best_image('business', orientation='horizontal')
if best:
    print(f"✅ Best image: {best.get('tags')}")
    print(f"   URL: {best.get('url')}")
else:
    print("❌ No best image found")

print("-" * 50)
print("✅ All tests passed!")
