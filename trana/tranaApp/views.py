from django.shortcuts import render
import os
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "ServiceAccountKey.json")
)
deafult_app = firebase_admin.initialize_app(cred)


db = firestore.client()


def get_components():
    reports_ref = db.collection(u"Medicines")
    reports = reports_ref.stream()
    co_list = []
    reports_list = []
    for report in reports:
        co_list.append(
            [report.to_dict()["locationNew"][0], report.to_dict()["locationNew"][1]]
        )
        entry = {}
        for field in report.to_dict():
            if field != "locationNew":
                entry[field] = report.to_dict()[field]
        entry["id"] = len(reports_list)
        reports_list.append(entry)
    return co_list, reports_list


def reportsDashboard(request):
    co_list, reports_list = get_components()
    context = {
        "co_list": co_list,
        "reports": reports_list,
    }
    return render(request, "dashboard.html", context)
