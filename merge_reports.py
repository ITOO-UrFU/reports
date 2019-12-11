import pandas as pd
import os
import datetime
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE_DIR, 'reports')

REPORTS = {}


def get_files():
    res_lst = []
    for r, d, f in os.walk(UPLOADS):
        for file in f:
            if '.csv' in file:
                res_lst.append(os.path.join(r, file))

    return res_lst


def parse_filename(filename):
    course = None
    f = filename.split()[-1].split(".")[0].split("_")
    date = datetime.datetime.strptime(f[-1], '%Y-%m-%d-%H%M')
    f = "_".join(f[:-1])

    for type in ("proctored", "student", "grade"):
        tmp = f.split(type)
        if len(tmp) != 1:
            course = tmp[0][:-1]
            rtype = f"{type}{tmp[1]}"
            return course, {"filename": filename, "type": rtype, "date": date.timestamp()}


files = get_files()
for f in files:
    course, report = parse_filename(f)

    if course in REPORTS.keys():
        REPORTS[course].append(report)
    else:
        REPORTS[course] = [report]


# motivate_grade = pd.DataFrame()
# motivate_proctored = pd.DataFrame()
# motivate_student_profile = pd.DataFrame()
def read_course_reports(course_reports):
    result = [None] * len(course_reports)
    for report in course_reports:
        df = pd.read_csv(report["filename"])
        if report["type"] == 'grade_report':
            result[1] = df[['Email', 'Grade']]
        elif report["type"] == 'proctored_exam_results_report':
            result[2] = df
        elif report["type"] == 'student_profile_info':
            result[0] = df[
                ['id', 'username', 'name', 'email', 'level_of_education', 'enrollment_mode', 'verification_status',
                 'cohort']]
    return result


def merge_reports(course_reports):
    df_list = read_course_reports(course_reports)
    merged_left_v1 = pd.merge(left=df_list[0], right=df_list[1], how='left', left_on='email', right_on='Email')
    del merged_left_v1['Email']
    merged_left_v2 = pd.merge(left=merged_left_v1, right=df_list[2], how='left', left_on='email', right_on='user_email')
    del merged_left_v2['user_email']
    merged_left_v2 = merged_left_v2.assign(course_id=course)
    # merged_left_v2.to_csv(f'result_{course}.csv')
    return merged_left_v2

result_df = pd.DataFrame()

for course, course_reports in REPORTS.items():
    result_df = result_df.append(merge_reports(course_reports))

profile_df = pd.read_csv('profile.csv')
del profile_df['User ID']
del profile_df['Username']
result_merge = pd.merge(left=result_df, right=profile_df, how='left', left_on='email', right_on='email')
print(result_merge.columns)
result_merge.to_csv('result.csv')

# print(REPORTS['UrFU_MOTIVATION_fall_2019'][0]['type']) proctored_exam_results_report   student_profile_info

# print(REPORTS)

# reports_df = pd.read_csv()

# print(f, date)

# def parse_data():
#     for each in form.cleaned_data['report_files']:
#                 parsed = str(each).split('.')[0].split("(")[0].strip().split("_")
#
#                 org = parsed[0]
#                 parsed.pop(0)
#                 date = datetime.datetime.strptime(parsed[-1], "%Y-%m-%d-%H%M").date()
#                 parsed.pop(-1)
#
#                 course_ids = Program.objects.order_by().values_list("course_id", flat=True).distinct()
#
#                 for id in course_ids:
#                     if id.lower() == str(each).split(f"{org}_")[1].split("_session")[0].lower():
#                         course_id = id
#
#                 sessions = Program.objects.order_by().values_list("session", flat=True).distinct()
#                 for s in sessions:
#                     if s in str(each):
#                         session = s
#
#                 try:
#                     for item in session.split("_") + course_id.split("_"):
#                         parsed.remove(item)
#                 except:
#                     pass
#
#                 report_type = "_".join(parsed)
#
#                 report = Report(report_file=each, title=str(each), date=date, course_id=course_id, session=session,
#                                 report_type=report_type)
#                 report.save()
#                 program = Program.objects.filter(session=session, course_id=course_id).first()
#                 program.reports.add(report)
#
#             return super(ReportUploadView, self).form_valid(form)
