from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Donor,AvailableBlood
from sqlalchemy import text

app = Flask(__name__)

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
            town=donor.town
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
            photoPath=photoPath
        )

        db.session.add(new_donor)
        db.session.commit()

    return render_template('createDonor.html') 



@app.route('/deleteDonor/<fullname>', methods=['DELETE'])
def deleteDonor(fullname):

    donor = getDonorByFullname2(fullname)
    if donor:
        db.session.delete(donor)
        db.session.commit()
        return ' deleted', 200
    else:
        return 'not found', 404


if __name__ == '__main__':
    app.run(debug=True)


