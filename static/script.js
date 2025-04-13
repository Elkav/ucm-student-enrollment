const url = "http://127.0.0.1:5000";
let user_name = "";

function create_account() {
    fetch(`${url}/create`)
        .then(response => response.text())
        .then(data => {
            document.open();
            document.write(data);
            document.close();
        })
        .catch(err => console.error(err));
}

function create() {
    let create_username = document.getElementById("username").value;
    let create_password = document.getElementById("password").value;
    // let create_legal_name = document.getElementById("legal_name").value;
    let statue = document.getElementById("role").value;

    fetch(`${url}/create`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            "username": create_username,
            "password": create_password,
            "legal_name": create_legal_name,
            "statue": statue,
        })
    })
        .then(response => response.json())
        .then(() => {})
        .catch(() => {});
}

function signIn(event) {
    event.preventDefault();
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");
    
    // Basic validation
    if (!username || !password) {
        errorMessage.textContent = "Please fill in all fields";
        return false;
    }
    
    // Clear any previous error messages
    errorMessage.textContent = "";
    
    fetch(`${url}/${username}/${password}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Login failed');
            }
            return response.text();
        })
        .then(data => {
            document.open();
            document.write(data);
            document.close();
            user_name = username;
        })
        .catch(error => {
            errorMessage.textContent = "Invalid username or password";
            console.error('Error:', error);
        });
    
    return false;
}

function showMyCourse_student() {
    
}

function showAllCourse_student() {

}

function showMyCourse_teacher() {

}

function signOut() {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.open();
            document.write(data);
            document.close();
            user_name = "";
        })
        .catch(err => console.error(err));
}