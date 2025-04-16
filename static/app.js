const url = "http://127.0.0.1:5000";
let username = "";

function showLogin() {
        fetch(`${url}/login`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("app").innerHTML = data;
        })
        .catch(err => console.error(err));
}

//load create.html template (for creating a new account)
function createAccount() {
    fetch(`${url}/create`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("app").innerHTML = data;
        })
        .catch(err => console.error(err));
}

// add new user account to database
function addUser() {
    let name = document.getElementById("username").value;
    let pwd = document.getElementById("password").value;
    let legalName = document.getElementById("legal_name").value;
    let role = document.getElementById("role").value;

    fetch(`${url}/create`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            "username": name,
            "password": pwd,
            "legal_name": legalName,
            "role": role,
        })
    })
        .then(response => response.json())
        .then(() => {signIn()}) // do some checks before signing in??
        .catch(err => console.error(err));
}

// redirect to user page based on role
function signIn() {
    let name = document.getElementById("username").value;
    let pwd = document.getElementById("password").value;
    fetch(`${url}/${name}/${pwd}`)
        .then(response => response.text())
        .then(data => {
            username = name;
            document.open();
            document.write(data); //again, NOT IDEAL
            document.close();
        })
        .catch(err => console.error(err));
}


function signOut() {
    showLogin();
    username = '';
}

function showMyCourses_student() {
    fetch(`${url}/student/${username}`)
        .then(response => response.json())
        .then(data => {
            const tableHead = document.getElementById("courseTableHead");
            tableHead.innerHTML = `
                <tr>
                    <th>Course Name</th>
                    <th>Teacher</th>
                    <th>Time</th>
                    <th>Students Enrolled</th>
                    <th>Grade</th>
                    <th>  </th>
                </tr>`;
            const tableBody = document.getElementById("courseTableBody");
            tableBody.innerHTML = "";
            Object.entries(data).forEach((element) => {
                let course = element[1];
                let row = document.createElement("tr");
                row.innerHTML = `
                    <td>${course["course_name"]}</td>
                    <td>${course["teacher_name"]}</td>
                    <td>${course["time"]}</td>
                    <td>${course["num_students"]}/${course["max_students"]}</td>
                    <td>${course["grade"]}%</td>
                    <td><button onclick='dropCourse("${course["course_name"]}")'>Drop</button></td>`
                tableBody.appendChild(row);
            });
        })
        .catch(err => console.error(err));
}

function showAllCourses_student() {
    fetch(`${url}/courses`)
        .then(response => response.json())
        .then(data => {
            const tableHead = document.getElementById("courseTableHead");
            tableHead.innerHTML = `
                <tr>
                    <th>Course Name</th>
                    <th>Teacher</th>
                    <th>Time</th>
                    <th>Students Enrolled</th>
                    <th> </th>
                </tr>`;

            const tableBody = document.getElementById("courseTableBody");
            tableBody.innerHTML = "";
            Object.entries(data).forEach((element) => {
                let course = element[1];
                let row = document.createElement("tr");
                row.innerHTML = `
                    <td>${course["course_name"]}</td>
                    <td>${course["teacher_name"]}</td>
                    <td>${course["time"]}</td>
                    <td>${course["num_students"]}/${course["max_students"]}</td>
                    <td><button onclick='addCourse("${course["course_name"]}")'>Add</button></td>`;
                tableBody.appendChild(row);
            });
        })
        .catch(err => console.error(err));
}

// let something = showMyCourses_teacher();

// document.getElementById("demo").innerHTML = something;

function showMyCourses_teacher() {
    var something = document.getElementById("demo");
    if(x.style.display === "none"){
        fetch(`${url}/teacher/${username}`)
        .then(response => response.json())
        .then(data => {
            console.log(username)
            console.table(data);
        })
        .catch(err => console.error(err));
    }
}

function addCourse(courseName){
	fetch(`${url}/student/${username}/${courseName}`, {
			method: 'POST',
		})
        .then(response => response.json())
        .then(data => console.log(data))
        .then(() => {showAllCourses_student()})
        .catch(err => {
            console.log(username)
            console.error(err)
        });
}

function dropCourse(courseName){
	fetch(`${url}/student/${username}/${courseName}`, {
			method: 'DELETE',
		})
        .then(response => response.json())
        .then(data => console.log(data))
        .then(() => {showMyCourses_student()})
        .catch(err => {
            console.log(username)
            console.error(err)
        });
}
