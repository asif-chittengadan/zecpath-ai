from parsers.section_builder import SectionBuilder

sections = {

    "Skills":[

        "Python",

        "SQL"

    ],

    "Education":[

        "B.Tech"

    ]

}

builder = SectionBuilder()

builder.save(

    sections,

    "data/labeled_resumes/sample.json"

)

print("Saved successfully.")