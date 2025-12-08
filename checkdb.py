from jsondb.database import read_docs

def read():
    try:
        read_docs()
    except Exception as e:
        print(f"Error while reading DB: {e}")

if __name__ == "__main__":
    read()
