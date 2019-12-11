import pandas
import os
import datetime

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
    rtype = None
    f = filename.split()[-1].split(".")[0].split("_")
    date = datetime.datetime.strptime(f[-1], '%Y-%m-%d-%H%M')
    f = "_".join(f[:-1])

    for type in ("proctored", "student", "grade"):
        f = f.split(type)
        if len(f) == 1:
            f = f[0]
        else:
            course = f[0][:-1]
            rtype = f"{type}{f[1]}"
            break
    if course and rtype:
        return [course, {"filename": filename, "type": rtype, "date": date}]
    else:
        raise Exception


files = get_files()
for f in files:
    REPORTS.setdefault(parse_filename(f)[0], parse_filename(f)[1])

for course in REPORTS.keys():
    print(course)


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
