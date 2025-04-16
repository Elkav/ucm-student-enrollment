const url = "http://127.0.0.1:5000";

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

    if(name === "" || pwd === ""){
        alert("Please enter a valid username and password");
        return;
    } else if(legalName === ""){
        alert("Please enter your legal name");
        return;
    }

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
        .then(() => {signIn()})
        .catch(err => console.error(err));
}

// redirect to user page based on role
function signIn() {
    let name = document.getElementById("username").value;
    let pwd = document.getElementById("password").value;
    if(name === "" || pwd === "") {
        alert("Invalid username or password");
        return;
    }

    const form = new URLSearchParams();
    form.append("username", name);
    form.append("password", pwd);

    fetch(`${url}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: form
    })
        .then(response => {
            if (!response.ok) throw new Error("Invalid username or password");
            return response.text();
        })
        .then(data => {
            document.getElementById("app").innerHTML = data;
            if (data.includes("STUDENT TEMPLATE")) {
                showMyCourses_student();
            } else if (data.includes("TEACHER TEMPLATE")) {
                showMyCourses_teacher();
            }
        })
        .catch(err => {
            alert(err.message);
        });
}

function signOut() {
    fetch(`${url}/logout`)
        .then(() => {
            showLogin();
        })
        .catch(err => console.error(err));
}

function showMyCourses_student() {
    fetch(`${url}/student`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("myCoursesTab").classList.add("active");
            document.getElementById("addCoursesTab").classList.remove("active");
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
    //First fetch courses the student is in (to know which "Add"s to grey out)
    fetch(`${url}/student`)  // get the list of enrolled courses
        .then(response => response.json())
        .then(myCourses => {
            let myCourseNames = myCourses.map(course => course['course_name']);
            //Then fetch all courses
            fetch(`${url}/courses`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById("addCoursesTab").classList.add("active");
                    document.getElementById("myCoursesTab").classList.remove("active");
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
                        let enrolled = myCourseNames.includes(course["course_name"]);
                        let full = course["num_students"] === course["max_students"];
                        row.innerHTML = `
                            <td>${course["course_name"]}</td>
                            <td>${course["teacher_name"]}</td>
                            <td>${course["time"]}</td>
                            <td>${course["num_students"]}/${course["max_students"]}</td>
                            <td><button ${enrolled || full ? `class="disabledBtn"` : `onclick='addCourse("${course["course_name"]}")'`}>
                            Add</button></td>`;
                        tableBody.appendChild(row);
                    });
                })
                .catch(err => console.error(err));
        })
}

function showMyCourses_teacher() {
    fetch(`${url}/teacher`)
        .then(response => response.json())
        .then(data => {
            const backButton = document.getElementById("back");
            backButton.style.display = "none";
            const tableHead = document.getElementById("courseTableHead");
            tableHead.innerHTML = `
                <tr>
                    <th>Course Name</th>
                    <th>Teacher</th>
                    <th>Time</th>
                    <th>Students Enrolled</th>
                </tr>`;
            const tableBody = document.getElementById("courseTableBody");
            tableBody.innerHTML = "";
            Object.entries(data).forEach((element) => {
                let course = element[1];
                let row = document.createElement("tr");
                row.innerHTML = `
                            <td><button onclick='showMyStudents_teacher("${course["course_name"]}")'>${course["course_name"]}</button></td>
                            <td>${course["teacher_name"]}</td>
                            <td>${course["time"]}</td>
                            <td>${course["num_students"]}/${course["max_students"]}</td>`
                tableBody.appendChild(row);
            });
        })
        .catch(err => console.error(err));
}

function showMyStudents_teacher(courseName){
	fetch(`${url}/teacher/${courseName}`)
        .then(response => response.json())
        .then(data => {
            const backButton = document.getElementById("back");
            backButton.style.display = 'block';
            const tableHead = document.getElementById("courseTableHead");
            tableHead.innerHTML = `
                <tr>
                    <th>Student Name</th>
                    <th>Grade</th>
                </tr>`;
            const tableBody = document.getElementById("courseTableBody");
            tableBody.innerHTML = "";
            Object.entries(data).forEach((element) => {
                let studentInfo = element[1]; //Contain an object with "student name: grade" but the student name is always different
                let studentName = Object.keys(studentInfo)[0];
                let studentGrade = studentInfo[studentName]
                let row = document.createElement("tr");
                row.innerHTML = `
                            <td>${studentName}</td>
                            <td id="${studentName}" contenteditable="true">${studentGrade}</td>`
                tableBody.appendChild(row);
                let gradeInput = document.getElementById(studentName);
                gradeInput.addEventListener("keypress", function(event) {
					if (event.key === "Enter"){
						event.preventDefault(); //Prevent the default behavior (aka adding a new line)
						let grade = Number(gradeInput.innerHTML);
						submitGrades(studentName, grade, courseName);
					}
				});
            });
        })
        .catch(err => console.error(err));
}

function submitGrades(studentName, studentGrade, courseName){
	console.log(`${studentName}'s grade is now ${studentGrade}`);

	fetch(`${url}/teacher/${courseName}/${studentName}/${studentGrade}`, {
			method: 'PUT',
		})
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(err => {
            console.error(err)
        });

    alert("Grade has been successfully updated!")

}

function addCourse(courseName){
	fetch(`${url}/student/${courseName}`, {
			method: 'POST',
		})
        .then(response => response.json())
        .then(data => console.log(data))
        .then(() => {showAllCourses_student()})
        .catch(err => {
            console.error(err)
        });
}

function dropCourse(courseName){
	fetch(`${url}/student/${courseName}`, {
			method: 'DELETE',
		})
        .then(response => response.json())
        .then(data => console.log(data))
        .then(() => {showMyCourses_student()})
        .catch(err => {
            console.error(err)
        });
}
