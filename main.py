import os

from utils import (
    HOLDINGS_FILES_DIR,
    MY_HOLDINGS,
    Holding,
    get_intersection_between_mfs,
    parse_holdings,
    plot_intersections,
    plot_venn_diagram_4,
)

files = [file for file in os.listdir(HOLDINGS_FILES_DIR) if file.endswith(".csv")]

# Process each mf in MY_HOLDINGS to get their constituent holdings
MF_HOLDINGS_LIST: dict[str, list[Holding]] = {}
for mf in MY_HOLDINGS:
    print(f"Processing holdings data for {mf}")
    holdings = parse_holdings(file_path=os.path.join(HOLDINGS_FILES_DIR, mf + ".csv"))
    MF_HOLDINGS_LIST[mf] = holdings


intersection_weights = get_intersection_between_mfs(MF_HOLDINGS_LIST, MY_HOLDINGS)
plot_intersections(intersection_weights)
plot_venn_diagram_4(MY_HOLDINGS[:4], MF_HOLDINGS_LIST)
