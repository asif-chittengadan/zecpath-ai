from parsers.section_builder import SectionBuilder


def test_section_builder_saves_and_loads_sections(tmp_path):
    sections = {
        "Skills": ["Python", "SQL"],
        "Education": ["B.Tech"],
    }
    output_path = tmp_path / "nested" / "sample.json"

    builder = SectionBuilder()
    builder.save(sections, output_path)

    assert output_path.exists()
    assert builder.load(output_path) == sections
