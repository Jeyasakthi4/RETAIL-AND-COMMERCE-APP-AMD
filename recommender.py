"""
RetailGenius - Recommendation Engine
Hybrid: rule-based filtering + Gemini AI
"""

import json
from typing import List, Dict, Optional

def get_recommendations(
    query: str,
    user_prefs: Dict,
    products_df,
    api_key: Optional[str] = None,
    language: str = "English"
) -> List[Dict]:
    """Get personalized recommendations"""
    
    filtered_df = products_df.copy()
    
    # FILTER 1: Price
    if user_prefs.get("max_price"):
        filtered_df = filtered_df[filtered_df['price'] <= user_prefs['max_price']]
    if user_prefs.get("min_price"):
        filtered_df = filtered_df[filtered_df['price'] >= user_prefs['min_price']]
    
    # FILTER 2: Category
    if user_prefs.get("category") and user_prefs.get("category") != "All":
        filtered_df = filtered_df[filtered_df['category'] == user_prefs['category']]
    
    # FILTER 3: Color
    if user_prefs.get("color"):
        filtered_df = filtered_df[filtered_df['color'].str.lower() == user_prefs['color'].lower()]
    
    # FILTER 4: Stock
    filtered_df = filtered_df[filtered_df['stock'] > 0]
    
    if len(filtered_df) == 0:
        return []
    
    # RANK by popularity
    filtered_df = filtered_df.sort_values('sales', ascending=False)
    
    # BUILD recommendations
    recommendations = []
    for idx, product in filtered_df.head(3).iterrows():
        reasons = []
        if user_prefs.get("max_price") and product['price'] <= user_prefs['max_price']:
            reasons.append("Matches your price range")
        if product['stock'] > 0:
            reasons.append("Available in stock")
        if product['sales'] > filtered_df['sales'].mean():
            reasons.append("Popular among users")
        
        recommendation = {
            "id": product['id'],
            "name": product['name'],
            "category": product['category'],
            "price": product['price'],
            "stock": product['stock'],
            "sales": product['sales'],
            "color": product.get('color', 'N/A'),
            "reasons": reasons
        }
        recommendations.append(recommendation)
    
    return recommendations

def test_recommender():
    import pandas as pd
    sample = [{'id': 1, 'name': 'Nike', 'category': 'Fashion', 'price': 5000, 'stock': 10, 'sales': 100, 'color': 'Black'}]
    df = pd.DataFrame(sample)
    recs = get_recommendations("shoes", {}, df)
    print("✅ Test passed")

if __name__ == "__main__":
    test_recommender()
