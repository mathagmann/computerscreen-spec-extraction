# Data generation

Downloads monitor shop offers as plain HTML and adds metadata as JSON.

## Usage

Run data generation with the following command:

```bash
python cli.py
```

It collects all monitors from Geizahls and downloads the shop offers as HTML. 
Some metadata is added to the HTML files and stored as JSON. 

### Get all monitors listed on Geizhals

This retrieves all monitors with their name and URL to the Geizhals product details with merchant offers.
Dumping the data as JSON is optional and creates the `product_listing.json` file, which contains a list of name and 
link for each monitor.

#### Code example
```python
browser = Browser()
products = create_data.retrieve_all_products(browser)

# Save monitor list (name, link) as JSON 
create_data.dump_product_listing(products)
```
}

This less than 5 minutes.


### Get monitor details

This retrieves the monitor details from the Geizhals product details page.
It stores of the shop's product pages as HTML together with metadata as JSON.

An **offer_{product_nr}_{offer_nr}.html** contains a shop's product page as plain HTML and 
the associated **offer_{product_nr}_{offer_nr}.json** contains metadata:
- `shop_name`: Name of the shop
- `price`: Cheapest price of the monitor on Geizhals
- `offer_link`: Link to the shop's product page
- `html_file`: Filename of the downloaded HTML file containing the shop's product page.
- `reference_file`: Filename of the Geizhals product details.

An **offer_reference_{product_nr}.json** contains the following information:
- `url`: URL to the Geizhals product details page
- `product_name`: Name of the monitor on Geizhals
- `product_details`: List of product details from Geizhals as key-value pairs
- `offers`: List of shop offers for this product from Geizhals, with shop name, price and link to the shop's product 
  page.

#### Code example
```python
browser = Browser()
create_data.retrieve_product_details(browser)
```

This takes around a day per 1000 monitors, and its multiple 1000s of shop offers.
