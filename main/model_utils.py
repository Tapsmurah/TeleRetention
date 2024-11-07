import pickle 
import pandas as pd # type: ignore
import numpy as np # type: ignore
import random

# Load the churn prediction model
with open('main/ml_models/churn_prediction_model.pkl', 'rb') as f:
    churn_model = pickle.load(f)

# Load the collaborative filtering model
with open('main/ml_models/recommendation_model.pkl', 'rb') as f:
    recommender_model = pickle.load(f)

interaction_df = pd.read_csv('main/ml_models/interaction_df.csv')

def predict_and_recommend(user_data):
    # Convert user_data into a DataFrame
    df = pd.DataFrame([user_data])

    ### Feature Engineering (before one-hot encoding)

    # 1. Engagement Score
    df['Engagement Score'] = (
        df['Total day minutes'] +
        df['Total eve minutes'] +
        df['Total night minutes'] +
        (df['Number vmail messages'] * 0.1)  # Weighting voicemail messages
    )

    # 2. Customer Lifetime Value (CLV)
    df['Customer Lifetime Value'] = (
        df['Total day charge'] +
        df['Total eve charge'] +
        df['Total night charge']
    )

    # 3. Average Monthly Charges
    df['Average Monthly Charge'] = df['Customer Lifetime Value'] / df['Tenure']
    df['Average Monthly Charge'] = df['Average Monthly Charge'].replace([np.inf, -np.inf], 0).fillna(0)

    # 4. Service Call Ratio
    total_calls = df[['Total day calls', 'Total eve calls', 'Total night calls']].sum(axis=1)
    df['Service Call Ratio'] = df['Customer service calls'] / total_calls
    df['Service Call Ratio'] = df['Service Call Ratio'].replace([np.inf, -np.inf], 0).fillna(0)

    # 5. Discounts Received and Discount Influence (simulating discounts)
    df['Discounts Received'] = 0  # Default to 0, since we don't have data
    df['Discount Influence'] = df['Discounts Received']  # Same as Discounts Received

    ### One-Hot Encoding for categorical variables (after feature engineering)
    df = pd.get_dummies(df, columns=['Gender', 'Location'], drop_first=True)

    ### Ensure All Expected Columns Exist
    expected_columns = [
        'Customer ID', 'Age', 'Senior Citizen', 'Tenure', 'Area code', 'Number vmail messages',
        'Total day minutes', 'Total day calls', 'Total day charge', 'Total eve minutes',
        'Total eve calls', 'Total eve charge', 'Total night minutes', 'Total night calls',
        'Total night charge', 'Total intl minutes', 'Total intl calls', 'Total intl charge',
        'Customer service calls', 'Gender_Male', 'Location_Harare', 'Location_Manicaland',
        'Location_Mashonaland Central', 'Location_Mashonaland East', 'Location_Mashonaland West',
        'Location_Masvingo', 'Location_Matabeleland North', 'Location_Matabeleland South',
        'Location_Midlands', 'International plan', 'Voice mail plan',
        'Engagement Score', 'Customer Lifetime Value', 'Average Monthly Charge',
        'Service Call Ratio', 'Discounts Received', 'Discount Influence'
    ]

    # Add missing columns with default value 0
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0

    # Ensure the DataFrame has the expected columns in correct order
    df = df[expected_columns]

    ### Predict Churn
    churn_proba = churn_model.predict_proba(df[expected_columns].values)[:, 1][0]

    ### Get Recommendations (if churn probability > 0.7)
    recommendations = None
    if churn_proba > 0.7:
        user_id = user_data['Customer ID']
        recommendations = get_top_n_recommendations(user_id, recommender_model, n=2, interaction_df=interaction_df)

    return churn_proba, recommendations

def get_top_n_recommendations(user_id, model, interaction_df, n=2):
    # Check if the user ID is part of the training set
    if user_id not in model.trainset._raw2inner_id_users:
        # Handle the case for new users
        all_products = interaction_df['Recommended Product'].unique()
        random_products = random.sample(list(all_products), n)
        return random_products

    # Proceed to get recommendations for existing users
    inner_id = model.trainset.to_inner_uid(user_id)
    recommendations = model.get_neighbors(inner_id, k=n)
    
    # Convert inner IDs back to raw IDs
    return [model.trainset.to_raw_iid(iid) for iid in recommendations]

def get_popular_products(interaction_df, n=5):
    """Get the top N popular products from interaction_df."""
    popular_products = interaction_df['Recommended Product'].value_counts().index[:n]
    return popular_products.tolist()

def get_hybrid_recommendations(user_id, interaction_df, knn_model, n=5):
    # Check if the user_id exists in the interaction_df for cold start detection
    if user_id not in interaction_df['Customer ID'].values:
        # Return popular products for new users
        return get_popular_products(interaction_df, n)

    # Get recommendations for existing users using the collaborative filtering model
    user_inner_id = knn_model.trainset.to_inner_uid(user_id)
    user_neighbors = knn_model.get_neighbors(user_inner_id, k=n)
    recommended_items = set()

    for neighbor in user_neighbors:
        neighbor_items = knn_model.trainset.ur[neighbor]
        recommended_items.update([knn_model.trainset.to_raw_iid(item_id) for item_id, _ in neighbor_items])
    
    # Return top N recommendations
    return list(recommended_items)[:n]
    