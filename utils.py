import csv
from dataclasses import dataclass

import matplotlib.pyplot as plt
import venn
from matplotlib_venn import venn2


@dataclass
class Holding:
    stock: str
    sector: str
    weight: float


HOLDING_THRESHOLD = 0.01
HOLDINGS_FILES_DIR = "./data"
MY_HOLDINGS: list[str] = [
    "nifty50",
    "next50",
    "ppflex",
    "tdigital",
    "ssmall",
    "n500m50",
    "micro250",
]
SEPARATOR = "-" * 79


# Parses the holdings file and returns a list of Holding objects
# Expects the holdings file to be from rupeevest.com
# The columns are expected to be:
# Company,Sector,_, Weight
# It also reads upto a line, where the first column is "Total"
# and stops reading further
def parse_holdings(file_path: str) -> list[Holding]:
    holdings: list[Holding] = []
    data: list[list[str]] = []

    with open(file_path, mode="r", newline="") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)  # header
        for _, row in enumerate(csv_reader):
            if row[0] == "Total":
                break
            else:
                data.append(row)
                holdings.append(Holding(row[0], row[1], float(row[3])))
    return holdings


def print_holdings(holdings: list[Holding]):
    holdings.sort(key=lambda x: x.weight, reverse=True)
    idx = 1

    for holding in holdings:
        if holding.weight >= HOLDING_THRESHOLD:
            print(f"{idx}: {holding.stock}: {holding.sector} ({holding.weight}%)")
            idx += 1


def compute_intersection(
    mf_a_holdings: list[Holding], mf_b_holdings: list[Holding]
) -> list[Holding]:
    mf_a_holdings_dict = {
        mf_a_holding.stock: mf_a_holding for mf_a_holding in mf_a_holdings
    }
    mf_b_holdings_dict = {
        mf_b_holding.stock: mf_b_holding for mf_b_holding in mf_b_holdings
    }

    intersection: list[Holding] = []
    for stock in mf_a_holdings_dict:
        if stock in mf_b_holdings_dict:
            holding_in_a = mf_a_holdings_dict[stock]
            holding_in_b = mf_b_holdings_dict[stock]
            intersection.append(
                Holding(
                    stock,
                    holding_in_a.sector,
                    min(holding_in_a.weight, holding_in_b.weight),
                )
            )
    return intersection


def plot_intersections(intersections: dict[str, float]):
    funds = list(intersections.keys())
    weights = list(intersections.values())

    plt.figure(figsize=(10, 6))
    plt.barh(funds, weights, color="skyblue")
    plt.xlabel("Intersection Weight (%)")
    plt.title("Intersection Weights Between Mutual Funds")
    plt.gca().invert_yaxis()  # Reverse the order for better readability
    plt.show()
    plt.savefig("./assets/intersections.png")

def plot_venn_diagram(
    mf_a: str,
    mf_b: str,
    intersection: list[Holding],
    MF_HOLDINGS_LIST: dict[str, list[Holding]],
):
    set_a = get_holding_set(MF_HOLDINGS_LIST, mf_a)
    set_b = get_holding_set(MF_HOLDINGS_LIST, mf_b)

    plt.figure(figsize=(8, 8))
    venn2([set_a, set_b], (mf_a, mf_b))
    plt.title(f"Venn Diagram of {mf_a} and {mf_b}")
    plt.savefig(f"./assets/venn_{mf_a}_{mf_b}.png")


def plot_venn_diagram_4(
    mfs_in_holdings: list[str], MF_HOLDINGS_LIST: dict[str, list[Holding]]
):
    mf_holdings_stock_names = {
        mf: get_holding_set(MF_HOLDINGS_LIST, mf) for mf in mfs_in_holdings
    }
    labels = venn.get_labels(
        [
            mf_holdings_stock_names[mfs_in_holdings[0]],
            mf_holdings_stock_names[mfs_in_holdings[1]],
            mf_holdings_stock_names[mfs_in_holdings[2]],
            mf_holdings_stock_names[mfs_in_holdings[3]],
        ],
        fill=["number", "percent"],
    )

    fig, _ = venn.venn4(labels, names=mfs_in_holdings[:4])
    fig.savefig("./assets/venn4.png")  # Save as a PNG file


def get_holding_set(MF_HOLDINGS_LIST: dict[str, list[Holding]], mf: str) -> set[str]:
    return set(holding.stock for holding in MF_HOLDINGS_LIST[mf])


def get_intersection_between_mfs(
    MF_HOLDINGS_LIST: dict[str, list[Holding]], MY_HOLDINGS: list[str]
) -> dict[str, float]:
    intersection_weights: dict[str, float] = {}
    for idx, mf in enumerate(MY_HOLDINGS):
        for _, other_mf in enumerate(MY_HOLDINGS[idx + 1 :]):
            print(f"Intersection of {mf} and {other_mf}:")
            intersection = compute_intersection(
                MF_HOLDINGS_LIST[mf], MF_HOLDINGS_LIST[other_mf]
            )
            if len(intersection) > 0:
                print_holdings(intersection)
                intersection_weight = sum(holding.weight for holding in intersection)
                plot_venn_diagram(mf, other_mf, intersection, MF_HOLDINGS_LIST)
                if intersection_weight > 0:
                    intersection_weights[f"{mf} & {other_mf}"] = intersection_weight
                print(f"Total intersection weight: {intersection_weight}%")
            else:
                print("No intersection")
            print(SEPARATOR)

    return intersection_weights
