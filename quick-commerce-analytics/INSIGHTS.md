# Quick-Commerce Product & Customer Analytics — Insights

## 1. Executive Summary

The analysis of the public Instacart Market Basket Analysis dataset shows strong evidence of repeat purchasing and substantial reorder activity across the customer base.

The dataset contains approximately **206K customers, 3M orders and 34M line items**. Approximately **59.01% of line items are reordered**, indicating that a significant share of purchasing consists of products customers have previously purchased.

Customers average **16.23 recorded orders**, while the average basket contains approximately **10.11 line items**. This suggests that repeat purchasing and basket composition are important dimensions for understanding customer value in a quick-commerce environment.

Customer retention is strong during the early order sequence but declines progressively with additional orders. Retention is approximately **84.9% by the 5th order**, **52.1% by the 10th order**, and **35.5% by the 15th order**, reaching approximately **26% by the 20th order**.

Product-level analysis shows that everyday grocery categories such as **dairy eggs, beverages, produce and bakery** have relatively high reorder rates. At the product level, **Banana** is the most frequently reordered product, with approximately **415K reordered items**.

The synthetic operational layer indicates an average simulated delivery time of **31.26 minutes**, a median of **31 minutes**, a P90 of **41.2 minutes**, and a P95 of **44.2 minutes**. Approximately **4.07%** of simulated orders are classified as late. These operational figures are illustrative only and should not be interpreted as actual Instacart delivery performance.

---

# 2. Customer & Retention Insights

## 2.1 Customer Base

The dataset contains approximately **206K customers** and **3M orders**.

The customer segmentation shows three groups:

| Segment | Customers |
| ---------------- | ------- |
| Occasional       | 107,431 |
| Repeat           | 78,469  |
| High-frequency   | 20,309  |

The **occasional segment is the largest**, representing roughly half of the customer base. The repeat segment is the second-largest group, while the high-frequency segment is substantially smaller.

### Interpretation

The customer base therefore contains a large group of customers with comparatively lower purchasing frequency alongside a meaningful repeat/high-frequency customer population.

### Business implication

For a quick-commerce platform, this creates two distinct analytical opportunities:

-  Encourage occasional customers to increase purchase frequency.
-  Increase basket size and retention among already-repeat customers.

The dataset can therefore support segmentation-based product strategies rather than treating all customers identically.

---

## 2.2 Strong Reorder Behaviour

Approximately **59.01% of all line items are reordered**, compared with approximately **41% new items**.

| Item Type | Approx. Share |
| ---------------------- | ------ |
| Reordered              | 59.01% |
| New                    | 40.99% |

This indicates that repeat purchasing is a major component of the observed shopping behaviour.

### Interpretation

A substantial proportion of baskets consists of products customers have purchased previously. This is consistent with the recurring nature of grocery purchasing.

### Business implication

Product experiences that reduce friction around repeat purchases could be explored, including:

-  Reorder shortcuts
-  Previous-order based recommendations
-  Frequently bought lists
-  Personalized replenishment suggestions
-  Recurring essentials bundles

These should be treated as product hypotheses rather than proven causal interventions.

---

# 3. Customer Retention & Cohort Insights

## 3.1 Order-Sequence Retention

The retention curve shows a gradual decline in the proportion of customers reaching later orders.

Observed retention values:

| Order Number | Retention |
| --------------------- | ------ |
| 3                     | 100.0% |
| 5                     | 84.9%  |
| 10                    | 52.1%  |
| 15                    | 35.5%  |
| 20                    | ~26%  |

The curve remains close to 100% through the earliest orders before beginning a more pronounced decline around the later early-order sequence.

By Order 10, approximately **52.1%** of the initial customer cohort reaches that order.

By Order 15, this decreases to approximately **35.5%**, and by Order 20 it is approximately **26%**.

### Interpretation

The analysis suggests that the largest customer attrition occurs as customers progress beyond the initial sequence of purchases, rather than immediately after the first few orders.

### Business implication

A quick-commerce product could investigate interventions around the early-to-mid customer lifecycle, such as:

-  Second/third-order incentives
-  Personalized reorder recommendations
-  Replenishment reminders
-  Loyalty milestones
-  Personalized bundles based on previous purchases

These are proposed opportunities, not conclusions about causal drivers of retention.

---

## 3.2 Customers Reaching Each Order

The number of customers reaching each successive order decreases steadily.

