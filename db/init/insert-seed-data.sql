-- db/init/02-insert-seed-data.sql
INSERT INTO users (name, email) VALUES
  ('Ali Rezaei', 'ali@example.com'),
  ('Sara Ahmadi', 'sara@example.com');

INSERT INTO orders (user_id, amount, status) VALUES
  (1, 100.50, 'completed'),
  (1, 23.00, 'pending'),
  (2, 75.00, 'completed');