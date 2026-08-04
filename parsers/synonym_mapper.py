class SynonymMapper:

    def __init__(self):

        self.skill_map = {

            "py": "Python",
            "python3": "Python",

            "js": "JavaScript",
            "javascript": "JavaScript",

            "node": "Node.js",
            "nodejs": "Node.js",

            "reactjs": "React",
            "react.js": "React",

            "postgres": "PostgreSQL",

            "mysql": "MySQL",

            "aws cloud": "AWS",

            "gcp": "Google Cloud",

            "azure cloud": "Azure"
        }

        self.role_map = {

            "software developer": "Software Engineer",

            "backend developer": "Backend Engineer",

            "frontend developer": "Frontend Engineer",

            "web developer": "Software Engineer",

            "full stack developer": "Full Stack Engineer",

            "ml engineer": "Machine Learning Engineer",

            "ai engineer": "AI Engineer"
        }

    def normalize_skill(self, skill):

        return self.skill_map.get(skill.lower(), skill)

    def normalize_role(self, role):

        return self.role_map.get(role.lower(), role)