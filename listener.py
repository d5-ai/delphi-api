from delphi_api import listen


if __name__ == "__main__":
    try:
        listen.main(True, False, False, False)
    except Exception as e:
        print(e)
