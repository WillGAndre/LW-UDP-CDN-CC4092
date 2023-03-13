from app import app
from applib import applib

result = applib.multiply(2,3)
print("result")
print(result)
# Run caching (?)
if __name__ == "__main__":
    app.run()