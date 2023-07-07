import os
import time
from janome.tokenizer import Tokenizer
import pykakasi
from tqdm import tqdm
from multiprocessing import Pool

tokenizer = Tokenizer()
kks = pykakasi.kakasi()
# chinese letter unicode range
ranges = [
    {"from": ord("\u3300"), "to": ord("\u33ff")},  # compatibility ideographs
    {"from": ord("\ufe30"), "to": ord("\ufe4f")},  # compatibility ideographs
    {"from": ord("\uf900"), "to": ord("\ufaff")},  # compatibility ideographs
    {
        "from": ord("\U0002F800"),
        "to": ord("\U0002fa1f"),
    },  # compatibility ideographs
    {"from": ord("\u2e80"), "to": ord("\u2eff")},  # cjk radicals supplement
    {"from": ord("\u4e00"), "to": ord("\u9fff")},
    {"from": ord("\u3400"), "to": ord("\u4dbf")},
    {"from": ord("\U00020000"), "to": ord("\U0002a6df")},
    {"from": ord("\U0002a700"), "to": ord("\U0002b73f")},
    {"from": ord("\U0002b740"), "to": ord("\U0002b81f")},
    {
        "from": ord("\U0002b820"),
        "to": ord("\U0002ceaf"),
    },  # included as of Unicode 8.0
]
        

def is_chinese(string):
    for char in string:
        is_c = any(
            [range["from"] <= ord(char) <= range["to"] for range in ranges]
        )
        if is_c:
            return True
    return False
    
def ja_tok(txt):
    new_txt = ""
    for token in tokenizer.tokenize(txt):
        src_word = token.__dict__["node"].node_label()
        token_info = token.__dict__["extra"]
        if token_info is None:
            if is_chinese(src_word):
                result = kks.convert(src_word)
                for re in result:
                    new_txt += re["hira"]
                continue
            new_txt += str(token).split("\t")[0]
        else:
            if is_chinese(src_word):
                src_word = token_info[-2]
                result = kks.convert(src_word)
                for re in result:
                    new_txt += re["hira"]
                continue
            new_txt += src_word
    return new_txt

def process_setup(
    kanji_list: list,
):
    # multiprocessing setup
    num_process = os.cpu_count()
    chunksize = max(1,len(kanji_list) // num_process)
    print("-"*20)
    print(f"Total processes:{os.cpu_count()} \nUsing processes:\t{num_process} \nChunk size:\t{chunksize}")
    print("-"*20)    
    return num_process, chunksize

def kanji_to_kana(
    kanji_list: list,
    num_process: int,
    chunksize: int,
):
    print("\nkanji 변환을 시작합니다.\n")
    start = time.time()
    pool = Pool(processes=num_process)
    converted_list = []
    with tqdm(kanji_list) as pbar:
        for converted in tqdm(pool.imap(func=ja_tok, iterable=kanji_list, chunksize=chunksize)):
            converted_list.append(converted)
            pbar.update()
    pool.close()
    pool.join()
    print("\n변환 소요시간 :", time.time() - start, "seconds")
    return converted_list    
