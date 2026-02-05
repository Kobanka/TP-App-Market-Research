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
        "userName": review.get("userName"),
        "userImage": review.get("userImage"),
        "rating": review.get("rating"),
        "reviewCreatedVersion": review.get("reviewCreatedVersion"),
        "at": at,
        "content": review.get("content"),
        "score": review.get("score"),
        "thumbsUpCount": review.get("thumbsUpCount")
    }


def fetch_app_reviews(app_id, count=100):
    result, _ = reviews(
        app_id,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=count
    )
    return result


if __name__ == "__main__":

    query = "ai note taking applications"

    apps_metadata = []
    apps_reviews = {}

    # Search apps
    apps = search_apps(query, num_results=100)

    for app_info in apps:
        app_id = app_info["appId"]

        # Store app metadata
        metadata = {
            "appId": app_id,
            "title": app_info.get("title"),
            "developer": app_info.get("developer"),
            "score": app_info.get("score"),
            "ratings": app_info.get("ratings"),
            "installs": app_info.get("installs"),
            "genre": app_info.get("genre"),
            "url": app_info.get("url"),
            "price": app_info.get("price")
        }
        apps_metadata.append(metadata)

        # Fetch and store reviews
        reviews_data = fetch_app_reviews(app_id, count=50)
        apps_reviews[app_id] = [
            serialize_review(r) for r in reviews_data
        ]

    raw_dir = os.path.join("App Market Research", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    # Save metadata JSON
    apps_meta_path = os.path.join(raw_dir, "apps_metadata.json")
    with open(apps_meta_path, "w", encoding="utf-8") as f:
        json.dump(apps_metadata, f, indent=4, ensure_ascii=False)

    # Save reviews JSON
    apps_reviews_path = os.path.join(raw_dir, "apps_reviews.json")
    with open(apps_reviews_path, "w", encoding="utf-8") as f:
        json.dump(apps_reviews, f, indent=4, ensure_ascii=False)

    print(f"✅ Apps metadata saved to {apps_meta_path}")
    print(f"✅ Apps reviews saved to {apps_reviews_path}")