import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# Đọc dữ liệu đã crawl
df = pd.read_csv("results.csv")

# Chọn các cột số để phân cụm
numeric_df = df.select_dtypes(include=['number']).copy()

# Loại bỏ các hàng thiếu dữ liệu
numeric_df.dropna(inplace=True)

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
scaled_data = scaler.fit_transform(numeric_df)

# Dùng phương pháp Elbow để xác định số cluster tối ưu
sse = []
K_range = range(2, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(scaled_data)
    sse.append(km.inertia_)

plt.figure(figsize=(6,4))
plt.plot(K_range, sse, marker='o')
plt.title('Elbow Method - SSE vs K')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('SSE (Inertia)')
plt.grid()
plt.show()

# Chọn số cụm tối ưu từ biểu đồ, ví dụ k = 4
k_optimal = 4
kmeans = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
labels = kmeans.fit_predict(scaled_data)

# Giảm chiều bằng PCA
pca = PCA(n_components=2)
reduced_data = pca.fit_transform(scaled_data)

# Vẽ biểu đồ các nhóm cầu thủ sau phân cụm
plt.figure(figsize=(8,6))
scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='viridis', s=30)
plt.title(f'Player Clusters (k={k_optimal}) via PCA')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.colorbar(scatter, label='Cluster')
plt.grid(True)
plt.show()
