from google_play_scraper import Sort, reviews, search
import json
import os


def search_apps(query, num_results=100):
    return search(
        query,
        lang='en',
        country='us',
        n_hits=num_results
    )


def serialize_review(review):
    at = review.get("at")
    # Convert datetime to ISO string to keep JSON serializable
    if hasattr(at, "isoformat"):
        at = at.isoformat()

    return {
        "reviewId": review.get("reviewId"),
        "userName": review.get("userName"),
        "userImage": review.get("userImage"),
        "rating": review.get("rating"),
        "reviewCreatedVersion": review.get("reviewCreatedVersion"),
        "at": at,
        "content": review.get("content"),
        "score": review.get("score"),
        "thumbsUpCount": review.get("thumbsUpCount")
    }


def fetch_app_reviews(app_id, max_reviews=500):
    """
    Fetch app reviews using continuation tokens to get as much data as possible.
    
    """
    all_reviews = []
    continuation_token = None
    
    while len(all_reviews) < max_reviews:
        try:
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=min(200, max_reviews - len(all_reviews)),  # Fetch up to 200 at a time
                continuation_token=continuation_token
            )
            
            if not result:
                break
                
            all_reviews.extend(result)
            
            # If no continuation token, we've reached the end
            if not continuation_token:
                break
                
        except Exception as e:
            print(f"⚠️  Error fetching reviews for {app_id}: {e}")
            break
    
    return all_reviews


if __name__ == "__main__":

    query = "ai note taking applications"

    # Create output directory
    raw_dir = os.path.join("App Market Research", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    apps_meta_path = os.path.join(raw_dir, "apps_metadata.json")
    apps_reviews_path = os.path.join(raw_dir, "apps_reviews.json")

    # Initialize files (overwrite if exists)
    with open(apps_meta_path, "w", encoding="utf-8") as f:
        json.dump([], f)
    
    with open(apps_reviews_path, "w", encoding="utf-8") as f:
        json.dump({}, f)

    # Search apps
    apps = search_apps(query, num_results=100)
    total_apps = len(apps)
    
    print(f"Found {total_apps} apps. Starting data collection...")

    for idx, app_info in enumerate(apps, 1):
        app_id = app_info["appId"]
        app_title = app_info.get("title", "Unknown")
        
        print(f"\n[{idx}/{total_apps}] Processing: {app_title} ({app_id})")

        # Prepare app metadata
        metadata = {
            "appId": app_id,
            "title": app_title,
            "developer": app_info.get("developer"),
            "score": app_info.get("score"),
            "ratings": app_info.get("ratings"),
            "installs": app_info.get("installs"),
            "genre": app_info.get("genre"),
            "url": app_info.get("url"),
            "price": app_info.get("price")
        }

        # Fetch reviews with continuation tokens
        reviews_data = fetch_app_reviews(app_id, max_reviews=500)
        print(f"   Fetched {len(reviews_data)} reviews")
        
        serialized_reviews = [serialize_review(r) for r in reviews_data]

        # Append metadata immediately (crash-safe)
        with open(apps_meta_path, "r", encoding="utf-8") as f:
            apps_metadata = json.load(f)
        apps_metadata.append(metadata)
        with open(apps_meta_path, "w", encoding="utf-8") as f:
            json.dump(apps_metadata, f, indent=4, ensure_ascii=False)

        # Append reviews immediately (crash-safe)
        with open(apps_reviews_path, "r", encoding="utf-8") as f:
            apps_reviews = json.load(f)
        apps_reviews[app_id] = serialized_reviews
        with open(apps_reviews_path, "w", encoding="utf-8") as f:
            json.dump(apps_reviews, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Apps metadata saved to {apps_meta_path}")
    print(f"✅ Apps reviews saved to {apps_reviews_path}")
    print(f"✅ Total apps processed: {total_apps}")