function showDonors() {
    fetch('/getDonors')
        .then(response => response.json())
        .then(data => {
            const donorsList = document.getElementById('donors-list');
            data.forEach(donor => {
                const li = document.createElement('li');
                li.textContent = `${donor.firstname} ${donor.lastname} - Blood Type: ${donor.bloodtype}, City: ${donor.city}, Town: ${donor.town}`;
                
               
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Delete';
                deleteBtn.classList.add('delete-button'); // CSS sınıfını butona ekle
                deleteBtn.addEventListener('click', function() {
                    deleteDonor(`${donor.firstname} ${donor.lastname}`);
                });

                li.appendChild(deleteBtn);
                donorsList.appendChild(li);
            });
        });
}

document.addEventListener('DOMContentLoaded', showDonors)

function deleteDonor(fullname) {
    fetch(`/deleteDonor/${fullname}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Başarılı yanıt durumunda yapılacak işlemler
            console.log('deleted');
            // Gerekirse sayfayı yenileyebilir ya da listeden bağışçıyı kaldırabilirsiniz.
        } else {
            // Hata durumunda yapılacak işlemler
            console.error('error');
        }
    })
    .catch(error => {
        console.error('İstek gönderilirken bir hata oluştu:', error);
    });
}



function populateCities() {
    const citySelect = document.getElementById('city');
    fetch('https://turkiyeapi.cyclic.app/api/v1/provinces?fields=name,areaCode')
        .then(response => response.json())
        .then(data => {
            data.data.forEach(city => {
                const option = document.createElement('option');
                option.value = city.name;
                option.textContent = city.name;
                citySelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching cities:', error));
}

document.addEventListener('DOMContentLoaded', populateCities)

function getTowns() {
    const citySelect = document.getElementById('city');
    const selectedCity = citySelect.value;
    const townSelect = document.getElementById('town');
    townSelect.innerHTML = '<option value="">Select a town</option>';

    if (selectedCity !== '') {
        fetch(`https://turkiyeapi.cyclic.app/api/v1/provinces?name=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                const districts = data.data[0].districts;
                districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district.name;
                    option.textContent = district.name;
                    townSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching towns:', error));
    }
}


