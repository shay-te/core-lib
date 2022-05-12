# String Helpers 

In string helpers we have functions that will convert different naming conventions.

### Functions and Usage

- `snake_to_camel` will convert snake case to camel case.
- `camel_to_snake` will convert camel case to snake case.
    #### Usage
```python
from core_lib.helpers.string import snake_to_camel, camel_to_snake

camel_case = snake_to_camel("this_is_snake_to_camel")
print(camel_case) # "ThisIsSnakeToCamel"
snake_case = camel_to_snake("ThisIsCamelToSnake")
print(snake_case) # "this_is_camel_to_snake"
```