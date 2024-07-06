

async function postMethod(route,data,token) {
        try {
        const response = await fetch(route, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        const data_1 = await response.json();
        return data_1;
    } catch (error) {
        console.error('Error:', error);
    }
    }


async function putMethod(route,data,token) {
    
        const response = await fetch(route, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        const data_1 = await response.json();
        return data_1;
    } 
    


async function deleteMethod(route,token) {
   
        const response = await fetch(route, {
            method: "DELETE",
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        return { "detail": "successful deleted" };
    } 
    










// document.addEventListener('DOMContentLoaded', function() {
//     document.querySelectorAll('.menu-item').forEach(function(item) {
//         item.addEventListener('click', function(event) {
//             document.querySelectorAll('.dropdown').forEach(function(dropdown) {
//                 dropdown.style.display = 'none';
//             });
//             item.querySelector('.dropdown').style.display = 'flex';
//             event.stopPropagation();
//         });
//     });

//     document.addEventListener('click', function() {
//         document.querySelectorAll('.dropdown').forEach(function(dropdown) {
//             dropdown.style.display = 'none';
//         });
//     });
// });



// // When the user scrolls down 20px from the top of the document, slide down the navbar
// window.onscroll = function() {scrollFunction()};

