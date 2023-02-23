#!/usr/bin/env python3
import sys
import json


def leveled_parse(report_item, flat_output):
    if "meta" in report_item and report_item["meta"]["messages"]:
        # is this a file with messages?
        relative_path = report_item["easy_path"].lstrip("root/")
        filename = report_item["meta"]["filename"]
        complexity = report_item["value"]
        meta_messages = [
            (complexity, filename, relative_path, msg)
            for msg in report_item["meta"]["messages"]
        ]
        flat_output.extend(meta_messages)

    for child in report_item.get("children", []):
        leveled_parse(child, flat_output)


def main(datafile):
    print("scanning", datafile)

    with open(datafile, "rt") as json_report:
        report = json.load(json_report)

    flat_output = list()
    leveled_parse(report, flat_output)

    flat_output.sort(reverse=True)

    # markdown output
    print("| file | full message | relative path |")
    print("| ---- | ------------ | ------------- |")

    for _, filename, path, message in flat_output:
        print(f"|{filename}|{message}|{path}")


if __name__ == "__main__":
    main(sys.argv[1])  # very assuming, i know
