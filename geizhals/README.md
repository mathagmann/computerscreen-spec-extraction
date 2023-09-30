# Geizhals

The Geizhals interface is a data retrieval interface for the [Geizhals](https://geizhals.de/) price comparison website.
It requires a browser implementation like [Playwright](https://playwright.dev/python/) to retrieve HTML.
- It extracts all products for a given category URL.
- It extracts product specifications, prices and shop offers for a given product URL.

## Usage

### Get all products for a category

```python
geizhals_category_page = "https://geizhals.at/?cat=monlcd19wide"
browser = Browser()
result = geizhals_api.get_category_page(geizhals_category_page, browser)
```

### Get product details 

Get product details like name, specifications and shop offers with price per shop.

```python
geizhals_product_page = ""
browser = Browser()
result = geizhals_api.get_product_page(product.link, browser)
```
