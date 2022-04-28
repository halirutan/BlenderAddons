from typing import List
import os


def merge_v1_v2_labels(surf_file: str, v1_file: str, v2_file: str):
    """
    This adds v1/v2 region labels to a `xxx_surf.asc` file like they are used in
    `import_surface_with_measures.py`. This appends another colum to the `xxx_surf.asc`
    file indicating 1 for v1 region vertex, 2 for v2 region vertex and 0 for all other
    vertices.

    It writes out a new file at the same location as the input file and prepends the
    file name with "labels".

    :param surf_file: Same surf file format as used in import_surface_with_measures.py
    :param v1_file: v1 label file
    :param v2_file: v1 label file
    """
    labels_v1 = load_labels(v1_file)
    labels_v2 = load_labels(v2_file)

    file_name = os.path.basename(surf_file)
    dir_name = os.path.dirname(surf_file)

    with open(f"{dir_name}/labels_{file_name}", "w") as out_f:
        with open(surf_file, "r") as in_f:
            for line in in_f.readlines():
                parts = line.split()
                label = int(float(parts[0]))
                if label in labels_v1:
                    parts.append("1")
                    print(" ".join(parts), file=out_f)
                elif label in labels_v2:
                    parts.append("2")
                    print(" ".join(parts), file=out_f)
                else:
                    parts.append("0")
                    print(" ".join(parts), file=out_f)


def load_labels(file: str) -> List[int]:
    """
    Loads labels from a file. The first two lines of the file are ignored.
    All other lines should have an integer at the start which is separated
    by space from all that follows on that line.

    This first integer is the id of the vertex from the xxx_surf.asc file.

    :param file: Input file
    :return: List of integers containing the vertex ids
    """
    with open(file, "r") as f:
        result = []
        # Skip the two header lines
        f.readline()
        f.readline()
        for line in f.readlines():
            parts = line.split()
            result.append(int(parts[0]))
        return result