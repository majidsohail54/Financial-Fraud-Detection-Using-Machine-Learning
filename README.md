RUN THIS PROJECT NEED REQURIMENTS.

DOWNLOAD PostgreSQL.

link:https://www.postgresql.org/download/


After install the sql . you need the add the tables one by one.


1st table.

CREATE TABLE transactions1 (
  transaction_id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- PCA features V1–V28 (anonymised in original dataset)
  v1 DOUBLE PRECISION, v2 DOUBLE PRECISION,
  v3 DOUBLE PRECISION, v4 DOUBLE PRECISION,
  v5 DOUBLE PRECISION, v6 DOUBLE PRECISION,
  v7 DOUBLE PRECISION, v8 DOUBLE PRECISION,
  v9 DOUBLE PRECISION, v10 DOUBLE PRECISION,
  v11 DOUBLE PRECISION, v12 DOUBLE PRECISION,
  v13 DOUBLE PRECISION, v14 DOUBLE PRECISION,
  v15 DOUBLE PRECISION, v16 DOUBLE PRECISION,
  v17 DOUBLE PRECISION, v18 DOUBLE PRECISION,
  v19 DOUBLE PRECISION, v20 DOUBLE PRECISION,
  v21 DOUBLE PRECISION, v22 DOUBLE PRECISION,
  v23 DOUBLE PRECISION, v24 DOUBLE PRECISION,
  v25 DOUBLE PRECISION, v26 DOUBLE PRECISION,
  v27 DOUBLE PRECISION, v28 DOUBLE PRECISION,

  amount NUMERIC(12, 2) NOT NULL,
  actual_class SMALLINT NOT NULL CHECK (actual_class IN (0, 1)),

  -- Split membership (for reproducibility)
  split_set VARCHAR(10) NOT NULL CHECK (split_set IN ('train', 'test'))
);


2nd table

CREATE TABLE model_predictions (
  prediction_id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT NOT NULL REFERENCES transactions1(transaction_id),

  model_name VARCHAR(50) NOT NULL CHECK (
    model_name IN ('logistic_regression', 'decision_tree', 'random_forest')
  ),

  predicted_class SMALLINT NOT NULL CHECK (predicted_class IN (0, 1)),
  fraud_probability DOUBLE PRECISION CHECK (fraud_probability BETWEEN 0 AND 1),
  predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_predictions_txn ON model_predictions(transaction_id);
CREATE INDEX idx_predictions_model ON model_predictions(model_name);


3rd table


CREATE TABLE model_metrics (
  metric_id BIGSERIAL PRIMARY KEY,
  model_name VARCHAR(50) NOT NULL,
  run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  accuracy DOUBLE PRECISION,
  precision_score DOUBLE PRECISION,
  recall_score DOUBLE PRECISION,
  f1_score DOUBLE PRECISION,

  random_state INTEGER,
  test_size DOUBLE PRECISION,
  smote_applied BOOLEAN NOT NULL DEFAULT TRUE
);

4th table

CREATE TABLE feature_importance (
  importance_id BIGSERIAL PRIMARY KEY,
  metric_id BIGINT REFERENCES model_metrics(metric_id),
  feature_name VARCHAR(10) NOT NULL,
  importance_score DOUBLE PRECISION NOT NULL,
  rank SMALLINT
);



after adding this table.

1.first go the terminal new terminal.
2.type in the terminal cd project
3.after that type python model.py
4. pip install uvicorn
5.after that type python -m uvicorn main:app --reload
6. after that in the side of the terminal you can see the (downARROW) symbol . then click that you can see the (command prompt) click it.
7.then type npm run dev.
8. this is overall project to run this working.




NOTICE: If this steps are not working . because you didn't install any libraries in the vs code check that fix it and run it.  
