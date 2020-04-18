import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./ServiceAccountKey.json")
deafult_app = firebase_admin.initialize_app(cred)


db = firestore.client()

"""
def getMedicine():
    response = {"age": "23", "gender": "F"}
    return response


response = getMedicine()
age = response["age"]
gender = response["gender"]

#doc_ref = db.collection(u"Medicines").document(u"R")
doc_ref.update(
    {u"age": age,}
)

print(gender + " and " + age + " successfully written to database")

users_ref = db.collection(u"Medicines")
docs = users_ref.stream()

for doc in docs:
    print(u"{} => {}".format(doc.id, doc.to_dict()))

"""


def get_coords(reports):
    co_list = []
    for report in reports:
        print(
            report.to_dict()["locationNew"][0], ", ", report.to_dict()["locationNew"][1]
        )


reports_ref = db.collection(u"Medicines")
reports = reports_ref.stream()
get_coords(reports)
