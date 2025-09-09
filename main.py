from CTVSort import CTVSort
from CMovieSort import CMovieSort


def process(config_file: str, strType: str):

    if (strType == "TV"):
        tvSort = CTVSort()
        tvSort.load_config(config_file)
        tvSort.process()
    else:
        if (strType == "Movies"):
            MovieSort = CMovieSort()
            MovieSort.load_config(config_file)
            MovieSort.process()



#process("TV_Debug.cfg", "TV")
process("TV.cfg", "TV")
process("example.cfg", "Movies")


