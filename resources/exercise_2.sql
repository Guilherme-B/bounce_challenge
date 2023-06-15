WITH category_prev_week_ AS (
  /*
    select the categories whose previous week's performance was below 100 sold units

    note that the outer query below cannot be leveraged to perform this computation directly,
    as that would mean filtering the categories at the Product level, whereas the goal
    is to filter based on the category's own behavior. 
      in practice this could be achieved by filtering on the JOIN predicate, see notes
      in the assumptions section.
  */
  SELECT
    products.category
  FROM
    orders
  INNER JOIN
    products
  ON
    orders.product_id = products.product_id
  WHERE
    -- filter dates whose order time is in the past week (between the previous week's Monday and Sunday)
    orders.order_time BETWEEN DATE_TRUNC('week', current_date - interval '1 week')::DATE AND (DATE_TRUNC('week', current_date - interval '1 week') + interval '6 days')::DATE
  GROUP BY
    products.category
  HAVING
    -- filter out the results for categories that have total sales less than 100 units in the past week
    SUM(orders.quantity) < 100
)

SELECT
  -- top 3 products in each category with the highest total sales in the past week
  ROW_NUMBER() OVER (PARTITION BY products.category ORDER BY SUM(orders.quantity) DESC) AS category_rank,
  products.category,
  products.product_name,
  COUNT(DISTINCT orders.order_id) orders_qty,
  SUM(orders.quantity) orders_amt
FROM
  orders
INNER JOIN
  products
ON
  orders.product_id = products.product_id
INNER JOIN
  customers
ON
  orders.customer_id = customers.customer_id
WHERE
  -- filter orders from Customers whose registration year is in the past year
  YEAR(customers.registration_date) = YEAR(GETDATE()) -1
  AND
  -- filter dates whose order time is in the past week (between the previous week's Monday and Sunday)
  orders.order_time BETWEEN DATE_TRUNC('week', current_date - interval '1 week')::DATE AND (DATE_TRUNC('week', current_date - interval '1 week') + interval '6 days')::DATE
  AND
  -- filter out the results for categories that have total sales less than 100 units in the past week
  products.category IN (SELECT category FROM category_prev_week_)
GROUP BY
  products.category,
  products.product_name
QUALIFY
  category_rank < 4