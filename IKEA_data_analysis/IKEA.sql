create database ikea_retail;
use ikea_retail;

CREATE TABLE ikea (
    invoiceno VARCHAR(20),
    date DATE,
    time TIME,
    stockcode VARCHAR(25),
    description TEXT,
    quantity INT,
    unitprice DOUBLE,
    custid INT,
    country VARCHAR(100)
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ikea_updated.csv'
INTO TABLE ikea
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(invoiceno, @date, @time, stockcode, description, quantity, unitprice, custid, country)
SET
    date = STR_TO_DATE(@date, '%d-%m-%Y'),
    time = STR_TO_DATE(@time, '%H:%i:%s');
    
    
select * from ikea limit 10;

-- /--   1. Sales Performance Insights --/
## 1. What is the total revenue generated?
select sum(unitprice * quantity) as revenue from ikea where quantity>0;

## 2. What is the average order value (AOV)?
select round(sum(unitprice*quantity)/ count(distinct invoiceno),2) as aov from ikea where quantity>0;

## 3. What are the top 10 highest revenue generating days?
select date, round(sum(unitprice*quantity),2) as revenue from ikea where quantity>0 group by date order by revenue desc limit 10;

## 4. Which month generated the highest sales?
select month(date) as month, round(sum(unitprice*quantity),2) as revenue from ikea where quantity>0 group by month order by revenue desc;

## 5. What is the revenue trend month-by-month?
select date_format(date, '%Y-%m') as month, sum(unitprice*quantity) as sales from ikea where quantity>0 group by month order by month;

## 6. What day of the week has the highest revenue?
select dayname(date) as month, round(sum(unitprice*quantity),2) as revenue from ikea where quantity>0 group by month order by revenue desc;

## 7. Which hour of the day customers purchase the most?
select hour(time) as hr, round(sum(unitprice*quantity),2) as revenue from ikea where quantity>0 group by hr order by revenue desc;

## 8. Weekend vs Weekday — when do people spend more?
select case when dayofweek(date) in (1,7) then 'weekend' else 'weekday' end as day_type,  
round(sum(unitprice*quantity),2) as revenue from ikea where quantity>0 group by day_type order by revenue desc;

## 9. Are customers buying more in mornings or evenings?
select case when hour(time) < 13 then 'Morning' else 'Evening' end as time_type,
round(sum(unitprice*quantity),2) as revenue from ikea where quantity>0 group by time_type order by revenue desc;

## 10. What is the busiest shopping time slot?
select hour(time) as timing, count(distinct invoiceno) as orders from ikea group by timing order by orders desc limit 3;


-- / -- 2. Product Insights --/
## 11. Top 10 most sold products (by quantity)
select description, sum(quantity) as orders from ikea where quantity>0 and description<>'' group by description order by orders desc limit 10;

## 12. Top 10 highest revenue products
select description, round(sum(quantity*unitprice),2) as revenue from ikea where quantity>0 and description<>'' group by description order by revenue desc limit 10;

## 13. Which products are frequently returned?
select description, count(*) as returns from ikea where quantity<0 and description in ('', 'Damaged') group by description order by returns desc limit 10;

## 14. Which products generate high revenue but low quantity?
select description, round(sum(quantity*unitprice),2) as revenue, sum(quantity) as orders from ikea 
group by description having revenue>15000 and orders < 5000;

## 15. Which products generate high quantity but low revenue?
select description, round(sum(quantity*unitprice),2) as revenue, sum(quantity) as orders from ikea group by description having revenue<15000 and orders > 5000;

## 16. Most expensive product sold
select description, unitprice from ikea where unitprice = (Select max(unitprice) from ikea);

## 17. Cheapest product sold
select description, unitprice from ikea where unitprice = (Select min(unitprice) from ikea where unitprice>0);

## 18. Product categories customers prefer (use description keywords)
select case when description like '%SET%' then 'Set' 
when description like '%BAG%' then 'Bag' else 'Others' end as category, count(*) as sales from ikea group by category;

## 19. Which products are usually bought together (same invoice)
select a.description, b.description, count(*) as freq from ikea a join ikea b on a.invoiceno=b.invoiceno and a.stockcode<b.stockcode
group by a.description, b.description order by freq desc limit 10;

## 20. Which items are impulse purchases (single quantity orders)
select description, count(*) as impulse from ikea where quantity=1 group by description order by impulse desc limit 10;


-- / -- 3. Customer Behaviour Insights  --/
## 21. Total unique customers
select count(distinct(custid)) from ikea;

## 22. Top 10 highest spending customers
select custid, round(sum(unitprice*quantity),2) as spend from ikea where custid<>0 group by custid order by spend desc limit 10;

## 23. Most frequent customers (by invoice count)
select custid, count(distinct(invoiceno)) as freq from ikea where custid<>0 group by custid order by freq desc;

## 24. Customers who buy in bulk vs small purchases
select custid, case when avg(quantity)>20 then 'Bulk' else 'Small' end purchaser from ikea group by custid;

## 25. Average spend per customer
select avg(total_spend) from (select custid, sum(quantity*unitprice) as total_spend from ikea group by custid) t;

## 26. Customer lifetime value (total spend per customer)
select custid, sum(quantity*unitprice) as CLV from ikea where custid<>0 group by custid order by CLV desc;

## 27. New vs returning customers per month
select date_format(date, '%Y-%m') month, (count(distinct custid)*100/count(custid)) as new_vs_returning from ikea group by month;

## 28. Customers active only once (one-time buyers)
select custid from ikea group by custid having count(distinct invoiceno)=1;

## 29. Customers who stopped purchasing (churn detection)
select custid, max(date) last_purchased from ikea group by custid having last_purchased<'2011-11-01';

## 30. Time gap between customer purchases (repeat cycle)
-- select custid, avg(datediff(date, lag(date) over(partition by custid order by date)))gap from ikea;
select custid, avg(gap_days) avg_cycle from (select custid, datediff(date, lag(date) over (partition by custid order by date)) as gap_days from ikea)t where gap_days is not null group by custid;




-- / --  4. Country / Geography Insights -- /
## 31. Which country generates highest revenue?
select country, sum(unitprice*quantity) as revenue from ikea group by country order by revenue desc limit 1;

## 32. Which country has highest average order value?
select country, avg(unitprice*quantity) as aov from ikea group by country order by aov desc limit 1;

## 33. Which country buys most quantity but low revenue?
select country, sum(quantity) qty, sum(unitprice*quantity) as revenue from ikea group by country order by qty desc;

## 34. Country with most unique customers
select country, count(distinct custid) as new from ikea group by country order by new desc limit 1;

## 35. Country with most returns
select country, count(*) returns from ikea where quantity<0 group by country order by returns desc limit 1;

## 36. Sales distribution across countries
select country, sum(unitprice*quantity) as revenue from ikea group by country;

## 37. Peak shopping time per country
select country, hour(time), count(*) from ikea group by country, hour(time);

## 38. Which products are popular in each country
select country, description, count(*) from ikea group by country, description;



-- / --  5. Returns & Cancellation Insights (VERY important dataset feature) -- /
## 39. Percentage of orders cancelled
select count(distinct invoiceno) * 100/(select count(distinct invoiceno) from ikea) from ikea where quantity<0;

## 40. Revenue lost due to cancellations
select sum(quantity*unitprice) loss from ikea where quantity<0;

## 41. Most returned products
select description, count(*) returns from ikea where quantity<0 and description<>'' group by description order by returns desc limit 1;

## 42. Customers with highest return behaviour
select custid, count(*) returns from ikea where quantity<0 and custid<>0 group by custid order by returns desc;

## 43. Countries with highest return rate
select country, count(*) returns from ikea where quantity<0 and custid<>0 group by country order by returns desc;

## 44. Are expensive items returned more?
select avg(unitprice) from ikea where quantity<0;

## 45. Do repeat customers return less?
select custid, count(*) from ikea where quantity<0 group by custid;

## 46. Return behaviour by day of week
select dayofweek(date), count(*) returns from ikea where quantity<0 group by dayofweek(date);
select dayname(date), count(*) returns from ikea where quantity<0 group by dayname(date);

## 47. Return behaviour by hour
select hour(time), count(*) returns from ikea where quantity<0 group by hour(time);



-- / --  6. Order Pattern Insights -- /
## 48. Average items per order
select avg(items) from (select invoiceno,sum(quantity) items from ikea group by invoiceno)t;

## 49. Largest order ever placed
select invoiceno, sum(quantity*unitprice) from ikea group by invoiceno order by 2 desc limit 1;

## 50. Smallest order value
select invoiceno, sum(quantity*unitprice) from ikea group by invoiceno order by 2 asc limit 1;

## 51. Distribution of order sizes
select invoiceno, count(*) from ikea group by invoiceno;

## 52. Bulk buyers vs normal buyers
select invoiceno, sum(quantity) qty from ikea group by invoiceno having qty>100;

## 53. How many products per invoice on average?
select avg(prods) from (select invoiceno, count(*) prods from ikea group by invoiceno)t;

## 54. Orders containing more than 10 items
select invoiceno from ikea group by invoiceno having sum(quantity)>10;

## 55. Do large orders happen at specific times?
select hour(time), avg(quantity) from ikea group by hour(time);



-- / -- 7. Advanced Analytical Insights (Stand-out level) -- /
## 56. RFM Analysis (Recency, Frequency, Monetary)
select custid, datediff(max(date), '2011-12-31') recency, count(distinct invoiceno) frequency, sum(quantity*unitprice) monetary from ikea group by custid having custid<>0;

## 57. Customer segmentation (high / medium / low value)
select custid, case when sum(quantity*unitprice) > 100000 then 'High'
when sum(quantity*unitprice) > 50000 then 'Medium' else 'Low' end segment from ikea group by custid;

## 58. Peak seasonal shopping period
select monthname(date), sum(quantity*unitprice) from ikea group by monthname(date);

## 59. Shopping behaviour before holidays (monthly spikes)
select monthname(date), count(*) from ikea group by monthname(date);

## 60. Detect business vs personal buyers
select custid, sum(quantity) from ikea group by custid having sum(quantity)>10000;

## 61. Cohort analysis — retention month-wise
select custid, min(date_format(date,'%Y-%m')) cohort from ikea group by custid;

## 62. Time between first and second purchase
select custid, avg(gap_days) avg_cycle from (select custid, datediff(date, lag(date) over (partition by custid order by date)) as gap_days from ikea)t where gap_days is not null group by custid;
select custid, min(date), max(date) from ikea group by custid;	


## 63. Are high spenders loyal?
select custid from ikea where custid<>0 group by custid having sum(quantity*unitprice)>50000 and count(distinct invoiceno)>100;

## 64. Probability of repeat purchase
select count(*) * 100/(select count(distinct custid) from ikea) from (select custid from ikea group by custid having count(distinct invoiceno)>1)t;

## 65. Identify VIP customers (top 5% revenue contributors)
select custid, total from (select custid, sum(quantity*unitprice) as total, ntile(20) over (order by sum(quantity*unitprice) desc) as percentile_rank from ikea 
group by custid) t where percentile_rank = 1;