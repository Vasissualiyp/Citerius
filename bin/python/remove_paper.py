import sys
from config import CiteriusConfig

if __name__ == "__main__":
    #ref_dir = sys.argv[1]
    config_file = None
    citerius = CiteriusConfig(config_file)
    label = citerius.fuzzy_find_label()
    answer = input(f"You are about to remove paper with label {label}. Are you sure? (y/N): ")
    if answer.lower() == 'y':
        citerius.remove_paper(label)
        citerius.repo.close()
    else:
        print(f"You answered '{answer}'. The paper will not be removed.")
