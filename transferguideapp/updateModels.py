from .models import Course
import requests
import json

"""
This is a very sketchy way of populating our database with courses using the SIS API
"""

def update():
    for i in range(1, 86):
        print(f"Fetching Page {i}...")
        try:
            url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1238"
            r = requests.get(url + "&page=" + str(i))
        except Exception:
            print("An Exception Occurred")
            continue
        else:
            for c in r.json():
                course = Course.create(str(c['subject']), str(c['catalog_nbr']), str(c['class_section']), str(c['descr']))
                course.save()
