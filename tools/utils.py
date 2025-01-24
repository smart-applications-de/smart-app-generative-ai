# -*- coding: utf-8 -*-
"""match proposal.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CuNHIvrP7CXteGmlpxPTucyjL4XKpDsA
"""

# Commented out IPython magic to ensure Python compatibility.

# %pip install -q google-colab-selenium --quiet
#/content/cv.md

from crewai import Agent, Task, Crew, Process
from crewai import LLM
from pydantic import BaseModel, ValidationError
from crewai_tools import (YoutubeChannelSearchTool,WebsiteSearchTool,YoutubeVideoSearchTool,CodeInterpreterTool,FileWriterTool,
     ScrapeWebsiteTool,SeleniumScrapingTool,SerperDevTool, CSVSearchTool, DirectoryReadTool, FileReadTool, PDFSearchTool)

import os
from dotenv import  load_dotenv


def CrewAiMatcher(germin_api, serp_api, profession, year, date,cv_path,location,ispdf=False):
        os.environ["GOOGLE_API_KEY"] = germin_api
        os.environ['SERPER_API_KEY'] = serp_api
        os.environ['OPENAI_API_KEY']=germin_api
        GOOGLE_API_KEY =germin_api
        google_tool = SerperDevTool(
                n_results=4,
                api_key=serp_api,
                verbose=True
            )
        
        llm = LLM(
            model="gemini/gemini-1.5-pro-002",
            temperature=0.3,
            verbose=True,
            api_key=germin_api,
            )
        if ispdf:
            file = PDFSearchTool(cv_path)
        else:
            file = FileReadTool(cv_path)

        cv_reader= Agent(llm=llm,
                               role=' CV Reader',
                               goal ='Extract relevant information from the CV, such as skills, experience, and education.',

                               memory=True,
                               backstory=( """
                                 With years of experience in HR, you excel at quickly identifying key qualifications in resumes.
                               """),
                             allow_delegation=False,
                             verbose=True )
        output_csv_file = f'./Crew_AI/Reports/{profession}_reader.md'
        read_cv_task = Task(description=(f"""
            Extract relevant information from the given CV content. Focus on skills, experience,
            education, and key achievements.
            Ensure to capture the candidate's professional summary, technical skills,
            work history, and educational background.
              CV content: {cv_path}
        """),


                            expected_output="""

            A structured summary of the CV, including:
            - Professional Summary
            - Technical Skills
            - Work History
            - Education
            - Key Achievements
                  """,
                            async_execution=False,
                            agent=cv_reader,
                            output_file=output_csv_file
                            )

        output_csv_job = f'./Crew_AI/Reports/{profession}_posting.md'
        job_posting_research= Agent(llm=llm,
                               role='Best Job Posting Research',
                               goal ='Search the best Job postings online that matchs the cv.',
                               memory=True,
                               backstory=( """
                                A Job posting research expert with decades of experience on searching jobs online platforms like stepstones, indeed, Xing and LinkInd.
                               """),
                                tools=[google_tool,  FileWriterTool(), WebsiteSearchTool()],
                                allow_delegation=False,
                                verbose=True

                               )
        job_posting_task = Task(description=(f"""
           Conduct a thorough research on online job posting on given {profession}, and summary from the CV extracted from the previous task.
           When possible extract job titles, job skills, education, location,work experience,link to the job and company name.
           Ensure you provide a list of top 5 job opportunities based on {profession} and summary from the prevous task, nearest location to {location} and the lastest job posting based on current data: {date}
           You're given the following parameters:
              profession: {profession}
              current year: {year}
              current date: {date}
         Just use the Information from the Title, Link and Snippet!
        """),

                                expected_output="""

            for each job posting when possible extract A structured  summary  including:
            -  job title
            - Technical Skills
            - work experience
            -  job location
            - job description
            - website url
            - job posting platform ( for example Linden.com, Indeed.com, stepstone.de etc) 
            -  company name
            Formatted as markdown.
                  """,
                                async_execution=False,
                                agent=job_posting_research,
                                 context=[read_cv_task],
                                output_file=output_csv_job
                                )


        matcher=Agent(llm=llm,
                               role='Matcher Expert',
                               goal =' Match the CV to the job opportunities based on Job skills, Education,language,location and experience',
                               verbose=True,
                               memory=True,
                               backstory=( """
                                           A seasoned recruiter, you specialize in finding the perfect fit between candidates and job roles.
                               """),
                               allow_delegation=False,
                              tools=[google_tool,  FileWriterTool(), WebsiteSearchTool()])

        output_csv_match = f'./Crew_AI/Reports/{profession}_matcher.md'
        match_cv_task= Task(description=("""
                Match the CV to the job opportunities based on skills, experience, and key
                achievements.
                Evaluate how well the candidate's profile fits each job description,
                focusing on the alignment of skills, work history, and key achievements
                with the job requirements. Use the results from  previous tasks. Don't scrape the websites because you don't have access
            """),

                    expected_output="""
                A ranked list of job opportunities that best match the CV, including:
                - Job Title
                - Match Score (based on skills and experience)
                - Key Matching Points
                - Job Link,
                - Company name,
                - job posting platform ( for example Linden.com, Indeed.com, stepstone.de etc) 
                - website url
                - job location
                    """,
                    async_execution=False,
                        agent=matcher ,
                        context=[read_cv_task,job_posting_task ],
                    output_file=output_csv_match
                             )

        crew = Crew(
                    agents=[cv_reader, job_posting_research,matcher],
                    tasks=[read_cv_task, job_posting_task,match_cv_task],
                    process=Process.sequential,
                    memory=True,
                    cache=True,
                    verbose=True,
                    max_rpm=50 ,
                    share_crew=True
                )
        return crew.kickoff()
