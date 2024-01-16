document.addEventListener('DOMContentLoaded', function() {
    const donorNameInput = document.getElementById('donorName');

    donorNameInput.addEventListener('input', function(event) {
        let input = event.target.value.trim(); // Girilen değeri al, boşlukları kaldır

        fetch('/search', {
            method: 'POST',
            body: JSON.stringify({ input }), // Sunucuya girilen değeri gönder
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        
        .then(data => {
            const datalist = document.getElementById('donorList');
            datalist.innerHTML = ''; 

            if (Array.isArray(data)) {
                data.forEach(name => {
                    let option = document.createElement('option');
                    option.value = name;
                    datalist.appendChild(option);
                });
            } else {
                console.error('Invalid data format received from the server');
            }
        })
        .catch(error => console.error('Error:', error));        
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const donorNameInput = document.getElementById('donorName');
    const bloodTypeInput = document.getElementById('bloodType');

    donorNameInput.addEventListener('input', function(event) {
        const selectedName = event.target.value.trim();

        fetch(`/getDonorByFullname/${selectedName}`, {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data !== null) { // Check if valid donor data is received
                bloodTypeInput.value = data.bloodtype;
            } else {
                // Clear the blood type input if no matching donor found
                bloodTypeInput.value = '';
            }
        })
        .catch(error => console.error('Error:', error));
    });
});



document.addEventListener('DOMContentLoaded', function() {
    const currentDateInput = document.getElementById('currentDate');

   
    const today = new Date();
    const year = today.getFullYear();
    let month = today.getMonth() + 1;
    let day = today.getDate();

    
    if (month < 10) {
        month = `0${month}`;
    }
    if (day < 10) {
        day = `0${day}`;
    }

    const currentDate = `${year}-${month}-${day}`;
    currentDateInput.value = currentDate;
});
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('submitButton').addEventListener('click', function(event) {
        var donorName = document.getElementById('donorName').value;
        
        fetch('/addBlood', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ donorName: donorName })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            var infoDiv = document.querySelector('.info');
            var para = document.createElement("p");

            if ('error' in data && data.error === 'Donor not found') {
                var errorPara = document.createElement("p");
                var errorTextNode = document.createTextNode(data.error);
                errorPara.appendChild(errorTextNode);
                infoDiv.appendChild(errorPara);

                setTimeout(function() {
                    infoDiv.removeChild(errorPara);
                    document.getElementById('myForm').reset();
                }, 2000); // 2 seconds delay
            } else if ('message' in data) {
                var textNode = document.createTextNode(data.message);
                para.appendChild(textNode);
                infoDiv.appendChild(para);

                setTimeout(function() {
                    infoDiv.removeChild(para);
                    document.getElementById('myForm').reset();
                }, 2000); // 2 seconds delay
            }
        })
        .catch(error => console.error('Error:', error));
    });
});


function homepageback() {
   
    window.location.href = '/';
}

