from flask import Flask, render_template, request,redirect, url_for, flash, jsonify,json
from models import db, Donor,AvailableBlood
from sqlalchemy import text
import schedule
import threading
import time
import requests
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donorsystem.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


cached_names = None

def get_cached_names():
    global cached_names
    if cached_names is None:
        donors = Donor.query.all()
        cached_names = [f"{donor.firstname} {donor.lastname}" for donor in donors]
    return cached_names

@app.route('/search', methods=['POST'])
def search():
    full_name_list = get_cached_names()
    return jsonify(full_name_list)

#-----------------------------------------------------------

@app.route('/getDonors')
def getDonors():
    """
    Get all donors.
    ---
    responses:
      200:
        description: Returns a list of all donors.
        schema:
          type: array
          items:
            properties:
              firstname:
                type: string
              lastname:
                type: string
              bloodtype:
                type: string
              city:
                type: string
              town:
                type: string
    """
    donors = Donor.query.all()
    donors_list = [{
        'firstname': donor.firstname,
        'lastname': donor.lastname,
        'bloodtype': donor.bloodtype,
        'city': donor.city,
        'town': donor.town,
    } for donor in donors]
    
    return jsonify(donors_list)


def donor_to_dict(donor):
    return {
        'id': donor.id,
        'firstname': donor.firstname,
        'lastname': donor.lastname,
        'bloodtype': donor.bloodtype,
        'city': donor.city,
        'town': donor.town
    
    }

@app.route('/getDonorByFullname/<fullname>', methods=['GET'])
def getDonorByFullname(fullname):
    donors = Donor.query.all()
    for donor in donors:
        full_name = f"{donor.firstname} {donor.lastname}"
        if full_name.lower() == fullname.lower(): 
            return jsonify(donor_to_dict(donor))
    return jsonify(None)

def getDonorByFullname2(fullname):
    donors = Donor.query.all()
    for donor in donors:
        full_name = f"{donor.firstname} {donor.lastname}"
        if full_name.lower() == fullname.lower(): 
            return donor
#--------------------------------------------------------

@app.route('/')
def homepage():
    return render_template('homePage.html')

@app.route('/addbloodpage', methods=['GET'])
def addbloodpage():
    return render_template('addBlood.html')

@app.route('/addBlood', methods=['POST'])
def addblood():
    data = request.get_json()
    donor_name = data.get('donorName')
    donor = getDonorByFullname2(donor_name)
    
    if donor:
        new_blood = AvailableBlood(
            bloodtype=donor.bloodtype,
            city=donor.city,
            town=donor.town,
            donor_id = donor.id
        )
        db.session.add(new_blood)
        db.session.commit()
        return jsonify({'message': '1 donation added to blood bank'})
    else:
        return jsonify({'error': 'Donor not found'})
        


@app.route('/createDonor', methods=['GET', 'POST'])
def createDonor():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        bloodtype = request.form['bloodtype']
        city = request.form['city']
        town = request.form['town']
        phoneNumber = request.form['phoneNumber']
        email=request.form['email']
        photoPath = request.files['photo'].filename if 'photo' in request.files else None

        if len(phoneNumber) != 10:
            return render_template('createDonor.html', error='Phone number should be 10 digits.')

        new_donor = Donor(
            firstname=firstname,
            lastname=lastname,
            bloodtype=bloodtype,
            city=city,
            town=town,
            phoneNumber=phoneNumber,
            email=email,
            photoPath=photoPath
        )

        db.session.add(new_donor)
        db.session.commit()

    return render_template('createDonor.html') 

# silinen donor'un bağışlarını da silmek için (mail atacak bir veri'ye ulaşılamayacağı için)
def findBloodsAndDelete(donor_id):
    blood_donations = AvailableBlood.query.filter_by(donor_id=donor_id).all()

    for blood_donation in blood_donations:
        db.session.delete(blood_donation)

    db.session.commit()
# Donor u sil
@app.route('/deleteDonor/<fullname>', methods=['DELETE'])
def deleteDonor(fullname):

    donor = getDonorByFullname2(fullname)
    
    if donor:
        findBloodsAndDelete(donor.id)
        db.session.delete(donor)
        db.session.commit()
        return ' deleted', 200
    else:
        return 'not found', 404


#get request from other service

def send_email(donor_id):
    donor = Donor.query.get(donor_id)
    if donor:
        email_address = donor.email
        # Burada gerçek e-posta gönderme işlemi yapılabilir
        print(f"E-posta gönderildi: {email_address}")
    else:
        print("Donor not found.")

def postMessage(request_id, blood_type, num_of_units, available_units):
    url = 'https://bloodrequestservice.azurewebsites.net/bloodfound'
    
    message = f"{num_of_units} found for {blood_type}"
    data = {
        "id": request_id,
        "message": message,
        "available_units": available_units
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    
    return response.status_code  # Durum kodunu döndürüyoruz



@app.route('/showRequests', methods=['GET', 'POST'])
def showRequests():
    response = requests.get('https://bloodrequestservice.azurewebsites.net/get_queue_data')

    if response.status_code == 200:
        api_data = response.json()
        return render_template('showRequests.html', Bloodrequests=api_data)
    else:
        return "Error fetching data"


# Zamanlanmış görevi tanımlama
@app.route('/get_requests', methods=['GET'])
def get_requests():
    response = requests.get('https://bloodrequestservice.azurewebsites.net/get_queue_data')

    if response.status_code == 200:
        api_data = response.json()

        for request_data in api_data:
            blood_type = request_data['blood_type']
            city = request_data['city']
            town = request_data['town']
            num_of_units = request_data['num_of_units']

            query = db.session.query(AvailableBlood).filter(
                AvailableBlood.bloodtype == blood_type,
                AvailableBlood.city == city,
                AvailableBlood.town == town
            )

            rows = query.limit(num_of_units).all()
            available_units = len(rows)

            if available_units <= num_of_units:
                status_code = postMessage(request_data['id'], request_data['blood_type'], request_data['num_of_units'], available_units)
                if status_code == 200:
                    for row in rows:
                        donor_id = row.donor_id
                        send_email(donor_id)  
                     return 'Requests processed'
                else:
                return 'Error fetching data from API'
   

# Zamanlanmış görevi 3 dakikada bir çalışacak şekilde planlama
schedule.every(3).minutes.do(get_requests)

# Zamanlanmış görevi yürütmek için arka planda çalışacak fonksiyon
def perform_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Arka planda zamanlanmış görevleri çalıştırma işlemini başlatma
def start_background_task():
    threading.Thread(target=perform_tasks).start()

if __name__ == '__main__':
    start_background_task()
    app.run(debug=True)