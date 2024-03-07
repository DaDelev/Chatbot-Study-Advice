config = {
    "vectordb_dir" : "storage",
    "doc_directory" : "../data/scraped_data",
    
    "metadata" : {
        "metadata_prompt": """Extract relevant information from the following document.
The document is related to the University of Mannheim. Some documents are only relevant to a specific \
study program, while others provide general information about the University of several study \
programs at once (use the "general" tag). If you think the document is relevant to a specific study \
program which is not in the list use the "other" tag.

{input}
""",
        "metadata_schema" : {
            "properties": {
                "study_program": {
                    "type": "string",
                    "enum": [
                        "B.Sc. Business Informatics",
                        "M.Sc. Business Informatics",
                        "B.Sc. Mathematics in Business and Economics",
                        "M.Sc. Mathematics in Business and Economics",
                        "Mannheim Master in Data Science",
                        "general",
                        "other"
                    ],
                    "description": "The study program this document is relevant to"
                },
                "short_description": {
                    "type": "string",
                    "description": "A short summary that describes what information can be found in this document in at most 3 sentences"
                },
            },
            "required": ["study_program", "short_description"]
        }


    }



}