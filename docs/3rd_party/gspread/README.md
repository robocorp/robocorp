# Gspread

Simple interface for interacting with Google Sheets. It allows you to read, write, manipulate Google sheets, and perform various operations on spreadsheet data.

## Usage

```python
import gspread

gc = gspread.service_account()

# create a new spreadsheet with different worksheets
sh = gc.open("Students")
group_a = sh.add_worksheet(title="Group A", rows=100, cols=20)
group_b = sh.add_worksheet(title="Group B", rows=100, cols=20)

# add students to each worksheet
group_a.update_cell(1, 1, 'Stephen')
group_a.update_cell(2, 1, 'Alice')
group_b.update_cell(1, 1, 'John')

# share the spreadsheet with someone
sh.share('my-personal-email@gmail.com', perm_type='user', role='writer')
```

> AI/LLM's are quite good with `gspread`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Calculate total sales from worksheet](snippets/calculate_total_sales.py)

## Links and references

- [PyPI](https://pypi.org/project/gspread/)
- [Documentation](https://docs.gspread.org/en/latest/)
- [Api referance](https://docs.gspread.org/en/latest/api/index.html)
