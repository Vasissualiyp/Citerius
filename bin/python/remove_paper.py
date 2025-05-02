import sys
from config import CiteriusConfig

if __name__ == "__main__":
    #ref_dir = sys.argv[1]
    ref_dir = "/home/vasilii/research/references"
    citerius = CiteriusConfig(ref_dir)
    label = citerius.fuzzy_find_label()
    citerius.remove_paper(label)
