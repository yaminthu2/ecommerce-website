

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
        if (response.ok)
            return { "detail": "successful deleted" };
        else
            return {"detail": "error"}
    } 
    










