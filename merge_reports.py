import pandas as pd
import os
import datetime
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE_DIR, 'reports23')

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

    for type in ("proctored", "student", "grade", "sga"):
        tmp = f.split(type)
        # print(tmp)
        if len(tmp) != 1:
            course = tmp[0][:-1]
            rtype = f"{type}{tmp[1]}"
            # print(type, tmp)
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
            result[2] = df[['user_email', 'exam_name']]
        elif report["type"] == 'student_profile_info':
            result[0] = df[['username', 'name', 'email']]
        elif report["type"] == 'sga_report':
            result[3] = df[['Имя пользователя', 'Загружено', 'Оценка']]

    return result


def read_course_reports_full(course_reports):
    result = [None] * len(course_reports)
    for report in course_reports:
        df = pd.read_csv(report["filename"])
        if report["type"] == 'grade_report':
            result[1] = df[['Email', 'Grade']]
        elif report["type"] == 'proctored_exam_results_report':
            result[2] = df
        elif report["type"] == 'student_profile_info':
            result[0] = df
        elif report["type"] == 'sga_report':
            result[3] = df[['Имя пользователя', 'Загружено', 'Оценка']]

    return result


def merge_reports(course_reports):
    df_list = read_course_reports(course_reports)
    merged_left_v1 = pd.merge(left=df_list[0], right=df_list[1], how='left', left_on='email', right_on='Email')
    merged_left_v1.to_csv('merged_left_v1.csv')
    del merged_left_v1['Email']
    merged_left_v2 = pd.merge(left=merged_left_v1, right=df_list[2], how='left', left_on='email', right_on='user_email')
    merged_left_v2.to_csv('merged_left_v2.csv')
    del merged_left_v2['user_email']
    merged_left_v2 = pd.merge(left=merged_left_v2, right=df_list[3], how='left', left_on='username',
                              right_on='Имя пользователя')
    merged_left_v2 = merged_left_v2.assign(course_id=course)
    return merged_left_v2


def merge_reports_full(course_reports):
    df_list = read_course_reports_full(course_reports)
    merged_left_v1 = pd.merge(left=df_list[0], right=df_list[1], how='left', left_on='email', right_on='Email')
    merged_left_v1.to_csv('merged_left_v1.csv')
    del merged_left_v1['Email']
    merged_left_v2 = pd.merge(left=merged_left_v1, right=df_list[2], how='left', left_on='email', right_on='user_email')
    merged_left_v2.to_csv('merged_left_v2.csv')
    del merged_left_v2['user_email']
    merged_left_v2 = pd.merge(left=merged_left_v2, right=df_list[3], how='left', left_on='username',
                              right_on='Имя пользователя')
    merged_left_v2 = merged_left_v2.assign(course_id=course)
    return merged_left_v2


result_df = pd.DataFrame()
result_df_full = pd.DataFrame()

for course, course_reports in REPORTS.items():
    result_df = result_df.append(merge_reports(course_reports))
    result_df_full = result_df_full.append(merge_reports_full(course_reports))

profile_df = pd.read_csv('profile.csv')
# , 'phone', 'series', 'number', 'address_register',
profile_df_full = profile_df
profile_df = profile_df[
    ['email', 'last_name', 'first_name', 'second_name', 'City', 'Job', 'edu_organization']]
# print(result_df.columns)
# print(profile_df.head(10))

result_merge = pd.merge(left=result_df, right=profile_df, how='left', left_on='email', right_on='email')
result_merge_full = pd.merge(left=result_df_full, right=profile_df_full, how='left', left_on='email', right_on='email')

stagir_df = pd.read_csv("stagir.csv")
stagir_df = stagir_df[['time', 'name']]
stagir_df_result = stagir_df.drop_duplicates(subset=['name'])

result_merge = pd.merge(left=result_merge, right=stagir_df_result, how='left', left_on='name', right_on='name')
result_merge_full = pd.merge(left=result_merge_full, right=stagir_df_result, how='left', left_on='name',
                             right_on='name')

result_merge = result_merge.drop_duplicates()
result_merge_full = result_merge_full.drop_duplicates()

print(result_merge.columns)
del result_merge['Имя пользователя']

result_merge.columns = ['Имя пользователя', 'ФИО', 'Электронная почта', 'Оценка', 'Статус прохождения прокторинга',
                        'Наличие прикрепленной итоговой работы', 'Оценка прикрепленной итоговой работы', 'course_id',
                        'Фамилия', 'Имя', 'Отчество', 'Город',
                        'Место работы', 'ВУЗ', 'Стажировка: заполнена анкета']
# print(result_merge.head(20))
result_merge['Статус прохождения прокторинга'] = result_merge[['Статус прохождения прокторинга']].replace('', "Нет")
result_merge['Наличие прикрепленной итоговой работы'] = result_merge[['Наличие прикрепленной итоговой работы']].fillna(
    "Нет")
result_merge['Стажировка: заполнена анкета'] = result_merge[['Стажировка: заполнена анкета']].fillna("Нет")
# test = test.replace('None', "Нет")
result_merge['Статус прохождения прокторинга'] = result_merge['Статус прохождения прокторинга'].replace(
    'Аттестация по онлайн-модулю', "Да")
result_merge['Статус прохождения прокторинга'] = result_merge['Статус прохождения прокторинга'].replace(
    'Аттестация по онлайн-модулю (аудитория)', "Очный прокторинг")
result_merge['Статус прохождения прокторинга'] = result_merge['Статус прохождения прокторинга'].fillna('Нет')
result_merge = result_merge.assign(e='Да')
result_merge = result_merge.rename(columns={'e': 'Статус заполения анкеты'})
result_merge['Статус заполения анкеты'] = np.where(result_merge['Фамилия'].isnull(), 'Нет',
                                                   result_merge['Статус заполения анкеты'])
result_merge['Стажировка: заполнена анкета'] = np.where(result_merge[['Стажировка: заполнена анкета']] != "Нет", 'Да',
                                                        result_merge['Стажировка: заполнена анкета'])
#
# #
# #
result_merge.to_csv('result.csv')
result_merge_full.to_csv('result_full.csv')

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
