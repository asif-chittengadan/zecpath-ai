import json
import re

import spacy
from rapidfuzz import process, fuzz


class SkillExtractor:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        with open(
            "data/skills.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.skills = {}

        for category, skill_list in data.items():

            self.skills[category] = sorted(
                skill_list,
                key=len,
                reverse=True
            )

        self.synonyms = {

            "js": "JavaScript",
            "javascript": "JavaScript",
            "ts": "TypeScript",
            "py": "Python",
            "cpp": "C++",
            "c plus plus": "C++",
            "c sharp": "C#",
            "node": "Node.js",
            "nodejs": "Node.js",
            "express": "Express.js",
            "mongo": "MongoDB",
            "mongodb": "MongoDB",
            "postgres": "PostgreSQL",
            "postgresql": "PostgreSQL",
            "powerbi": "Power BI",
            "ml": "Machine Learning",
            "ai": "Artificial Intelligence",
            "dl": "Deep Learning"

        }

        self.skill_stacks = {

            "mern": [
                "MongoDB",
                "Express.js",
                "React",
                "Node.js"
            ],

            "mean": [
                "MongoDB",
                "Express.js",
                "Angular",
                "Node.js"
            ],

            "lamp": [
                "Linux",
                "Apache",
                "MySQL",
                "PHP"
            ]

        }

        self.all_skills = []

        for skill_list in self.skills.values():

            self.all_skills.extend(skill_list)

    def extract(self, section_lines):

        text = "\n".join(section_lines)

        lower_text = text.lower()

        doc = self.nlp(text)

        extracted = {
            "technical": [],
            "business": [],
            "creative": []
        }

        # -----------------------------
        # Dictionary Matching
        # -----------------------------

        for category, skill_list in self.skills.items():

            for skill in skill_list:

                pattern = r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)'

                if re.search(pattern, lower_text):

                    extracted[category].append({

                        "skill": skill,

                        "confidence": 1.00,

                        "matched_by": "dictionary"

                    })

        # -----------------------------
        # Synonym Matching
        # -----------------------------

        for alias, original in self.synonyms.items():

            pattern = r'(?<!\w)' + re.escape(alias) + r'(?!\w)'

            if re.search(pattern, lower_text):

                for category, skill_list in self.skills.items():

                    if original in skill_list:

                        extracted[category].append({

                            "skill": original,

                            "confidence": 0.98,

                            "matched_by": "synonym"

                        })

        # -----------------------------
        # Skill Stack Detection
        # -----------------------------

        for stack, stack_skills in self.skill_stacks.items():

            pattern = r'(?<!\w)' + re.escape(stack) + r'(?!\w)'

            if re.search(pattern, lower_text):

                for skill in stack_skills:

                    for category, skill_list in self.skills.items():

                        if skill in skill_list:

                            extracted[category].append({

                                "skill": skill,

                                "confidence": 0.97,

                                "matched_by": "stack"

                            })

        
        normalized = self.__normalize(extracted)

        return self.__build_output(normalized)

    def __normalize(self, extracted):

        normalized = {}

        for category, skills in extracted.items():

            normalized[category] = {}

            for item in skills:

                skill = item["skill"]

                if skill not in normalized[category]:

                    normalized[category][skill] = item

                elif item["confidence"] > normalized[category][skill]["confidence"]:

                    normalized[category][skill] = item

        return normalized

    def __build_output(self, normalized):

        result = {}

        total = 0

        for category in self.skills.keys():

            values = list(normalized.get(category, {}).values())

            values.sort(

                key=lambda x: (

                    -x["confidence"],

                    x["skill"]

                )

            )

            result[category] = values

            total += len(values)

        result["summary"] = {

            "technical_count": len(result.get("technical", [])),

            "business_count": len(result.get("business", [])),

            "creative_count": len(result.get("creative", [])),

            "total_skills": total

        }

        return result