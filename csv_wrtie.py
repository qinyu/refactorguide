
import csv
import os

from itertools import groupby
from operator import attrgetter


c_format = '''{}
Class '{name}' in '{package}' belongs to '{module}'
  depends on:
    {}
'''

d_format = "- {category} '{name}' in '{package}' belongs to '{module}'"


m_format = '''{}
├──{}
'''




def repr_dep_group(dep_li):
    if not dep_li:
        return ""

    s=""
    for key, li in groupby(dep_li, key=attrgetter('module')):
        li1 = ["{}.{}\n".format(i.package, i.name) for i in li]
        s += m_format.format(key, "├──".join(li1))
    return s


def write_csv(module_dict):
    for m, pkg_dict in module_dict.items():
        for pkg in pkg_dict.values():

            module_name = m.lstrip("..:").replace(":", ".")
            file_name = 'csv/{}/{}.csv'.format(module_name, pkg.name)
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

            with open(file_name, 'w', newline='') as f:

                w = csv.writer(f)
                w.writerow(["Name", "Production",
                        "Android", "Jar", "Aar", "LocalJar"])
                for c in pkg.classes:
                    w.writerow(["{}.{}\n".format(c.package, c.name),
                    repr_dep_group(
                        [d for d in c.dependencies if d.category == "Production"]),
                    repr_dep_group(
                        [d for d in c.dependencies if d.category == "Android"]),
                    repr_dep_group(
                        [d for d in c.dependencies if d.category == "3rdJar"]),
                    repr_dep_group(
                        [d for d in c.dependencies if d.category == "3rdAar"]),
                    repr_dep_group(
                        [d for d in c.dependencies if d.category == "LocalJar"])]
                    )