The chart starts at approximately **206K customers** and falls to approximately **53K customers by Order 20**.

This provides a complementary view to the percentage retention curve: the absolute customer population available for subsequent purchases becomes progressively smaller.

### Key observation

The platform therefore has a much smaller pool of highly engaged customers at higher order numbers than at the beginning of the observed customer journey.

This makes high-frequency customers particularly relevant for understanding long-term purchasing behaviour, while the large occasional segment provides a substantial population for potential frequency-growth analysis.

---

# 4. Product & Category Insights

## 4.1 Department-Level Reorder Behaviour

The highest reorder rates are observed in everyday-use categories.

The leading categories include:

1. **Dairy eggs**
2. **Beverages**
3. **Produce**
4. **Bakery**
5. **Deli**
6. **Pets**
7. **Babies**
8. **Bulk**
9. **Snacks**
10. **Alcohol**

The reorder rate for the leading categories is above 60%, while several categories toward the bottom of the distribution are below 40%.

### Interpretation

Categories associated with routine consumption and replenishment tend to exhibit stronger repeat purchasing behaviour in this dataset.

### Business implication

Category-level reorder rates can be used to inform:

-  Personalized reorder surfaces
-  Category-specific recommendation strategies
-  Subscription/replenishment concepts
-  “Buy again” experiences
-  Personalized bundles

The analysis should not be interpreted as showing that category reorder rate alone causes higher customer value.

---

# 5. Product-Level Insights

## 5.1 Highest Reordered Products by Volume

**Banana** is the most frequently reordered product in the dataset, with approximately **415,166 reordered items**.

Other products among the highest reordered by volume include:

-  Bag of Organic Bananas
-  Organic Strawberries
-  Organic Baby Spinach
-  Organic Hass Avocado
-  Organic Avocado
-  Organic Whole Milk
-  Large Lemon
-  Organic Raspberries
-  Strawberries

### Interpretation

The highest-volume reordered products are predominantly everyday grocery and fresh-produce products.

This reinforces the importance of recurring essentials in repeat purchasing behaviour.

### Business implication

High-volume reordered products could be useful candidates for:

-  Reorder shortcuts
-  Personalized home-page recommendations
-  Frequently bought sections
-  Basket-building recommendations
-  Essential-item bundles

---

## 5.2 High Reorder-Rate Products

The products with the highest reorder propensity are different from the products with the largest absolute reorder volume.

For example, **Raw Veggie Wrappers** has a product reorder rate of approximately **94%**.

Other products appearing among the highest-reorder-rate products include:

-  Serenity Ultimate Extreme Overnight Pads
-  Orange Energy Shots
-  Chocolate Love Bar
-  Soy Powder Infant Formula
-  Simply Sleep Nighttime Sleep Aid
-  Energy Shot, Grape Flavor
-  Russian River Valley Reserve Pinot Noir
-  Bars Peanut Butter
-  Soy Crisps Lightly Salted

### Important distinction

**Reorder volume and reorder rate measure different things.**

A product can have:

-  Very high reorder volume because many customers purchase it.
-  Very high reorder rate because the customers who purchase it tend to purchase it repeatedly.

Therefore, product strategy should consider both metrics rather than ranking products using only one.

---

# 6. Basket Behaviour

The average basket contains approximately **10.11 line items**.

Across the dataset:

- **20M** line items are reordered.
- **14M** line items are new.
-  Reordered items account for **59.01%** of all line items.

### Interpretation

Customers are not only returning to the platform; a substantial portion of the items within their baskets are also familiar/repeated products.

### Business implication

This supports exploring product experiences that combine:

**Discovery + Replenishment**

rather than focusing exclusively on new-product discovery.

For example, a customer could be shown their frequently reordered essentials alongside recommendations for complementary new products.

---

# 7. Order-Tenure Behaviour

The reorder-rate-by-order-number curve increases sharply during the earliest orders and then gradually approaches a higher plateau.

The later-order portion of the curve is approximately in the **80–85% range**.

### Interpretation

Customers who progress further through the observed order sequence appear increasingly likely to purchase items that they have purchased before.

This suggests that purchasing becomes more habitual as customers accumulate more orders.

### Business implication

The customer journey can potentially transition from:

**Discovery → Familiarity → Replenishment**

A product experience could therefore become progressively more personalized as customer purchase history accumulates.

---

# 8. Delivery & Operational Insights

## Important Data Qualification

