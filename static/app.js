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
    let create_legal_name = document.getElementById("legal_name").value;
    let role = document.getElementById("role").value;

    fetch(`${url}/create`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            "username": create_username,
            "password": create_password,
            "legal_name": create_legal_name,
            "role": role,
        })
    })
        .then(response => response.json())
        .then(() => {})
        .catch(() => {});
}

function signIn() {
    let enter_username = document.getElementById("username").value;
    let enter_password = document.getElementById("password").value;
    fetch(`${url}/${enter_username}/${enter_password}`)
        .then(response => response.text())
        .then(data => {
            document.open();
            document.write(data);
            document.close();
            user_name = enter_username;
        })
        .catch(err => console.error(err));
}

function showMyCourse_student() {
    fetch(`${url}/student/${user_name}`)
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(err => {
            console.log(user_name)
            console.error(err)
        });
}

function showAllCourse_student() {
    fetch(`${url}/courses`)
        .then(response => response.json())
        .then(data => {
            console.table(data);
        })
        .catch(err => console.error(err));
}

function showMyCourse_teacher() {
    fetch(`${url}/teacher/${user_name}`)
        .then(response => response.json())
        .then(data => {
            console.log(user_name)
            console.table(data);
        })
        .catch(err => console.error(err));
}

function signOut() {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.open();
            document.write(data);
            document.close();
            user_name = "";
            user_role = "";
        })
        .catch(err => console.error(err));
}
