import pandas as pd
import re

df = pd.read_json('allcourse.json')


def extract_prereqs(text):

    match = re.search(r'Prereq:\s*(.*)', text, re.IGNORECASE)
    if not match:
        return []

    prereq_text = match.group(1).strip()

    return prereq_text


casglob = "Counts as a CAS Global & Cultural Diversity course"
casquan = " Counts as a CAS Quantitative Reasoning course"
sagedepsem = "Counts as a SAGES Departmental Seminar course"
sagesencap ="Counts as a SAGES Senior Capstone course"
#sageunisem
ugercapproj="Counts as a Capstone Project course"
ugercommin="Counts as a Communication Intensive course"
ugerdisccomm="Counts as a Disciplinary Communication course"
humdiv= "Counts as a Human Diversity & Commonality course"
ugerlocalglob="Counts as a Local & Global Engagement course"
ugermoralethical="Counts as a Moral & Ethical Reasoning course"
ugerquan="Counts as a Quantitative Reasoning course"
ugerglobalpers="Counts as a Understanding Global Perspectives course"
ugerwellmovfull="Counts as a Full-Semester Wellness/Movement course"
ugerwellmovehalf="Counts as a Half-Semester Wellness/Movement course"
ugerwellnofull="Counts as a Full-Semester Wellness/Non-movement course"
ugerwellnohalf="Counts as a Half-Semester Wellness/Non-movement course"

def add_info(df):
    #basic 
    df['subject'] = df['title'].str[:4]
    df['code'] = df['title'].str[:8]
    df['name'] = df['title'].apply(lambda x: x[11:-11])
    df['credits'] = df['title'].apply(lambda x: x[-8:-7])

    #counts as
    df['cas_global_and_cultural_diversity'] = df['desc'].apply(lambda x: casglob in x )
    df['cas_quanitative_reasoning'] = df['desc'].apply(lambda x: casquan in x )
    df['sages_departmental_seminar'] = df['desc'].apply(lambda x: sagedepsem in x )
    df['sages_senior_capstone'] = df['desc'].apply(lambda x: sagesencap in x )
    df['captsone_project'] = df['desc'].apply(lambda x: ugercapproj in x )
    df['communication_intensive'] = df['desc'].apply(lambda x: ugercommin in x )
    df['disciplinary_intensive'] = df['desc'].apply(lambda x: ugerdisccomm in x )
    df['human_diversity_and_commonality'] = df['desc'].apply(lambda x: humdiv in x )
    df['local_and_global_engagement'] = df['desc'].apply(lambda x: ugerlocalglob in x )
    df['moral_and_ethical_reasoning'] = df['desc'].apply(lambda x: ugermoralethical in x )
    df['quantitative_reasoning'] = df['desc'].apply(lambda x: ugerquan in x )
    df['understanding_global_perspectives'] = df['desc'].apply(lambda x: ugerglobalpers in x )
    df['full_semester_wellness_movement'] = df['desc'].apply(lambda x: ugerwellmovfull in x )
    df['half_semester_wellnessmovement'] = df['desc'].apply(lambda x: ugerwellmovehalf in x )
    df['full_semester_wellness_no_movement'] = df['desc'].apply(lambda x: ugerwellnofull in x )
    df['half_semester_wellness_no_movement'] = df['desc'].apply(lambda x: ugerwellnohalf in x )

    #prereqs
    df['prereq'] = df['desc'].apply(lambda x: extract_prereqs(x))

add_info(df)

df.to_csv('finalcourse.csv',index=False)
