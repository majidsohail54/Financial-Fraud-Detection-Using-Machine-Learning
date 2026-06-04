# =========================
# 1. Import Libraries
# =========================
import os
from pathlib import Path
import psycopg2
import pandas as pd
import pickle
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# =========================
# 2. Load Model
# =========================
here = Path(__file__).resolve().parent
model = pickle.load(open(here / "fraud_model.pkl", "rb"))

# =========================
# 3. Connect Database
# =========================
conn = psycopg2.connect(
    database=os.getenv("DB_NAME", "fraud_detection"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "Majid@2005"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)

cursor = conn.cursor()

def ensure_table(cursor, table_name, required_columns, create_sql):
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=%s",
        (table_name,)
    )
    existing_columns = [row[0] for row in cursor.fetchall()]

    if not all(col in existing_columns for col in required_columns):
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(create_sql)
        conn.commit()

ensure_table(
    cursor,
    "model_predictions",
    ["transaction_id", "model_name", "predicted_class"],
    """
    CREATE TABLE model_predictions (
        prediction_id SERIAL PRIMARY KEY,
        transaction_id INTEGER,
        model_name TEXT,
        predicted_class INTEGER,
        fraud_probability FLOAT,
        predicted_at TIMESTAMP DEFAULT NOW()
    )
    """
)
ensure_table(
    cursor,
    "model_metrics",
    ["model_name", "accuracy"],
    """
    CREATE TABLE model_metrics (
        metric_id SERIAL PRIMARY KEY,
        model_name TEXT,
        accuracy FLOAT,
        recorded_at TIMESTAMP DEFAULT NOW()
    )
    """
)
print("✅ Connected to Database")

# =========================
# 4. Fetch REAL TEST DATA (Better than 10 rows)
# =========================
query = """
SELECT * FROM transactions1
WHERE split_set = 'test'
LIMIT 1000
"""

df = pd.read_sql(query, conn)

print("\nData fetched:", df.shape)

# =========================
# 5. Fix Column Names
# =========================
df.columns = df.columns.str.capitalize()
df.rename(columns={"Actual_class": "Class"}, inplace=True)

# =========================
# 6. Add Missing Feature
# =========================
df["Time"] = 0

# =========================
# 7. Prepare Features
# =========================
feature_cols = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

X = df[feature_cols]
y_true = df["Class"]

# =========================
# 8. Predict
# =========================
predictions = model.predict(X)

# =========================
# 9. Show Sample Results
# =========================
print("\n🔍 Sample Prediction Results:\n")

for i in range(10):   # show first 10 only
    actual = "⚠️ Fraud" if y_true.iloc[i] == 1 else "✅ Legitimate"
    predicted = "⚠️ Fraud" if predictions[i] == 1 else "✅ Legitimate"

    print(f"Transaction {i+1}: Actual = {actual} | Predicted = {predicted}")

# =========================
# 10. Evaluation Metrics
# =========================
accuracy = accuracy_score(y_true, predictions)

print("\n📊 Accuracy:", accuracy)
print("\n📉 Confusion Matrix:\n", confusion_matrix(y_true, predictions))
print("\n📋 Classification Report:\n", classification_report(y_true, predictions))

print("Total Fraud (Actual):", sum(y_true))
print("Total Fraud (Predicted):", sum(predictions))

# =========================
# 11. Store Predictions
# =========================
for i in range(len(predictions)):
    cursor.execute("""
        INSERT INTO model_predictions (transaction_id, model_name, predicted_class)
        VALUES (%s, %s, %s)
    """, (
        int(df.iloc[i]["Transaction_id"]),
        "random_forest",
        int(predictions[i])
    ))

conn.commit()
print("\n✅ Predictions stored")

# =========================
# 12. Store Accuracy
# =========================
cursor.execute("""
    INSERT INTO model_metrics (model_name, accuracy)
    VALUES (%s, %s)
""", ("random_forest", float(accuracy)))

conn.commit()

# =========================
# 13. Close Connection
# =========================
conn.close()