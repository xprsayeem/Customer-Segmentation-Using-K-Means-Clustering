"""
Customer Segmentation Using K-Means Clustering
Dataset: Online Retail (UCI Machine Learning Repository)
Author: Sayeem Mahfuz
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# =============================================================================
# STEP 1: Load and Preprocess Data
# =============================================================================

# Load data from same directory as script
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, 'Online_Retail.csv'), encoding='UTF-8')
print(f"Raw data: {len(df)} records")

# Preprocessing: remove missing CustomerIDs, cancellations, and invalid values
df = df.dropna(subset=['CustomerID'])
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
df['CustomerID'] = df['CustomerID'].astype(int)
print(f"Clean data: {len(df)} records, {df['CustomerID'].nunique()} customers")

# =============================================================================
# STEP 2: Create RFM Features
# =============================================================================

# Snapshot date = day after last transaction (our reference "today")
snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

# Aggregate by customer to create RFM metrics
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,  # Recency: days since last purchase
    'InvoiceNo': 'nunique',                                    # Frequency: number of transactions
    'TotalPrice': 'sum'                                        # Monetary: total spend
}).reset_index()
rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

print(f"\nRFM Features:\n{rfm.describe().round(2)}")

# =============================================================================
# STEP 3: Scale Features
# =============================================================================

# Log transform (reduces skewness) + StandardScaler (normalizes for K-Means)
rfm_log = np.log1p(rfm[['Recency', 'Frequency', 'Monetary']])
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log)

# =============================================================================
# STEP 4: K-Means Clustering
# =============================================================================

k = 4  # Number of clusters
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# Display cluster profiles
print(f"\nCluster Profiles (K={k}):")
print(rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().round(2))

# =============================================================================
# STEP 5: Visualize Results
# =============================================================================

plt.figure(figsize=(10, 6))
scatter = plt.scatter(rfm['Frequency'], rfm['Monetary'], c=rfm['Cluster'], cmap='viridis', alpha=0.6)
plt.xlabel('Frequency (Number of Purchases)')
plt.ylabel('Monetary (Total Spend £)')
plt.title('Customer Segments')
plt.colorbar(scatter, label='Cluster')
plt.savefig('clusters.png', dpi=150)
plt.show()

# Save results
rfm.to_csv('customer_segments.csv', index=False)
print("\nSaved: clusters.png, customer_segments.csv")
