from collections import OrderedDict

from parsers.heading_detector import HeadingDetector


class SectionSplitter:

    def __init__(self):

        self.detector = HeadingDetector()

    def split(self, text):

        sections = OrderedDict()

        current_section = "Header"

        sections[current_section] = []

        lines = [

            line.strip()

            for line in text.splitlines()

            if line.strip()

        ]

        for line in lines:

            heading = self.detector.detect(line)

            if heading:

                current_section = heading

                if current_section not in sections:

                    sections[current_section] = []

                continue

            sections[current_section].append(line)

        return sections