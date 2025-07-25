def classify_heading_level(font_sizes):
    """
    Map the top-3 distinct font sizes to H1, H2, H3.
    Anything smaller is treated as body text.
    """
    # sort unique sizes descending
    sorted_sizes = sorted(set(font_sizes), reverse=True)
    levels = {}
    # only top 3 become headings
    mapping = {0: "H1", 1: "H2", 2: "H3"}
    for rank, size in enumerate(sorted_sizes[:3]):
        levels[size] = mapping[rank]
    return levels
