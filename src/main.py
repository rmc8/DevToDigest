import os

import fire

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def proc(tag_name:str, webhook_url:str):
    pass

def main():
    fire.Fire(proc)


if __name__ == "__main__":
    main()
