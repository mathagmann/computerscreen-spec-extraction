# Rule-based parser

The shop parser uses a rule-based approach to extract information from the HTML of the shop offers. The rules are defined in `rules.py` and are applied to the HTML of the shop offers. 
The extracted information is then stored in a JSON file.

## Requirements

For each shop a YAML configuration file is needed. 
It contains the rules to extract semi-structured specifications from this shop website. 
The configuration files are located in the `config` folder.

## Usage

The shop parser can be used as follows:

```python
specification_dict = shop_parser.parse_shop(shop_html, shop_name)
```

It returns a dictionary containing the extracted sem-structured specifications as key-value pairs.
