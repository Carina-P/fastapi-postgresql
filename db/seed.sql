INSERT INTO customers (name, email, country)
    VALUES
        ('Anna Andersson', 'anna@example.com', 'Sweden'),
        ('Erik Svensson', 'erik@example.com', 'Sweden'),
        ('Maria Johansson', 'maria@example.com', 'Sweden'),
        ('John Smith', 'john@example.com', 'UK'),
        ('Emma Wilson', 'emma@example.com', 'UK'),
        ('Hans Müller', 'hans@example.com', 'Germany'),
        ('Sophie Weber', 'sophie@example.com', 'Germany'),
        ('Pierre Dubois', 'pierre@example.com', 'France'),
        ('Laura Rossi', 'laura@example.com', 'Italy'),
        ('Peter Hansen', 'peter@example.com', 'Denmark');

INSERT INTO products (name, price, active, category)
    VALUES
        ('grey-t', 30.49, TRUE, 't-shirt'),
        ('blue-trousers', 99.99, TRUE, 'trousers'),
        ('red-shirt', 68.56, TRUE, 'shirt-m'),
        ('black-sweater', 101.48, TRUE, 'sweater-m'),
        ('white-socks', 5.95, TRUE, 'socks-m'),
        ('running-shoes', 129.90, TRUE, 'shoes'),
        ('winter-jacket', 249.00, TRUE, 'jacket'),
        ('green-t', 35.50, TRUE, 't-shirt'),
        ('black-trousers', 89.90, FALSE, 'trousers'),
        ('sports-socks', 12.95, TRUE, 'socks-m');

INSERT INTO orders (customer_id, order_date, status)
    VALUES
        (1, '2026-09-01', 'completed'),
        (2, '2026-09-03', 'shipped'),
        (1, '2026-09-05', 'pending'),
        (3, '2026-09-07', 'completed'),
        (4, '2026-09-10', 'shipped'),
        (5, '2026-09-12', 'pending'),
        (2, '2026-09-15', 'completed'),
        (3, '2026-09-18', 'cancelled'),
        (1, '2026-09-20', 'shipped'),
        (4, '2026-09-22', 'pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES
        (1, 1, 2, 199.00),
        (1, 2, 1, 349.00),
        (2, 3, 1, 499.00),
        (3, 1, 3, 199.00),
        (3, 4, 2, 129.00),
        (4, 2, 2, 349.00),
        (5, 5, 1, 799.00),
        (5, 1, 1, 199.00),
        (6, 3, 2, 499.00),
        (7, 4, 4, 129.00),
        (7, 5, 1, 799.00),
        (8, 2, 1, 349.00),
        (9, 1, 2, 199.00),
        (9, 3, 1, 499.00);