const url = "http://127.0.0.1:5000";
let username = "";

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
        .then(() => {signIn();})
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
            username = enter_username;
        })
        .catch(err => console.error(err));
}

function showMyCourse_student() {
    fetch(`${url}/student/${username}`)
        .then(response => response.json())
        .then(data => {
            const head = document.getElementById('tableDisplay');
            const table_body = document.getElementById('tableBody');
            const head_content = `<tr>
                    <td>Course Name</td>
                    <td>Time</td>
                    <td>Students Enrolled</td>
                </tr>`;
            head.innerHTML = head_content;
            table_body.innerHTML = '';
            for (const [course, [time, students]] of Object.entries(data)) {
                const row = `<tr>
                    <td>${course}</td>
                    <td>${time}</td>
                    <td>${students}</td>
                </tr>`;
                table_body.innerHTML += row;
            }
        })
        .catch(err => {
            console.log(username)
            console.error(err)
        });
}

function showAllCourse_student() {
    fetch(`${url}/courses/${username}`)
        .then(response => response.json())
        .then(data => {
            const head = document.getElementById('tableDisplay');
            const table_body = document.getElementById('tableBody');
            const head_content = `<tr>
                    <td>Course Name</td>
                    <td>Time</td>
                    <td>Students Enrolled</td>
                    <td>Register</td>
                </tr>`;
            head.innerHTML = head_content;
            table_body.innerHTML = ''
            for (const [course, [time, students_enrolled, registered]] of Object.entries(data)) {
                let row = '';
                if (registered === 'YES') {
                    row = `<tr>
                        <td>${course}</td>
                        <td>${time}</td>
                        <td>${students_enrolled}</td>
                        <td><button onclick="dropCourse('${course}')">Drop</button></td>
                    </tr>`;
                } else {
                    row = `<tr>
                        <td>${course}</td>
                        <td>${time}</td>
                        <td>${students_enrolled}</td>
                        <td><button onclick="registerCourse('${course}')">Add</button></td>
                    </tr>`;
                }

                table_body.innerHTML += row;
            }
        })
        .catch(err => console.error(err));
}

function dropCourse(course) {
    fetch(`${url}/student/${username}/${course}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json',},
    })
        .then(response => response.json())
        .then(_ => showAllCourse_student())
        .catch(err => console.error(err));
}

function registerCourse(course) {
    fetch(`${url}/student/${username}/${course}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
    })
        .then(response => response.json())
        .then(_ => showAllCourse_student())
        .catch(err => console.error(err));
}

function showMyCourse_teacher() {
    fetch(`${url}/teacher/${username}`)
        .then(response => response.json())
        .then(data => {
            const head = document.getElementById('tableDisplay');
            const table_body = document.getElementById('tableBody');
            const head_content = `<tr>
                    <td>Course Name</td>
                    <td>Time</td>
                    <td>Students Enrolled</td>
                </tr>`;
            head.innerHTML = head_content;
            table_body.innerHTML = ''
            for (const [course, [time, students]] of Object.entries(data)) {
                const row = `<tr>
                    <td><button onclick="classInfo('${course}')">${course}</button></td>
                    <td>${time}</td>
                    <td>${students}</td>
                </tr>`;
                table_body.innerHTML += row;
            }
        })
        .catch(err => console.error(err));
}

function classInfo(course) {
        fetch(`${url}/teacher/${username}/${course}`)
        .then(response => response.json())
        .then(data => {
            const head = document.getElementById('tableDisplay');
            const table_body = document.getElementById('tableBody');
            const head_content = `<tr>
                    <td>Student Name</td>
                    <td>Students Grade</td>
                </tr>`;
            head.innerHTML = head_content;
            table_body.innerHTML = ''
            for (const [student_name, student_grade] of Object.entries(data)) {
                const row = `<tr>
                    <td>${student_name}</td>
                    <td><input type="text" value="${student_grade}" 
                    onchange="updateGrade(this,'${course}', '${student_name}')"></td>
                </tr>`;
                table_body.innerHTML += row;
            }
        })
        .catch(err => console.error(err));
}

function updateGrade(input, course, student_name) {
    const grade = input.value
    fetch(`${url}/teacher/${username}/${course}/${student_name}/${grade}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
    })
        .then(response => response.json())
        .then(_ => classInfo(course))
        .catch(err => console.error(err));
}

function signOut() {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.open();
            document.write(data);
            document.close();
            username = "";
        })
        .catch(err => console.error(err));
}