The delivery analysis is based on a **synthetic delivery dataset generated as an illustrative operational layer**.

The original Instacart dataset does not provide actual delivery timestamps. 

All conclusions below should be described as observations from the simulated operational layer.

---

## 8.1 Simulated Delivery Performance

The synthetic delivery layer produces:

| Metric | Value |
| --------------------- | --------- |
| Average delivery time | 31.26 min |
| Median delivery time  | 31.00 min |
| P90 delivery time     | 41.20 min |
| P95 delivery time     | 44.20 min |
| Late delivery rate    | 4.07%     |

The median and average are relatively close, while the P90 and P95 are meaningfully higher.

### Interpretation

The simulated distribution is concentrated around approximately **20–40 minutes**, with a smaller tail extending toward longer delivery times.

The difference between median and high-percentile delivery times illustrates why average delivery time alone is insufficient for operational monitoring.

### Business implication

For a real quick-commerce operation, useful operational KPIs would include:

-  Median delivery time
-  P90/P95 delivery time
-  Late-delivery rate
-  Delivery-time distribution
-  Performance by time of day
-  Performance by customer segment
-  Performance by geography/store/dark store

---

## 8.2 Delivery Time Distribution

The synthetic delivery distribution is concentrated primarily between approximately **20 and 40 minutes**, with the largest concentration around the late-20s/early-30s range.

There are relatively few simulated orders at very high delivery times.

This demonstrates why percentile metrics such as P90 and P95 are useful alongside the average: they capture the longer tail of delivery performance.

---

# 9. Business Implications

Based on the dashboard, the following product opportunities emerge as **hypotheses for further testing**:

### 1. Build stronger reorder experiences

With **59.01% of line items being reordered**, repeat purchasing represents a substantial component of observed behaviour.

Potential features:

-  Buy Again
-  Frequently Purchased
-  Reorder entire previous basket
-  One-tap replenishment

### 2. Target occasional customers

The occasional segment contains approximately **107K customers**, making it the largest customer segment.

Potential experiments could test:

-  Second-order incentives
-  Personalized recommendations
-  First-to-second-order nudges
-  Curated essentials baskets

### 3. Personalize based on purchase history

As customers progress through the order sequence, reorder behaviour becomes increasingly prominent.

This supports progressively stronger personalization based on:

-  Previous purchases
-  Purchase frequency
-  Product reorder probability
-  Basket composition

### 4. Optimize essential-product discovery

Products such as bananas, berries, spinach, avocados and milk appear prominently among high-volume reordered products.

These products could be incorporated into:

-  Essential-item recommendations
-  Personalized grocery lists
-  Replenishment reminders
-  Basket-building recommendations

### 5. Monitor operational tail performance

The synthetic delivery analysis demonstrates the value of tracking P90/P95 delivery time in addition to average delivery time.

For a real platform, this would allow operations teams to identify situations where average performance appears acceptable while a smaller group of customers experiences substantially longer deliveries.

---

# 10. Limitations

### 1. Public Instacart dataset

This project uses the public Instacart Market Basket Analysis dataset and **does not use proprietary quick-commerce company data**.

Therefore, findings describe the available Instacart dataset rather than the performance of a specific Indian quick-commerce platform.

### 2. No calendar dates

The dataset does not provide usable calendar dates for the orders.

Therefore, the retention analysis is based on **order sequence/tenure**:

> Order 1 → Order 2 → Order 3 → ... → Order N

It is **not calendar-based cohort retention** such as January 2025 → February 2025.

### 3. Dataset selection and repeat customers

The available customer/order data contains users with multiple recorded orders. Consequently, the dashboard reports:

> **Repeat Customer Rate = 100%**

This should **not** be interpreted as saying that 100% of all Instacart customers are repeat customers.

Instead, it reflects the construction/coverage of the dataset.

For this reason, order-sequence retention and reorder behaviour are more informative metrics for this project.

### 4. Synthetic delivery data

The delivery table is synthetically generated.

All delivery-related insights are therefore **illustrative rather than observed platform performance**.

### 5. No causal inference

The dashboard identifies patterns and relationships in the dataset.

It does not establish that a particular product feature, promotion or customer characteristic **causes** higher retention, reorder rate or basket size.

### 6. Product-level high reorder rate

Products with extremely high reorder rates may have relatively different purchase volumes.

Therefore:

> **High reorder rate ≠ high business impact**

Both reorder rate and reorder volume should be considered when prioritizing products.
