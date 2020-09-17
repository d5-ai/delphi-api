from delphi_api import bqSync

if __name__ == "__main__":
    try:
        bqSync.main(False, False)
    except Exception as e:
        print(e)
