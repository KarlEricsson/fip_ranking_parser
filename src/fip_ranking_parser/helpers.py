from pathlib import Path
import pandas as pd

ranking_original = Path("ranking.csv")
ranking_clean = Path("ranking_clean.csv")
def manual_replace(error_names: list[str]) -> list[str]:
    """Manual hacks that clean() couldn't fix"""
    find_list: list[str] = [
        "Ã(cid:129)lvaro Melendez Amaya",
        "Dovydas Å abÅ«nas",
        "Enrique Casado De Ã(cid:129)vila",
        "Linas PlanÄ(cid:141)iÅ«nas",
        "Tadas MiseviÄ(cid:141)ius",
        "Aimar Diaz RodrÃ guez",
        "Javier RamÃ rez DavÃ³",
        "JesÃºs IrÃ bar Olmo Villarreal",
    ]
    replace_list: list[str] = [
        "Álvaro Melendez Amaya",
        "Dovydas Šabūnas",
        "Enrique Casado De Ávila",
        "Linas Plančiūnas",
        "Tadas Misevičius",
        "Aimar Diaz Rodríguez",
        "Javier Ramírez Davó",
        "Jesús Iríbar Olmo Villarreal",
    ]
    df = pd.read_csv("ranking_clean.csv")
    df["name"] = df["name"].replace(find_list, replace_list)
    df.to_csv("ranking_clean.csv", encoding="utf-8", index=False)
    not_replaced: list[str] = []
    for name in error_names:
        if name not in find_list:
            not_replaced.append(name)
    return not_replaced

def csv_finder() -> Path:
    if Path(ranking_clean).exists():
        return ranking_clean
    elif Path(ranking_original).exists():
        return ranking_original
    else:
        raise FileNotFoundError("File not found. Try 'fiprank load <rankingfile.pdf>'")
   

    
    