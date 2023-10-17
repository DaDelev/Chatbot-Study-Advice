# source: https://github.com/whitead/paper-qa


import os
os.environ['OPENAI_API_KEY'] = ''

from paperqa import Docs

docs = Docs(llm='gpt-3.5-turbo')

# using the master wifo module catalogue
docs.add('docs/MK_MSc_Wifo__2023.pdf', citation="module catalogue 2023", docname="MK_MSc_Wifo__2023.pdf")


answer = docs.query("What is the aim of the module Large Scale Data Management?")
print(answer.formatted_answer)
# ----------------------------------- ANSWER -----------------------------------
# 
# Question: What is the aim of the module Large Scale Data Management?
# The aim of the module Large Scale Data Management is for students to acquire knowledge about methods and systems for managing large datasets and data-intensive computing.
# They will learn to judge, select, and use traditional or non-traditional data management systems for different tasks, as well as solve computational problems involving large datasets.
# The module covers concepts, algorithms, and system issues related to parallel and distributed databases, big data platforms, and NoSQL, NewSQL, and polystore systems.
# The learning outcomes and qualification goals include developing expertise in these areas (MK_MSc_Wifo__2023.pdf pages 18-21, MK_MSc_Wifo__2023.pdf pages 16-18).

# References
# 1. (MK_MSc_Wifo__2023.pdf pages 18-21): module catalogue 2023
# 2. (MK_MSc_Wifo__2023.pdf pages 16-18): module catalogue 2023

answer = docs.query("How many ECTS points do i have to achieve in computer science fundamentals courses?")
print(answer.formatted_answer)
# ----------------------------------- ANSWER -----------------------------------
# Question: How many ECTS points do i have to achieve in computer science fundamentals courses?
# To achieve the required ECTS points in the Computer Science fundamentals courses, 
# you need to earn a total of 18 ECTS points (MK_MSc_Wifo__2023.pdf pages 3-6).

# References
# 1. (MK_MSc_Wifo__2023.pdf pages 3-6): module catalogue 2023